# Manual test plan — Star Citizen Companion

Run on the **Windows gaming PC**. The single-instance lock will refuse a
second startup, so quit any tray-running copy first.

## Prereqs

- Repo cloned, `pip install -e ".[dev]"` complete (or just `pip install -e .`)
- `.env` populated with `DEEPGRAM_API_KEY` plus at least one of
  `OPENAI_API_KEY` (gpt-5-nano default) or `MINIMAX_API_KEY`
- Star Citizen installed; **Settings → Graphics → Display Mode = Borderless
  Windowed** (capture won't grab Exclusive Fullscreen)
- A hotkey to push-to-talk: `Home` by default, or whatever your VKB
  controller is bound to send via JoyToKey

## Run

    python -m sc_companion

Or double-click the desktop shortcut (`Star Citizen Companion`).

## Smoke checks (no game running yet)

1. SC reticle icon appears in the tray.
2. Press `Home`, hold for 1s, say "hello", release.
3. Within ~3s: overlay shows a reply, TTS speaks it.
4. Right-click tray → **Brain** submenu shows OpenAI / OpenAI + Web /
   MiniMax. Switch to a different one — overlay confirms `(switched to ...)`.
5. Right-click tray → Quit. Process exits cleanly.
6. Launch a second time while the first is still running — second exits
   immediately with a "already running" messagebox.

## In-game checks (SC launched, borderless windowed)

1. Press `Home`, ask "what is on my screen?". Reply describes the SC HUD —
   cockpit, MFDs, mobiGlas if open, etc.
2. Hold `Home`, say nothing, release within 200ms → overlay says
   "(didn't catch that)".
3. Pull network → press `Home`, ask anything → overlay shows
   "(brain error: ...)".
4. Switch SC to Exclusive Fullscreen → overlay says "(capture failed: ...)"
   instead of crashing.
5. Ask 3 follow-up questions in a row — answers should reflect awareness of
   prior turns.

## Binding-aware replies

These exercise the BuzZz Killer Dual VKB profile reference:

1. "How do I self-destruct?" → mentions left stick button 28 (double-tap).
2. "How do I engage the quantum drive?" → walks through spool + engage.
3. "How do I set scan mode?" → mentions right stick R-Ctrl + button 22.

## Action execution (keyboard auto-press)

These rely on `sc_keyboard_defaults.md`. Star Citizen must be the foreground
window or the action is refused with "Star Citizen is not the foreground
window".

1. "Open my mobiGlas" → brain calls `propose_sc_action`, presses `F1`.
2. "Cycle camera view" → presses `F4`.
3. "Take a screenshot" → presses `F12`.
4. Ask for something only your VKB profile knows (e.g. "transform cycle") →
   brain should describe the stick button rather than press a key it
   doesn't have a default for.

## Latency

Stopwatch from PTT release to first audible word. Target ≤ 3s.

## Quota / cost check

After ~30 questions in a session, no rate-limit errors. (gpt-5-nano +
Deepgram are well under any per-minute caps for normal play.)
