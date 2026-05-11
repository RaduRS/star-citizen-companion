# Star Citizen Companion

A voice companion for Star Citizen. Push-to-talk, asks an LLM brain (OpenAI
GPT-5 nano with vision, or MiniMax M2.7), replies via Deepgram Aura-2 voice
+ a transparent overlay. Built around a VKB Gladiator NTX EVO dual-stick
setup — once you drop your binding doc into `data/vkb_bindings.md`, the
assistant will answer "how do I X?" in terms of which stick button to press.

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
nano), OpenAI + Web, and MiniMax at runtime. Press and hold **Home** (or
whichever key you bind your VKB controller to send), speak your question,
release. The reply shows in a small overlay top-right and is spoken aloud.

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

## VKB context (TODO)

`src/sc_companion/data/vkb_bindings.md` is currently a placeholder. Drop
your VKB binding doc for Star Citizen there (markdown, format-flexible) and
restart — it'll be prepended to the brain's system prompt so it can name
specific stick buttons in its replies.

## Keyboard execution

The brain can press keyboard keys for you (e.g., "open mobiglas" → presses
`F1`). The list of safe defaults lives at
`src/sc_companion/data/sc_keyboard_defaults.md` and is also a stub — fill
in your actual bindings before relying on action execution.

Safety: only an allowlisted set of keys is ever pressed; Win key, Alt+F4,
Ctrl+Alt+Del are hard-blocked. The companion also refuses to send keys
unless Star Citizen is the foreground window.

## Manual test plan

After install, walk through `docs/manual-test.md` once to verify capture,
mic, hotkey, overlay, and quota all behave. (Note: the manual test doc was
inherited from x4-companion and still references X4 in places — adjust as
you go.)
