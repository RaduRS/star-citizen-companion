"""Star Citizen keyboard binding loader. Stub.

Star Citizen stores per-user actionmaps at:
    %USERPROFILE%\\Saved Games\\roberts space industries\\StarCitizen\\
    LIVE\\user\\client\\0\\controls\\mappings\\layout_my_*.xml

The shape is meaningfully different from X4's inputmap.xml — actions live
under <actionmap> blocks with <action> children, and bindings reference
input devices via attributes like input="kb1_h". Wire this up once the
user's preferred export is settled. Until then the brain falls back to the
vendored sc_keyboard_defaults.md.
"""
from __future__ import annotations

from pathlib import Path


def find_user_inputmap() -> Path | None:
    return None


def parse_inputmap(path: Path) -> dict[str, str]:
    return {}


def format_bindings_markdown(bindings: dict[str, str]) -> str:
    return ""


def format_synonym_table(bindings: dict[str, str]) -> str:
    return ""


ACTION_SYNONYMS: list[tuple[str, list[str]]] = []
