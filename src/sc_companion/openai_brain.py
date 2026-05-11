import base64
import datetime
import json
from typing import Any

from openai import AsyncOpenAI

from .brain import Brain, BrainReply, ConversationHistory, ProposedAction
from .minimax_brain import BASE_SYSTEM_PROMPT, VKB_PREAMBLE

KEYBOARD_DEFAULTS_PREAMBLE = (
    "\n\n--- STAR CITIZEN KEYBOARD BINDINGS (used for execution — ALWAYS use"
    " these, never VKB button names) ---\n"
)

ACTIONS_SYSTEM_SUFFIX = (
    "\n\nYOU CAN PRESS STAR CITIZEN'S KEYBOARD KEYS for the user via the "
    "propose_sc_action function. When you call this function the keys are "
    "pressed IMMEDIATELY — there is NO confirmation step. Do NOT ask the "
    "user to say 'go' or 'confirm'. Just call the function and announce "
    "what you're doing in present tense ('Opening MobiGlas', 'Engaging "
    "quantum drive', 'Toggling lights').\n"
    "\n"
    "ALWAYS call propose_sc_action when the user asks for any in-game "
    "action:\n"
    "- 'open mobiglas' / 'open map' / 'open inventory'\n"
    "- 'engage quantum' / 'spool quantum' / 'lock quantum target'\n"
    "- 'request landing' / 'self destruct' / 'eject'\n"
    "- 'lights on' / 'gear down' / 'toggle gimbal'\n"
    "- 'press F' / 'do it for me'\n"
    "- 'can you open the X' / 'can you do that' (treat as a request)\n"
    "\n"
    "Source-of-truth rule for which keys to press:\n"
    "1. The STAR CITIZEN KEYBOARD BINDINGS section above (when present) is "
    "parsed from the user's actual actionmap. Use it as the truth.\n"
    "2. If a binding is shown only as a VKB button name (e.g., A4 HAT) "
    "in the bindings, that's the controller — DO NOT pass it to the "
    "function. Decline politely instead.\n"
    "3. Never use VKB button names in the function call. VKB info is only "
    "for describing the physical controller in your spoken reply.\n"
    "4. If you don't see the action in the bindings table and don't know "
    "Star Citizen's keyboard default with high confidence, decline "
    "politely instead of guessing.\n"
    "\n"
    "Do NOT call propose_sc_action for:\n"
    "- Pure information questions ('what does this MFD do', 'where is X')\n"
    "- Status checks ('what do you see')"
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


def _extract_text_and_action(response: Any) -> tuple[str, ProposedAction | None]:
    """Pull the text reply and (optional) function-call payload out of a
    Responses API response object. If the model returns only a function call
    without spoken text, synthesize fallback text so the user hears something."""
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
        action = ProposedAction(
            name=str(args.get("action_name", "SC action"))[:80],
            keys=tuple(str(k) for k in keys),
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
