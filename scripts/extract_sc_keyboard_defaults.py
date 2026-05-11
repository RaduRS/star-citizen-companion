"""Parse Star Citizen's default action map XML and emit a markdown reference
of every keyboard (kb1_*) binding. Writes data/sc_keyboard_defaults.md so the
brain knows which key to press for any action.

Source: src/sc_companion/data/sc_defaults_3.0.xml (Ben Humpert's All
Keybindings dump for 3.0, CC BY-SA 4.0). Action names + ~80% of keys are
stable through 4.x; some categories (master mode toggle, weapon group
selectors, MFD cycling) have shifted in later patches — the brain is told
to prefer screenshot hints over this list when there's a conflict.

Re-run whenever a fresher dump is available:
    python scripts/extract_sc_keyboard_defaults.py
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XML_PATH = ROOT / "src" / "sc_companion" / "data" / "sc_defaults_3.0.xml"
OUT_PATH = ROOT / "src" / "sc_companion" / "data" / "sc_keyboard_defaults.md"

# Map XML keycode tokens to Python keyboard-library syntax.
KEY_TOKENS = {
    "lctrl": "ctrl",
    "rctrl": "right ctrl",
    "lshift": "shift",
    "rshift": "right shift",
    "lalt": "alt",
    "ralt": "right alt",
    "mwheel_up": "scroll up",
    "mwheel_down": "scroll down",
    "np_enter": "num enter",
    "np_div": "num /",
    "np_mul": "num *",
    "np_add": "num +",
    "np_sub": "num -",
    "np_period": "num .",
    "tilde": "`",
    "minus": "-",
    "equals": "=",
    "lbracket": "[",
    "rbracket": "]",
    "semicolon": ";",
    "apostrophe": "'",
    "comma": ",",
    "period": ".",
    "slash": "/",
    "backslash": "\\",
    "prtsc": "print screen",
    "scroll": "scroll lock",
    "pgup": "page up",
    "pgdn": "page down",
}

CATEGORY_LABELS = {
    "spaceship_general": "Ship — general",
    "spaceship_view": "Ship — view & camera",
    "spaceship_movement": "Ship — flight & movement",
    "spaceship_docking": "Ship — docking",
    "spaceship_targeting": "Ship — targeting",
    "spaceship_targeting_advanced": "Ship — targeting (advanced)",
    "spaceship_target_hailing": "Ship — hailing",
    "spaceship_radar": "Ship — radar / scanning",
    "spaceship_scanning": "Ship — scanning",
    "spaceship_mining": "Ship — mining",
    "spaceship_salvage": "Ship — salvage",
    "spaceship_turret": "Turret",
    "turret_movement": "Turret — movement",
    "turret_advanced": "Turret — advanced",
    "spaceship_weapons": "Ship — weapons",
    "spaceship_missiles": "Ship — missiles",
    "spaceship_defensive": "Ship — countermeasures / defense",
    "spaceship_power": "Ship — power triangle",
    "spaceship_hud": "Ship — HUD / MFD",
    "lights_controller": "Lights",
    "player": "On-foot — player",
    "prone": "On-foot — prone",
    "tractor_beam": "Tractor beam",
    "zero_gravity_eva": "EVA — zero-G",
    "zero_gravity_traversal": "EVA — traversal",
    "vehicle_general": "Ground vehicle — general",
    "vehicle_driver": "Ground vehicle — driver",
    "vehicle_gunner": "Ground vehicle — gunner",
    "spectator": "Spectator",
    "default": "Default / global",
    "multiplayer": "Multiplayer",
    "invite": "Party / invite",
    "player_emotes": "Emotes",
    "player_choice": "Player choice",
    "player_input_optical_tracking": "Head/optical tracking",
    "view_director_mode": "Director mode",
    "seat_general": "Seat (general / mode select)",
    "remote_camera": "Remote camera",
}

# Patch-volatile categories: brain should prefer the on-screen prompt over
# the listed default and decline cleanly when uncertain.
VOLATILE_CATEGORIES = {
    "spaceship_general",       # power on/off, flight ready, doors — moved a lot
    "spaceship_movement",      # master mode toggle, decoupled etc.
    "spaceship_weapons",       # group selectors changed in master mode
    "spaceship_power",         # power triangle binds got reshuffled
    "spaceship_hud",           # MFD cycling shifted to alt+E/Q in 4.x
}

# Hand-maintained overrides for entries whose default key changed between
# the 3.0 source dump and current SC. Action ID -> current key (Python
# keyboard library syntax). Add entries here as the user reports
# mispresses during play; this layer survives `extract_*` regeneration.
PATCH_OVERRIDES: dict[str, str] = {
    "v_power_toggle": "u",  # 4.x: U toggles ship power (3.0 had 5)
}


def translate_token(tok: str) -> str:
    """kb1 token -> human key name suitable for the keyboard library."""
    return KEY_TOKENS.get(tok, tok)


def decode_kb_input(raw: str) -> str | None:
    """'kb1_lalt+l' -> 'alt+l'. Returns None for non-keyboard inputs."""
    if not raw.startswith("kb1_"):
        return None
    body = raw[len("kb1_"):].strip()
    if not body:
        return None
    parts = body.split("+")
    return "+".join(translate_token(p) for p in parts)


def humanize_action(name: str) -> str:
    """v_ifcs_speed_limiter_toggle -> Speed Limiter Toggle. Strips common
    StarEngine prefixes so the readable name is what the brain sees."""
    s = name
    for prefix in ("v_ifcs_", "v_view_", "v_atc_", "v_target_", "v_weapon_",
                   "v_eva_", "v_emote_", "v_pl_", "v_ifcs", "v_"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    return s.replace("_", " ").strip().title() or name


def parse_activation(rebind: ET.Element) -> str:
    bits: list[str] = []
    mode = rebind.get("activationMode")
    if mode and mode != "press":
        bits.append(mode.replace("_", "-"))
    multitap = rebind.get("multiTap")
    if multitap and multitap != "1":
        bits.append(f"{multitap}x tap")
    hold = rebind.get("holdTriggerDelay")
    if hold:
        bits.append(f"hold {hold}s")
    return f" ({', '.join(bits)})" if bits else ""


def main() -> int:
    if not XML_PATH.exists():
        print(f"missing XML: {XML_PATH}", file=sys.stderr)
        return 1
    tree = ET.parse(str(XML_PATH))
    root = tree.getroot()

    out: list[str] = [
        "# Star Citizen — default KEYBOARD bindings",
        "",
        "Generated from `src/sc_companion/data/sc_defaults_3.0.xml` "
        "(Ben Humpert, *All Keybindings using ADVANCED CONTROLS*, "
        "CC BY-SA 4.0). Source dump is for SC 3.0; action names are stable "
        "through 4.x but a handful of categories were rebound across major "
        "patches. Re-run `scripts/extract_sc_keyboard_defaults.py` against "
        "a newer XML when one is available.",
        "",
        "## Important notes for the brain",
        "",
        "1. **Screenshot wins.** If the screenshot shows a contextual hint "
        "like `Press <key> to <action>`, use that key literally — it "
        "overrides this list. SC moves keys across patches; the on-screen "
        "hint is always current.",
        "2. **Patch-volatile categories** (marked ⚠ below): master-mode "
        "toggle, flight-ready, power-triangle bindings, MFD cycling, "
        "weapon-group selectors. If you're about to press a key from one "
        "of those sections and the screenshot doesn't confirm it, "
        "**decline politely** rather than guess.",
        "3. **Modifier syntax for execution** uses the Python `keyboard` "
        "library: `alt+l`, `right shift+backspace`, `ctrl+f`. Hold/double-tap "
        "activation is noted in parens after each key.",
        "4. **Joystick-only actions** (no `kb1_*` entry below for that "
        "action) — the user runs a 100% joystick VKB profile. If an action "
        "is not in this list, it has no vanilla keyboard binding. **Do "
        "not invent one.** Tell the user to use their stick.",
        "",
        "---",
        "",
    ]

    total = 0
    override_count = 0
    for am in root.findall("actionmap"):
        am_name = am.get("name") or "(unnamed)"
        label = CATEGORY_LABELS.get(am_name, am_name)
        marker = " ⚠" if am_name in VOLATILE_CATEGORIES else ""
        rows: list[str] = []
        for act in am.findall("action"):
            act_name = act.get("name") or ""
            for rb in act.findall("rebind"):
                key = decode_kb_input(rb.get("input") or "")
                if key is None:
                    continue
                modifier = parse_activation(rb)
                # Apply user-reported patch overrides over the 3.0 default.
                # We mark the entry so the brain knows it's curated, not raw.
                override = PATCH_OVERRIDES.get(act_name)
                note = ""
                if override is not None and override != key:
                    key = override
                    note = " (4.x override)"
                    override_count += 1
                rows.append(
                    f"- `{act_name}` ({humanize_action(act_name)}) — "
                    f"`{key}`{modifier}{note}"
                )
                total += 1
        if not rows:
            continue
        out.append(f"## {label} (`{am_name}`){marker}")
        out.append("")
        out.extend(rows)
        out.append("")

    out.append("---")
    out.append(
        f"_{total} keyboard bindings parsed ({override_count} 4.x overrides "
        "applied). ⚠ = patch-volatile category — verify with on-screen hints._"
    )

    OUT_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes, "
          f"{total} bindings, {override_count} overrides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
