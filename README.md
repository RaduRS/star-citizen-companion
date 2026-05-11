# Star Citizen Companion

A voice companion for Star Citizen. Push-to-talk, asks an LLM brain (OpenAI
GPT-5 nano with vision, or MiniMax M2.7), replies via Deepgram Aura-2 voice
+ a transparent overlay. Built around a VKB Gladiator NTX EVO dual-stick
setup with BuzZz Killer's Dual VKB profile — the brain knows all 223 stick
bindings plus SC's vanilla keyboard defaults, so it can press keys for you
("open mobiglas" → presses F1) and answer "how do I X?" questions in terms
of your actual layout.

Forked from [x4-companion](https://github.com/<owner>/x4-companion). Same
architecture, different game-specific bits (system prompt, bindings, action
tool, foreground-window check).

## How it runs

There is no installer or `.exe`. You run it from source:

```
python -m sc_companion
```

To update later: `git pull && python -m sc_companion`.

## Install (Windows gaming PC)

Requires Python 3.12+.

```
git clone https://github.com/<owner>/star-citizen-companion.git
cd star-citizen-companion
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

(`pip install -e ".[dev]"` if you also want the test suite.)

## API keys (do **not** commit these)

The repo is public — never put API keys in any file that's committed.
`.env` is gitignored; the only file that holds keys is `.env` on your
gaming PC, created from `.env.example`:

```
copy .env.example .env
```

Then edit `.env`. You need Deepgram (for STT + TTS), and at least one of
OpenAI or MiniMax for the brain:

```
DEEPGRAM_API_KEY=...
OPENAI_API_KEY=sk-...        # default brain: gpt-5-nano
MINIMAX_API_KEY=mxp-...      # optional alternate brain
```

System environment variables also work and take precedence over `.env`.

## Run

Star Citizen must be in **Borderless Windowed** (capture won't work in
Exclusive Fullscreen).

```
.venv\Scripts\activate
python -m sc_companion
```

A tray icon appears with a Brain submenu — switch between OpenAI (GPT-5
nano), OpenAI + Web, and MiniMax at runtime. **Your active brain choice
is persisted** to `~/.sc-companion/config.toml` and survives restarts.
Only one instance runs at a time — double-clicking the launcher while
the tray icon is already there will pop a "already running" messagebox
and exit, not run a duplicate.

Press and hold **Home** (or whichever key you bind your VKB controller
to send), speak your question, release. The reply shows in a small
overlay top-right and is spoken aloud.

## Configuration

Optional `~/.sc-companion/config.toml`:

```toml
[hotkey]
key = "home"

[voice]
model = "aura-2-thalia-en"

[brain]
default = "openai"           # "openai" | "openai_web" | "minimax"
openai_model = "gpt-5-nano"
openai_reasoning_effort = "low"
history_turns = 12

[overlay]
position = "top-right"
opacity = 0.85
font_size = 16
fade_seconds = 30
```

## VKB context

The VKB stick layout the brain knows is generated from
`src/sc_companion/data/Dual VKB Gladiator NXT/layout_BK_DualVKB_4-6_exported.xml`
(BuzZz Killer's Dual VKB Gladiator EVO Pro profile, SC 4.6) by
`scripts/extract_vkb_bindings.py` → `data/vkb_bindings.md`. That markdown
file is loaded at startup and prepended to the system prompt, so the brain
answers "how do I X?" in terms of specific stick buttons.

If you update the XML profile (new SC patch, rebound something), re-run:

```
python scripts/extract_vkb_bindings.py
```

The folder also ships the canonical PDFs (Ground / Ship binding charts) —
keep those open on a second monitor for the physical button labels (T1, A4
HAT, etc.) that the chart PDFs map to the numeric `button N` references.

## Keyboard execution

The brain presses keys via the `propose_sc_action` tool. Source-of-truth
for which key maps to which action is
`src/sc_companion/data/sc_keyboard_defaults.md`, generated from
`sc_defaults_3.0.xml` by `scripts/extract_sc_keyboard_defaults.py`.

**When the brain presses a wrong key** (SC defaults drift between
patches), add an entry to the `PATCH_OVERRIDES` dict at the top of
`scripts/extract_sc_keyboard_defaults.py`, then re-run the script:

```python
PATCH_OVERRIDES: dict[str, str] = {
    "v_power_toggle": "u",  # 4.x: U (was 5 in the 3.0 dump)
    # add more as you spot them during play
}
```

```
python scripts/extract_sc_keyboard_defaults.py
```

The brain's prompt also tells it: when asked to do something, **press
the key, don't describe the stick**. If an action has no keyboard
binding (joystick-only in your profile, or new since the 3.0 dump),
the brain declines with "I can't press that — no keyboard binding I
can use." It will not tell you which stick button to press in that
case — that's deliberate per user preference.

### Safety

- Only an allowlisted set of keys is ever pressed; Win key, Alt+F4,
  Ctrl+Alt+Del are hard-blocked.
- The companion refuses to send keys unless Star Citizen is the
  foreground window.
- If the brain ever proposes a joystick name (e.g. "button 26") as a
  keyboard key, the extraction layer drops it and rewrites the spoken
  reply to "I can't press that" — no fake announcement.

## Vendored data + licenses

- `src/sc_companion/data/Dual VKB Gladiator NXT/` — BuzZz Killer's Dual
  VKB Gladiator EVO Pro profile for SC 4.6 (XML actionmap, Ground/Ship
  chart PDFs, JoyToKey configs). Source:
  [Spectrum thread](https://robertsspaceindustries.com/spectrum/community/SC/forum/50174/thread/buzzz-killer-s-recommended-exported-bindings).
- `src/sc_companion/data/sc_defaults_3.0.xml` — Ben Humpert, *All
  Keybindings using ADVANCED CONTROLS* (SC 3.0 dump), licensed
  **CC BY-SA 4.0**. Source:
  [GitHub gist](https://gist.github.com/an3k/1fe4a6782e1d21e7821f64af208a22b5).
  Any redistribution of derivatives of this file (including the
  generated `sc_keyboard_defaults.md`) must preserve the attribution
  and share-alike terms.

## Manual test plan

After install, walk through `docs/manual-test.md` once to verify capture,
mic, hotkey, overlay, brain switching, action execution, and binding-aware
replies all behave.
