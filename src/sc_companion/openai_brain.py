import base64
import datetime
import json
from typing import Any

from openai import AsyncOpenAI

from .brain import Brain, BrainReply, ConversationHistory, ProposedAction
from .minimax_brain import BASE_SYSTEM_PROMPT, VKB_PREAMBLE
from .sc_actions import is_safe_key

KEYBOARD_DEFAULTS_PREAMBLE = (
    "\n\n--- STAR CITIZEN KEYBOARD BINDINGS (used for execution — ALWAYS use"
    " these, never VKB button names) ---\n"
)

ACTIONS_SYSTEM_SUFFIX = (
    "\n\nWHEN THE USER ASKS YOU TO DO SOMETHING, YOU PRESS THE KEY. You do "
    "not describe what they should press. You do not mention the joystick. "
    "You ARE the hands. Call propose_sc_action and announce in present "
    "tense ('Toggling power', 'Opening MobiGlas', 'Cycling camera').\n"
    "\n"
    "Decision flow:\n"
    "1. Look at the KEYBOARD BINDINGS table above. Find the action whose "
    "ID or humanized name is the closest match for what the user asked.\n"
    "2. If you find a reasonable match in the table → CALL "
    "propose_sc_action with the key from that entry. Press it. The user "
    "asked you to act — act.\n"
    "3. If no reasonable match exists in the table → SAY 'I can't press "
    "that — it doesn't have a keyboard binding I know of.' DO NOT mention "
    "the joystick, VKB, stick buttons, or which controller button to use. "
    "DO NOT tell them to press anything on their stick. Just decline.\n"
    "\n"
    "What counts as a 'reasonable match':\n"
    "- EXACT: user says 'open mobiglas' and the table has `mobiglas` → "
    "press it.\n"
    "- CLOSE on intent: user says 'turn off engines' and the table has "
    "`v_power_toggle = 5` → press 5. Power-toggle covers engine power, "
    "that's a real match.\n"
    "- CLOSE on synonyms: 'turn lights on' → `v_lights = 3` → press 3.\n"
    "- NOT a match: 'turn on engines' mapped to `v_throttle_up = w` is "
    "WRONG. Throttle up is just forward thrust, not engine power. If the "
    "only candidate is a weak/tangential fit, decline.\n"
    "\n"
    "Hard rules:\n"
    "a) Never put VKB / joystick names (button N, hat, stick, R-Ctrl + "
    "buttonX, etc.) in the keys array. Keys array is KEYBOARD ONLY.\n"
    "b) Never mention the VKB joystick layout in your spoken reply when "
    "declining. The VKB section in your context is for visual questions "
    "('how does the stick layout look') only — it is NOT a fallback "
    "answer when keyboard execution isn't possible.\n"
    "c) Categories marked ⚠ are patch-volatile. Still press if confident, "
    "but if the user's intent is ambiguous, prefer a one-sentence "
    "decline over a wrong press.\n"
    "d) Pass the key from the table EXACTLY as shown (e.g. `alt+l`, "
    "`right shift+backspace`, `f1`).\n"
    "\n"
    "Do NOT call propose_sc_action for:\n"
    "- Pure information questions ('what does this MFD do', 'where am I')\n"
    "- Status checks ('what do you see on screen')"
)

PROPOSE_ACTION_TOOL = {
    "type": "function",
    "name": "propose_sc_action",
    "description": (
        "Propose a keyboard action to perform in Star Citizen. The app "
        "stores this as pending until the user confirms verbally."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action_name": {
                "type": "string",
                "description": "Short human-readable action name, max 6 words.",
            },
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Sequence of key combos to press in order. Use the "
                    "Python keyboard library syntax: single key like 'm', "
                    "combos with '+' like 'shift+1'. Use Star Citizen "
                    "default keyboard bindings."
                ),
            },
            "explanation": {
                "type": "string",
                "description": "One short sentence describing what these keys do in Star Citizen.",
            },
        },
        "required": ["action_name", "keys", "explanation"],
        "additionalProperties": False,
    },
    "strict": True,
}


# Patterns that mean the model leaked a joystick reference into the keys array
# rather than a keyboard key. is_safe_key would also reject these at execute
# time, but by then the TTS has already announced "Pressing <stick combo>" —
# catching them here lets us swap to a descriptive reply.
_JOYSTICK_LEAK_TOKENS = (
    "button", "stick", "hat", "trigger", "pinky", "vkb",
)


def _looks_like_joystick(key: str) -> bool:
    k = key.lower()
    return any(tok in k for tok in _JOYSTICK_LEAK_TOKENS)


def _extract_text_and_action(response: Any) -> tuple[str, ProposedAction | None]:
    """Pull the text reply and (optional) function-call payload out of a
    Responses API response object. Reject the action (no keypress) if the
    model proposed joystick names or unsafe keys — instead, return a
    descriptive reply so the user hears what to press rather than a wrong
    press."""
    text = response.output_text or ""
    action: ProposedAction | None = None
    output = getattr(response, "output", None) or []
    for item in output:
        item_type = getattr(item, "type", None)
        if item_type != "function_call":
            continue
        if getattr(item, "name", None) != "propose_sc_action":
            continue
        raw = getattr(item, "arguments", None)
        if not raw:
            continue
        try:
            args = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            continue
        keys = args.get("keys") or []
        if not keys:
            continue
        key_strs = [str(k) for k in keys]

        # Reject if any proposed key is actually a joystick reference or
        # otherwise fails the safety check. The brain's spoken reply might
        # have already said "Pressing X" — overwrite it so the user gets
        # consistent description instead of a fake press.
        bad = [k for k in key_strs if _looks_like_joystick(k) or not is_safe_key(k)]
        if bad:
            # Joystick leak or unsafe key. Don't press, don't mention the
            # stick — the user explicitly asked the companion to be the
            # hands; if we can't press it, we just say so.
            action_name = str(args.get("action_name", "that"))[:80]
            note = (
                f"I can't press that — {action_name.lower()} doesn't have a "
                f"keyboard binding I can use."
            )
            return note, None

        action = ProposedAction(
            name=str(args.get("action_name", "SC action"))[:80],
            keys=tuple(key_strs),
            explanation=str(args.get("explanation", "")),
        )
        break
    if action and not text.strip():
        keys_phrase = " then ".join(action.keys)
        text = f"Pressing {keys_phrase} to {action.name.lower()}."
    return text, action


class OpenAIBrain(Brain):
    """Vision + (optional) web-search + (optional) SC-action-proposal brain
    backed by OpenAI's Responses API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5-nano",
        history_turns: int = 6,
        timeout: float = 60.0,
        vkb_bindings: str | None = None,
        keyboard_defaults: str | None = None,
        web_search: bool = False,
        actions_enabled: bool = True,
        reasoning_effort: str = "minimal",
    ):
        self._model = model
        self._history = ConversationHistory(max_turns=history_turns)
        self._client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self._web_search = web_search
        self._actions_enabled = actions_enabled
        self._reasoning_effort = reasoning_effort
        prompt = BASE_SYSTEM_PROMPT
        if vkb_bindings:
            prompt += VKB_PREAMBLE + vkb_bindings
        if actions_enabled and keyboard_defaults:
            prompt += KEYBOARD_DEFAULTS_PREAMBLE + keyboard_defaults
        if actions_enabled:
            prompt += ACTIONS_SYSTEM_SUFFIX
        self._system_prompt = prompt

    async def answer(self, frame: bytes, query: str) -> BrainReply:
        img_b64 = base64.b64encode(frame).decode()
        mime = "image/jpeg" if frame[:3] == b"\xff\xd8\xff" else "image/png"
        now = datetime.datetime.now().strftime("%A, %Y-%m-%d %H:%M %Z").strip()
        system = f"{self._system_prompt}\n\nToday is {now}."

        messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
        for turn in self._history.as_messages():
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": query},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,{img_b64}",
                    },
                ],
            }
        )

        kwargs: dict[str, Any] = {"model": self._model, "input": messages}
        if self._reasoning_effort:
            kwargs["reasoning"] = {"effort": self._reasoning_effort}
        tools: list[dict[str, Any]] = []
        if self._web_search:
            tools.append({"type": "web_search_preview"})
        if self._actions_enabled:
            tools.append(PROPOSE_ACTION_TOOL)
        if tools:
            kwargs["tools"] = tools

        response = await self._client.responses.create(**kwargs)
        text, action = _extract_text_and_action(response)
        self._history.append_user(query)
        self._history.append_assistant(text)
        return BrainReply(text=text, pending_action=action)

    async def aclose(self) -> None:
        try:
            await self._client.close()
        except Exception:
            pass
