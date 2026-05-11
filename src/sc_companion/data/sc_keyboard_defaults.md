# Star Citizen — default KEYBOARD bindings (vanilla)

This file is the source of truth for the Star Citizen Companion's keyboard
execution. The companion sends OS-level keyboard events, so action proposals
must use **keyboard keys** here, never VKB stick button names.

## Important notes for the brain

1. **Screenshot wins.** If the screenshot shows a contextual hint like
   `Press <key> to <action>`, use that key literally — it overrides this
   list. SC patches sometimes rebind defaults; the hint is always current.
2. **High-confidence only.** This list is curated for keys that have been
   stable across recent patches (4.x). Entries marked `(verify)` change
   frequently — if you don't see the action in the screenshot's hints AND
   it's marked `(verify)` here, prefer to **decline politely** rather than
   guess.
3. **Modifiers in this list use the Python `keyboard` library syntax**:
   `shift+x`, `ctrl+f`, `alt+m`, `right shift+backspace`. Hold-to-arm
   actions are noted as such.
4. **The user runs JoyToKey + a 100% joystick VKB profile** (BuzZz Killer's
   Dual VKB). That means most ship actions reach SC via simulated keyboard
   events too — so default keyboard bindings still work in their setup.

---

## Universal / UI

- `F1` — Open/close MobiGlas
- `F2` — Personal Inner Thought / inventory access (verify)
- `F4` — Cycle camera views (cockpit ↔ external orbit ↔ chase)
- `F5` — Selfie camera
- `F8` — Return to default view
- `F10` — Voice chat push-to-talk
- `F11` — Open Star Map (galactic map, used for quantum travel)
- `F12` — Screenshot
- `Esc` — Open/close game menu (pause)
- `Backspace` — Back / cancel current menu (also: arm component for self-destruct sequence when held with `Right Shift`)
- `Tab` — Cycle MFD focus in cockpit; cycle context in some menus
- `~` — Console (developer; usually disabled in live)

## Movement — on-foot

- `W` / `A` / `S` / `D` — Walk forward / strafe left / back / right
- `Space` — Jump (tap) / jump up in zero-G
- `Left Shift` — Sprint (hold)
- `Left Ctrl` — Crouch (toggle)
- `Z` — Prone (verify — was `X` in older patches)
- `Left Alt` — Walk (slow toggle)
- `C` — Lean / cover toggle (verify)

## Interaction — on-foot

- `F` — Interact short-press (use the highlighted thing)
- `F` (hold) — Open inner thought wheel (context menu of nearby interactions)
- `Y` (hold) — Initiate EVA (in zero-G context) / vector control

## Weapons — on-foot

- `Left Mouse` — Fire
- `Right Mouse` (hold) — ADS / aim down sights
- `R` — Reload
- `1` — Primary weapon
- `2` — Secondary weapon
- `3` — Sidearm
- `4` — Knife / melee weapon
- `G` — Throw grenade (verify)
- `H` — Holster / unholster

## Ship — power & systems

- `U` — Toggle ship power (engines + thrusters off/on)
- `I` — Flight ready / activate ship systems (verify — has been `U`, `Right Alt+Shift+P`, others)
- `O` — Open/close doors of current ship (verify)
- `R` — Toggle landing gear
- `L` — Toggle ship lights
- `N` — Toggle engines (verify — sometimes the engine toggle is bound elsewhere)
- `K` — Self-destruct (10s arm) — actually: `Right Shift+Backspace` (hold)
- `0` (zero) — Cycle shield level (verify)

## Ship — flight modes

- `Caps Lock` — Toggle SCM / NAV master mode (verify — has been `M` / `B` historically)
- `V` — Toggle decoupled mode (free rotation, no auto-orient)
- `X` — Brake / hold position (kills relative velocity)
- `Space` — Boost / afterburner (hold while moving)
- `Left Shift` (in flight) — Boost (verify — sometimes `Tab`)
- `Z` — VTOL toggle (verify; only on VTOL-capable ships)

## Ship — quantum / navigation

- `B` (hold) — Spool quantum drive toward target
- `B` (tap, after spool + lock) — Engage quantum travel
- `J` — Cycle quantum target forward (verify)
- `F11` — Open Star Map to pick a quantum destination
- `Insert` — Save (in tutorials / single-player flows; usually not in PU)

## Ship — weapons

- `Space` (in cockpit) — Fire weapon group 1
- `Left Mouse` (in cockpit) — Fire weapon group 1
- `Right Mouse` (in cockpit) — Fire weapon group 2 / launch missiles when armed
- `1` — Select weapon group 1
- `2` — Select weapon group 2
- `3` — Select weapon group 3 (if assigned)
- `G` — Toggle gimbal lock (verify)
- `T` — Target reticle / scan toggle (verify)

## Ship — missiles & countermeasures

- `Right Alt+T` — Increase missile range / target lock distance (verify)
- `Right Alt+G` — Decrease missile range (verify)
- `H` — Deploy chaff / countermeasure (verify — has been `J`, `H`)
- `G` — Deploy flare (verify)

## Ship — power triangle

- `F5` (in cockpit, no modifier) — actually conflict; see below
- `Right Alt+1` — Max power to weapons
- `Right Alt+2` — Max power to shields
- `Right Alt+3` — Max power to thrusters
- `Right Alt+4` — Equal power distribution (verify)

(SC's power triangle binds shift a lot. Verify with the in-game keybinding menu before relying on these for execution.)

## Ship — targeting

- `T` — Lock target under reticle (verify)
- `Tab` — Cycle nearest hostile target (verify)
- `Right Tab` — Cycle nearest friendly (verify)
- `R` (out of cockpit context) — Reload (don't confuse with landing gear)
- `Mouse 4` / `Mouse 5` — Cycle target subsystems (verify; needs mouse with side buttons)
- `Right Alt+R` — Cycle targets reset / all (verify)

## Ship — scanning & mining

- `Tab` (in scan mode) — Trigger scan ping
- `Left Mouse` (in mining mode) — Fire mining laser
- `Scroll wheel` — Throttle mining laser power
- `M` — Toggle mining mode (verify — has overlapped with map key)
- `R` (mining/salvage) — Cycle laser type / consumable
- `G` (mining) — Mining consumable 1 (verify)

## Ship — comms / ATC

- `Y` — Hail target (open comms with locked target)
- `N` — Comms decline (verify; sometimes accept/decline are reversed)
- `Left Alt+N` — Cycle ATC request (verify — Loading Area / Hangar / Landing)

## EVA / zero-G

- `W` / `A` / `S` / `D` — Strafe in 3D space
- `Space` — Strafe "up" (relative to helmet)
- `Left Ctrl` — Strafe "down"
- `Q` / `E` — Roll left / right
- `Shift` — Boost (hold)
- `X` — Brake / kill velocity
- `Y` (hold) — Toggle EVA mode (verify)

## Ground vehicles

- `W` / `A` / `S` / `D` — Throttle / steer
- `Space` — Handbrake
- `Left Shift` — Boost
- `R` — Driver gear (verify — varies by vehicle)
- `F` — Exit vehicle (hold)
- `L` — Vehicle lights

---

## Known to change across patches (be extra careful)

- Master-mode toggle (SCM ↔ NAV) — moved between `M`, `B`, `Caps Lock` across recent patches.
- Power-on / flight-ready — `U` vs `I` vs combinations have shifted.
- Self-destruct — historically `Right Shift+Backspace (hold 3s)`; the
  `Backspace` key wins the actual trigger, the shift modifier arms it.
- Mining mode toggle — has overlapped with map/MFD keys.

When in doubt, look at the screenshot for a current contextual hint and use
that key. Or decline politely and tell the user to check
`Options → Keybindings`.
