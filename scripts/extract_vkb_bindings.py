"""Parse a Star Citizen actionmap XML export and emit a markdown reference of
VKB stick bindings grouped by category. Writes to data/vkb_bindings.md so the
brain has a token-efficient summary of what each stick button does.

Re-run whenever the XML profile changes:
    python scripts/extract_vkb_bindings.py
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = ROOT / "src" / "sc_companion" / "data" / "Dual VKB Gladiator NXT"
XML_PATH = PROFILE_DIR / "layout_BK_DualVKB_4-6_exported.xml"
OUT_PATH = ROOT / "src" / "sc_companion" / "data" / "vkb_bindings.md"

# Per the deviceoptions block in the XML: js1 = Right stick, js2 = Left stick
# (Star Citizen indexes joysticks by enumeration order, not physical hand.)
DEVICE_LABEL = {
    "js1": "right stick",
    "js2": "left stick",
    "kb1": "keyboard",
    "mo1": "mouse",
}

MODIFIER_NAMES = {
    "lctrl": "L-Ctrl", "rctrl": "R-Ctrl",
    "lshift": "L-Shift", "rshift": "R-Shift",
    "lalt": "L-Alt", "ralt": "R-Alt",
}

CATEGORY_LABELS = {
    "seat_general": "Seat (general / mode select)",
    "spaceship_general": "Ship — general",
    "spaceship_view": "Ship — view & camera",
    "spaceship_movement": "Ship — flight & throttle",
    "spaceship_docking": "Ship — docking",
    "spaceship_targeting": "Ship — targeting",
    "spaceship_targeting_advanced": "Ship — targeting (advanced)",
    "spaceship_target_hailing": "Ship — hailing",
    "spaceship_radar": "Ship — radar",
    "spaceship_scanning": "Ship — scanning",
    "spaceship_mining": "Ship — mining",
    "spaceship_salvage": "Ship — salvage",
    "spaceship_weapons": "Ship — weapons",
    "spaceship_missiles": "Ship — missiles",
    "spaceship_defensive": "Ship — countermeasures / defense",
    "spaceship_power": "Ship — power triangle",
    "spaceship_hud": "Ship — HUD / MFD",
    "turret_movement": "Turret — movement",
    "turret_advanced": "Turret — advanced",
    "lights_controller": "Lights",
    "player": "On-foot — player",
    "tractor_beam": "Tractor beam",
    "zero_gravity_eva": "EVA — zero-G",
    "zero_gravity_traversal": "EVA — traversal",
    "vehicle_general": "Ground vehicle — general",
    "vehicle_driver": "Ground vehicle — driver",
    "spectator": "Spectator",
    "default": "Default",
    "player_input_optical_tracking": "Head/optical tracking",
    "player_choice": "Player choice",
    "view_director_mode": "Director mode",
}


def humanize_action(name: str) -> str:
    """v_ifcs_speed_limiter_toggle -> Speed Limiter Toggle (drops the v_/ifcs_ noise)."""
    s = name
    for prefix in ("v_ifcs_", "v_view_", "v_atc_", "v_target_", "v_weapon_",
                   "v_emote_", "v_eva_", "v_ifcs", "v_"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    return s.replace("_", " ").strip().title()


def parse_input(raw: str) -> str | None:
    """Translate an XML input string like 'js2_rctrl+button10' into a human
    description like 'left stick: R-Ctrl + button 10'. Returns None for
    unbound entries (empty/whitespace tail)."""
    if not raw:
        return None
    # raw forms seen: "js1_button22", "js2_rctrl+button10",
    # "js2_hat1_up", "js2_roty", "kb1_f", "mo1_mouse1", "js1_ " (unbound)
    m = re.match(r"^(js[12]|kb[12]|mo[12])_(.*)$", raw)
    if not m:
        return raw  # unknown shape, pass through verbatim
    device = DEVICE_LABEL.get(m.group(1), m.group(1))
    rest = m.group(2).strip()
    if not rest:
        return None  # unbound

    # Split on '+' to separate modifier(s) from the actual button/hat/axis
    parts = rest.split("+")
    *mods, target = parts
    mod_str = " + ".join(MODIFIER_NAMES.get(m, m) for m in mods)

    # Normalise the target token
    if target.startswith("button"):
        target_human = f"button {target[len('button'):]}"
    elif target.startswith("hat"):
        # hat1_up, hat1_down_left, etc.
        bits = target.split("_", 1)
        hat_n = bits[0][len("hat"):]
        direction = bits[1] if len(bits) > 1 else ""
        target_human = f"hat {hat_n} {direction}".strip()
    elif target in {"x", "y", "z", "rotx", "roty", "rotz", "slider1", "slider2"}:
        target_human = f"axis {target}"
    elif target.startswith("mouse"):
        target_human = f"mouse {target[len('mouse'):]}"
    else:
        target_human = target

    if mod_str:
        return f"{device}: {mod_str} + {target_human}"
    return f"{device}: {target_human}"


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
        "# VKB Gladiator EVO Pro — BuzZz Killer Dual VKB profile",
        "",
        "Generated from "
        "`src/sc_companion/data/Dual VKB Gladiator NXT/"
        "layout_BK_DualVKB_4-6_exported.xml` "
        "(Star Citizen 4.6 export). Re-run "
        "`scripts/extract_vkb_bindings.py` whenever the profile changes.",
        "",
        "Joystick assignment per the profile:",
        "- **right stick** (`js1`) — VKBsim Gladiator EVO R",
        "- **left stick** (`js2`) — VKBsim Gladiator EVO L",
        "",
        "When the user asks 'how do I X', name the physical button below "
        "(e.g. \"left stick button 28, double-tap\") and cross-reference the "
        "Ground/Ship binding chart PDFs in the same folder for the exact "
        "physical key labels (T1, A4 HAT, etc.).",
        "",
    ]

    total_bound = 0
    for am in root.findall("actionmap"):
        am_name = am.get("name") or "(unnamed)"
        label = CATEGORY_LABELS.get(am_name, am_name)
        rows: list[str] = []
        for act in am.findall("action"):
            act_name = act.get("name") or ""
            for rb in act.findall("rebind"):
                desc = parse_input(rb.get("input") or "")
                if desc is None:
                    continue
                modifier = parse_activation(rb)
                rows.append(
                    f"- `{act_name}` ({humanize_action(act_name)}) — "
                    f"{desc}{modifier}"
                )
                total_bound += 1
        if not rows:
            continue
        out.append(f"## {label} (`{am_name}`)")
        out.append("")
        out.extend(rows)
        out.append("")

    out.append(f"---")
    out.append(f"_{total_bound} bound entries across "
               f"{sum(1 for _ in root.findall('actionmap'))} categories._")

    OUT_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes, "
          f"{total_bound} bindings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
