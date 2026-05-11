import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PATH = Path.home() / ".sc-companion" / "config.toml"

@dataclass
class HotkeyConfig:
    key: str = "home"

@dataclass
class AudioConfig:
    input_device: str = ""
    output_device: str = ""

@dataclass
class VoiceConfig:
    provider: str = "deepgram"
    model: str = "aura-2-thalia-en"

@dataclass
class BrainConfig:
    default: str = "openai"
    model: str = "MiniMax-M2.7"
    openai_model: str = "gpt-5-nano"
    openai_reasoning_effort: str = "low"
    image_understanding: bool = True
    history_turns: int = 12
    web_search: bool = False

@dataclass
class OverlayConfig:
    position: str = "top-right"
    opacity: float = 0.85
    font_size: int = 16
    fade_seconds: int = 30

@dataclass
class Secrets:
    minimax_api_key: str = ""
    deepgram_api_key: str = ""
    openai_api_key: str = ""

@dataclass
class Config:
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    brain: BrainConfig = field(default_factory=BrainConfig)
    overlay: OverlayConfig = field(default_factory=OverlayConfig)
    secrets: Secrets = field(default_factory=Secrets)

def load_config(path: Path = DEFAULT_PATH) -> Config:
    data: dict = {}
    if path.exists():
        data = tomllib.loads(path.read_text())
    return Config(
        hotkey=HotkeyConfig(**data.get("hotkey", {})),
        audio=AudioConfig(**data.get("audio", {})),
        voice=VoiceConfig(**data.get("voice", {})),
        brain=BrainConfig(**data.get("brain", {})),
        overlay=OverlayConfig(**data.get("overlay", {})),
        secrets=Secrets(
            minimax_api_key=os.environ.get("MINIMAX_API_KEY", ""),
            deepgram_api_key=os.environ.get("DEEPGRAM_API_KEY", ""),
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        ),
    )


_BRAIN_HEADER_RE = re.compile(r"^\[brain\][ \t]*$", re.MULTILINE)
_NEXT_SECTION_RE = re.compile(r"^\[", re.MULTILINE)
# Use [ \t]* not \s* — \s eats newlines and would consume the line above.
_DEFAULT_LINE_RE = re.compile(r"^[ \t]*default[ \t]*=[ \t]*.*$", re.MULTILINE)


def save_brain_default(brain_key: str, path: Path = DEFAULT_PATH) -> None:
    """Surgically write `default = "<brain_key>"` into the [brain] section of
    config.toml. Creates the file (and parent dir) if missing. Preserves any
    other sections, keys, and comments the user may have added."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new_line = f'default = "{brain_key}"'

    if not path.exists():
        path.write_text(f"[brain]\n{new_line}\n", encoding="utf-8")
        return

    text = path.read_text(encoding="utf-8")
    header = _BRAIN_HEADER_RE.search(text)
    if header is None:
        sep = "" if text.endswith("\n") or not text else "\n"
        path.write_text(f"{text}{sep}\n[brain]\n{new_line}\n", encoding="utf-8")
        return

    section_start = header.end()
    next_section = _NEXT_SECTION_RE.search(text, pos=section_start + 1)
    section_end = next_section.start() if next_section else len(text)
    section = text[section_start:section_end]

    if _DEFAULT_LINE_RE.search(section):
        section = _DEFAULT_LINE_RE.sub(new_line, section, count=1)
    else:
        section = "\n" + new_line + section

    path.write_text(text[:section_start] + section + text[section_end:], encoding="utf-8")
