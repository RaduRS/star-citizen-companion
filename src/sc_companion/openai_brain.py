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
    "\n\nYou CAN press Star Citizen's keyboard keys via the propose_sc_action "
    "function. Use it CONSERVATIVELY. A wrong press is much worse than a "
    "description of what to press — the user can always press a key "
    "themselves, but a wrong press might fire weapons, jettison cargo, or "
    "self-destruct.\n"
    "\n"
    "RULE: Before calling propose_sc_action, find an entry in the KEYBOARD "
    "BINDINGS table whose action ID or humanized name is an EXACT or "
    "near-exact phrasing match for what the user asked. If there is no "
    "exact match, do NOT call the function. Speak a description instead.\n"
    "\n"
    "Examples of WRONG semantic matching (do NOT do this):\n"
    "- User: 'turn on engines' → there is no action named 'engines on'. Do "
    "NOT map this to throttle_up just because it involves the engine. "
    "Decline: 'Turning on engines isn't a single keyboard action — flight "
    "ready toggles the whole power state. Want me to try flight ready?'\n"
    "- User: 'request undock' → there's no `v_atc_request` entry. ATC was "
    "added after the source dump. Decline: 'ATC isn't in my keyboard "
    "reference — use your stick or the in-game comms menu.'\n"
    "- User: 'fire missiles' if the table only has `v_weapon_launch_missile` "
    "with no keyboard rebind → decline rather than press space/m/whatever.\n"
    "\n"
    "Examples of correct calls (action ID matches user's words clearly):\n"
    "- 'open mobiglas' → mobiglas entry → press `f1`\n"
    "- 'cycle camera view' → v_view_cycle_fwd → press `f4`\n"
    "- 'turn lights on' → v_lights → press `3`\n"
    "\n"
    "Source-of-truth rule for which keys to press:\n"
    "1. The STAR CITIZEN KEYBOARD BINDINGS section above is the COMPLETE "
    "list of valid keys you may pass to propose_sc_action. It was machine-"
    "generated from SC's default action map. If an action is NOT in that "
    "table, IT HAS NO VANILLA KEYBOARD BINDING. Do not invent one. Do not "
    "fall back on 'common sense' or what you remember about SC defaults — "
    "your memory of SC keys is unreliable across patches.\n"
    "2. When the action is missing from the table:\n"
    "   - If the screenshot shows a contextual hint like 'Press <key> to "
    "<action>', use that key literally and call propose_sc_action with it.\n"
    "   - Otherwise, DECLINE: say something like 'That action isn't bound "
    "to a vanilla keyboard key — you'd need to use your stick or rebind "
    "it in Options → Keybindings.' Do NOT call propose_sc_action.\n"
    "3. Categories marked ⚠ in the bindings (master mode toggle, "
    "flight-ready, power triangle, MFD cycling, weapon-group selectors) "
    "are patch-volatile. If the action is in one of those AND the "
    "screenshot doesn't confirm the listed key, decline rather than press.\n"
    "4. Never use VKB button names (A4 HAT, button 22, etc.) in the keys "
    "array. The keys array is for KEYBOARD keys only. VKB info is for "
    "describing the physical controller in your spoken reply.\n"
    "5. Pass the key from the table EXACTLY as shown (e.g., `alt+l`, "
    "`right shift+backspace`, `f1`). Don't reformat or rename keys.\n"
    "\n"
    "Do NOT call propose_sc_action for:\n"
    "- Pure information questions ('what does this MFD do', 'where is X')\n"
    "- Status checks ('what do you see')\n"
    "- Actions whose ID/name doesn't appear in the bindings table"
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
            action_name = str(args.get("action_name", "the action"))[:80]
            note = (
                f"That looks like a joystick binding, not a keyboard key — "
                f"you'd press {' / '.join(key_strs)} on the stick to "
                f"{action_name.lower()}."
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
