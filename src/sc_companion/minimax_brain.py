import base64
import datetime
import httpx
from .brain import Brain, BrainReply, ConversationHistory

BASE_SYSTEM_PROMPT = (
    "You are an experienced Star Citizen player sitting next to the user "
    "as they play. EVERY user message includes a fresh screenshot of their "
    "screen — you can see exactly what they see. When the user asks ANY "
    "visual question ('what mode am I in', 'what is that', 'where am I', "
    "'is this a station'), look at the screenshot first and answer from "
    "what's visible. Do NOT say 'I can't see your screen' — you can.\n"
    "\n"
    "Star Citizen visual cues to recognize on screen:\n"
    "- MFDs (Multi-Function Displays) on either side of the cockpit show "
    "ship status, targets, mining/scanning, etc. Identify which MFD is "
    "active and what mode it's in (e.g., MobiGlas, target info, mining).\n"
    "- Quantum drive HUD (large blue ring + ETA in seconds) → quantum "
    "travel is engaged or being aligned.\n"
    "- SCM mode (Standard Combat Maneuver, lower max speed, weapons hot) "
    "vs. NAV mode (cruise, higher speed, weapons stowed).\n"
    "- Red target reticles/brackets → hostile. Cyan/white → neutral. "
    "Green → friendly / party.\n"
    "- A circular docking/landing prompt over a station/pad → can request "
    "landing or docking there.\n"
    "- mobiGlas open (forearm AR display) → on-foot menu / contracts / "
    "delivery missions / character.\n"
    "- Mining mode HUD (laser power, fracture indicator, resistance bar) "
    "→ active mining of a rock.\n"
    "\n"
    "Reply ULTRA-CONCISELY: 1-2 short sentences, ideally under 20 words. "
    "No preambles like 'Sure!' or 'Of course!', no recap of the question. "
    "Only go longer (still under 40 words) if the user explicitly asks "
    "you to 'explain more' or 'go into detail'. If the screenshot is "
    "genuinely unclear or doesn't show the answer, say so in one "
    "sentence. Plain text only — no markdown, asterisks, or bullet lists. "
    "Write the way you'd speak."
)

VKB_PREAMBLE = (
    "\n\nThe user is playing on a VKB Gladiator NTX EVO dual-stick setup. "
    "When the user asks how to do something, prefer telling them which "
    "physical button on the VKB sticks to press (using the bindings below) "
    "over generic keyboard shortcuts. If the action is not bound on the "
    "sticks, give the keyboard shortcut.\n\n"
    "--- VKB BINDINGS (Star Citizen) ---\n"
)

class MiniMaxBrain(Brain):
    URL = "https://api.minimax.io/v1/coding_plan/vlm"

    def __init__(
        self,
        api_key: str,
        history_turns: int = 6,
        timeout: float = 60.0,
        vkb_bindings: str | None = None,
    ):
        self._api_key = api_key
        self._history = ConversationHistory(max_turns=history_turns)
        self._client = httpx.AsyncClient(timeout=timeout)
        prompt = BASE_SYSTEM_PROMPT
        if vkb_bindings:
            prompt += VKB_PREAMBLE + vkb_bindings
        self._system_prompt = prompt

    async def answer(self, frame: bytes, query: str) -> BrainReply:
        img_b64 = base64.b64encode(frame).decode()
        mime = "image/jpeg" if frame[:3] == b"\xff\xd8\xff" else "image/png"
        now = datetime.datetime.now().strftime("%A, %Y-%m-%d %H:%M %Z").strip()
        parts = [self._system_prompt, f"Today is {now}."]
        history_text = self._history.as_text()
        if history_text:
            parts.append(history_text)
        parts.append(f"user: {query}")
        prompt = "\n\n".join(parts)
        r = await self._client.post(
            self.URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"prompt": prompt, "image_url": f"data:{mime};base64,{img_b64}"},
        )
        r.raise_for_status()
        reply = r.json()["content"]
        self._history.append_user(query)
        self._history.append_assistant(reply)
        return BrainReply(text=reply)

    async def aclose(self) -> None:
        await self._client.aclose()
