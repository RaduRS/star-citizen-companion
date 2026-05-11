# Star Citizen — default KEYBOARD bindings

Generated from `src/sc_companion/data/sc_defaults_3.0.xml` (Ben Humpert, *All Keybindings using ADVANCED CONTROLS*, CC BY-SA 4.0). Source dump is for SC 3.0; action names are stable through 4.x but a handful of categories were rebound across major patches. Re-run `scripts/extract_sc_keyboard_defaults.py` against a newer XML when one is available.

## Important notes for the brain

1. **Screenshot wins.** If the screenshot shows a contextual hint like `Press <key> to <action>`, use that key literally — it overrides this list. SC moves keys across patches; the on-screen hint is always current.
2. **Patch-volatile categories** (marked ⚠ below): master-mode toggle, flight-ready, power-triangle bindings, MFD cycling, weapon-group selectors. If you're about to press a key from one of those sections and the screenshot doesn't confirm it, **decline politely** rather than guess.
3. **Modifier syntax for execution** uses the Python `keyboard` library: `alt+l`, `right shift+backspace`, `ctrl+f`. Hold/double-tap activation is noted in parens after each key.
4. **Joystick-only actions** (no `kb1_*` entry below for that action) — the user runs a 100% joystick VKB profile. If an action is not in this list, it has no vanilla keyboard binding. **Do not invent one.** Tell the user to use their stick.

---

## Ship — general (`spaceship_general`) ⚠

- `v_eject` (Eject) — `alt+l` (double-tap)
- `v_eject_cinematic` (Eject Cinematic) — `alt+l` (double-tap)
- `v_exit` (Exit) — `alt+f`
- `v_self_destruct` (Self Destruct) — `alt+backspace`
- `v_cooler_throttle_up` (Cooler Throttle Up) — `alt+np_8`
- `v_cooler_throttle_down` (Cooler Throttle Down) — `alt+np_7`
- `v_flightready` (Flightready) — `8`
- `v_doors_open_all` (Doors Open All) — `9`
- `v_doors_close_all` (Doors Close All) — `9`
- `v_doors_lock_all` (Doors Lock All) — `0`
- `v_doors_unlock_all` (Doors Unlock All) — `0`

## Ship — view & camera (`spaceship_view`)

- `v_view_cycle_fwd` (Cycle Fwd) — `f4`
- `v_view_mode` (Mode) — `f3`
- `v_view_zoom_in` (Zoom In) — `scroll up`
- `v_view_zoom_out` (Zoom Out) — `scroll down`
- `v_view_freelook_mode` (Freelook Mode) — `z`
- `v_view_look_behind` (Look Behind) — `alt+z`

## Ship — flight & movement (`spaceship_movement`) ⚠

- `v_toggle_relative_mouse_mode` (Toggle Relative Mouse Mode) — `alt+,`
- `v_roll_left` (Roll Left) — `q`
- `v_roll_right` (Roll Right) — `e`
- `v_toggle_yaw_roll_swap` (Toggle Yaw Roll Swap) — `alt+.`
- `v_throttle_toggle_minmax` (Throttle Toggle Minmax) — `backspace`
- `v_throttle_up` (Throttle Up) — `w`
- `v_throttle_down` (Throttle Down) — `s`
- `v_brake` (Brake) — `c`
- `v_target_match_vel` (Match Vel) — `m`
- `v_ifcs_toggle_vector_decoupling` (Toggle Vector Decoupling) — `v`
- `v_strafe_up` (Strafe Up) — `space`
- `v_strafe_down` (Strafe Down) — `ctrl`
- `v_strafe_left` (Strafe Left) — `a`
- `v_strafe_right` (Strafe Right) — `d`
- `v_strafe_forward` (Strafe Forward) — `alt+w`
- `v_strafe_back` (Strafe Back) — `alt+s`
- `v_ifcs_toggle_safeties` (Toggle Safeties) — `2`
- `v_ifcs_toggle_esp` (Toggle Esp) — `alt+o`
- `v_decoupled_brake` (Decoupled Brake) — `c`
- `v_decoupled_strafe_up` (Decoupled Strafe Up) — `space`
- `v_decoupled_strafe_down` (Decoupled Strafe Down) — `ctrl`
- `v_decoupled_strafe_left` (Decoupled Strafe Left) — `a`
- `v_decoupled_strafe_right` (Decoupled Strafe Right) — `d`
- `v_decoupled_strafe_forward` (Decoupled Strafe Forward) — `w`
- `v_decoupled_strafe_back` (Decoupled Strafe Back) — `s`
- `v_decoupled_roll_left` (Decoupled Roll Left) — `q`
- `v_decoupled_roll_right` (Decoupled Roll Right) — `e`
- `v_afterburner` (Afterburner) — `shift`
- `v_boost` (Boost) — `x`
- `v_toggle_landing_system` (Toggle Landing System) — `n`
- `v_autoland` (Autoland) — `n`
- `v_toggle_qdrive_engagement` (Toggle Qdrive Engagement) — `b`

## Ship — targeting (`spaceship_targeting`)

- `v_couple_aim_to_move` (Couple Aim To Move) — `alt+m`
- `v_toggle_mouse_aim_only` (Toggle Mouse Aim Only) — `right shift`
- `v_toggle_weapon_gimbal_lock` (Toggle Weapon Gimbal Lock) — `alt+j`
- `v_target_reticle_focus` (Reticle Focus) — `r`
- `v_target_cycle_all_fwd` (Cycle All Fwd) — `i`
- `v_target_cycle_all_back` (Cycle All Back) — `k`
- `v_target_cycle_friendly_fwd` (Cycle Friendly Fwd) — `u`
- `v_target_cycle_friendly_back` (Cycle Friendly Back) — `j`
- `v_target_toggle_pinned_focused` (Toggle Pinned Focused) — `p`
- `v_target_cycle_pinned_fwd` (Cycle Pinned Fwd) — `o`
- `v_target_cycle_pinned_back` (Cycle Pinned Back) — `l`
- `v_target_cycle_hostile_fwd` (Cycle Hostile Fwd) — `y`
- `v_target_cycle_hostile_back` (Cycle Hostile Back) — `h`
- `v_target_nearest_hostile` (Nearest Hostile) — `t`
- `v_target_cycle_reticle_mode` (Cycle Reticle Mode) — `alt+k`
- `v_target_head_tracking` (Head Tracking) — `alt+r`
- `scan_toggle_mode` (Scan Toggle Mode) — `tab`

## Turret (`spaceship_turret`)

- `v_toggle_weapon_gimbal_lock` (Toggle Weapon Gimbal Lock) — `alt+j`
- `v_target_reticle_focus` (Reticle Focus) — `r`
- `v_target_cycle_all_fwd` (Cycle All Fwd) — `i`
- `v_target_cycle_all_back` (Cycle All Back) — `k`
- `v_target_cycle_friendly_fwd` (Cycle Friendly Fwd) — `u`
- `v_target_cycle_friendly_back` (Cycle Friendly Back) — `j`
- `v_target_toggle_pinned_focused` (Toggle Pinned Focused) — `p`
- `v_target_cycle_hostile_fwd` (Cycle Hostile Fwd) — `y`
- `v_target_cycle_hostile_back` (Cycle Hostile Back) — `h`
- `v_target_nearest_hostile` (Nearest Hostile) — `t`
- `scan_toggle_mode` (Scan Toggle Mode) — `tab`

## Ship — countermeasures / defense (`spaceship_defensive`)

- `v_weapon_launch_countermeasure` (Launch Countermeasure) — `g`
- `v_weapon_launch_countermeasure_cinematic` (Launch Countermeasure Cinematic) — `g`
- `v_weapon_cycle_countermeasure_fwd` (Cycle Countermeasure Fwd) — `1`
- `v_shield_raise_level_forward` (Shield Raise Level Forward) — `np_8`
- `v_shield_raise_level_back` (Shield Raise Level Back) — `np_2`
- `v_shield_raise_level_left` (Shield Raise Level Left) — `np_4`
- `v_shield_raise_level_right` (Shield Raise Level Right) — `np_6`
- `v_shield_raise_level_up` (Shield Raise Level Up) — `np_9`
- `v_shield_raise_level_down` (Shield Raise Level Down) — `np_7`
- `v_shield_reset_level` (Shield Reset Level) — `np_5`

## Ship — power triangle (`spaceship_power`) ⚠

- `v_power_focus_group_1` (Power Focus Group 1) — `f5`
- `v_power_focus_group_2` (Power Focus Group 2) — `f6`
- `v_power_focus_group_3` (Power Focus Group 3) — `f7`
- `v_power_reset_focus` (Power Reset Focus) — `f8`
- `v_power_throttle_up` (Power Throttle Up) — `alt+np_5`
- `v_power_throttle_down` (Power Throttle Down) — `alt+np_4`
- `v_power_throttle_max` (Power Throttle Max) — `alt+np_5` (double-tap)
- `v_power_throttle_min` (Power Throttle Min) — `alt+np_4` (double-tap)
- `v_power_toggle_group_1` (Power Toggle Group 1) — `7`
- `v_power_toggle_group_2` (Power Toggle Group 2) — `6`
- `v_power_toggle_group_3` (Power Toggle Group 3) — `4`
- `v_power_toggle` (Power Toggle) — `u` (4.x override)

## Ship — radar / scanning (`spaceship_radar`)

- `v_radar_toggle_active_or_passive` (Radar Toggle Active Or Passive) — `.`
- `v_radar_cycle_zoom_fwd` (Radar Cycle Zoom Fwd) — `,`

## Ship — HUD / MFD (`spaceship_hud`) ⚠

- `mobiglas` (Mobiglas) — `f1`
- `v_hud_open_scoreboard` (Hud Open Scoreboard) — `f1`
- `v_starmap` (Starmap) — `f2`

## Lights (`lights_controller`)

- `v_lights` (Lights) — `3`

## On-foot — player (`player`)

- `moveleft` (Moveleft) — `a`
- `moveright` (Moveright) — `d`
- `moveforward` (Moveforward) — `w`
- `moveback` (Moveback) — `s`
- `jump` (Jump) — `space`
- `crouch` (Crouch) — `ctrl`
- `prone` (Prone) — `c`
- `sprint` (Sprint) — `shift`
- `grenade` (Grenade) — `g`
- `zoom_out` (Zoom Out) — `scroll down`
- `zoom_in` (Zoom In) — `scroll up`
- `selectpistol` (Selectpistol) — `1`
- `selectprimary` (Selectprimary) — `2`
- `selectsecondary` (Selectsecondary) — `3`
- `selectgadget` (Selectgadget) — `4`
- `reload` (Reload) — `r`
- `holster` (Holster) — `h`
- `stabilize` (Stabilize) — `shift`
- `weapon_change_firemode` (Weapon Change Firemode) — `v`
- `accelerate` (Accelerate) — `shift`
- `decelerate` (Decelerate) — `b`
- `fixed_speed_increment` (Fixed Speed Increment) — `scroll up`
- `fixed_speed_decrement` (Fixed Speed Decrement) — `scroll down`
- `toggle_flashlight` (Toggle Flashlight) — `t`
- `combatheal` (Combatheal) — `x`
- `combathealtarget` (Combathealtarget) — `x`
- `refillgastank` (Refillgastank) — `b`
- `thirdperson` (Thirdperson) — `f4`
- `free_thirdperson_camera` (Free Thirdperson Camera) — `z`
- `mobiglas` (Mobiglas) — `f1`
- `pl_hud_open_scoreboard` (Pl Hud Open Scoreboard) — `f1`
- `scan_toggle_mode` (Scan Toggle Mode) — `tab`
- `v_starmap` (Starmap) — `f2`
- `force_respawn` (Force Respawn) — `alt+backspace`
- `v_eject` (Eject) — `alt+l` (double-tap)
- `v_eject_cinematic` (Eject Cinematic) — `alt+l` (double-tap)
- `nextitem` (Nextitem) — `6`

## On-foot — prone (`prone`)

- `prone_rollleft` (Prone Rollleft) — `a` (2x tap)
- `prone_rollright` (Prone Rollright) — `d` (2x tap)

## EVA — zero-G (`zero_gravity_eva`)

- `eva_roll_left` (Eva Roll Left) — `q`
- `eva_roll_right` (Eva Roll Right) — `e`
- `eva_strafe_up` (Eva Strafe Up) — `space`
- `eva_strafe_down` (Eva Strafe Down) — `ctrl`
- `eva_strafe_left` (Eva Strafe Left) — `a`
- `eva_strafe_right` (Eva Strafe Right) — `d`
- `eva_strafe_forward` (Eva Strafe Forward) — `w`
- `eva_strafe_back` (Eva Strafe Back) — `s`
- `eva_brake` (Eva Brake) — `x`
- `eva_boost` (Eva Boost) — `shift`
- `eva_toggle_headlook_mode` (Eva Toggle Headlook Mode) — `z`

## Ground vehicle — general (`vehicle_general`)

- `v_exit` (Exit) — `alt+f`
- `v_horn` (Horn) — `c`
- `v_view_cycle_fwd` (Cycle Fwd) — `f4`
- `v_view_zoom_in` (Zoom In) — `scroll up`
- `v_view_zoom_out` (Zoom Out) — `scroll down`
- `v_view_look_behind` (Look Behind) — `z`
- `mobiglas` (Mobiglas) — `f1`
- `v_starmap` (Starmap) — `f2`

## Ground vehicle — driver (`vehicle_driver`)

- `v_move_forward` (Move Forward) — `w`
- `v_move_back` (Move Back) — `s`
- `v_yaw_left` (Yaw Left) — `a`
- `v_yaw_right` (Yaw Right) — `d`
- `v_roll_left` (Roll Left) — `q`
- `v_roll_right` (Roll Right) — `e`
- `v_brake` (Brake) — `x`

## Multiplayer (`multiplayer`)

- `respawn` (Respawn) — `x`

## Spectator (`spectator`)

- `spectate_toggle_lock_target` (Spectate Toggle Lock Target) — `y`
- `spectate_zoom_in` (Spectate Zoom In) — `scroll up`
- `spectate_zoom_out` (Spectate Zoom Out) — `scroll down`
- `spectate_toggle_hud` (Spectate Toggle Hud) — `b`
- `spectate_gen_nextmode` (Spectate Gen Nextmode) — `f4`
- `spectate_gen_prevmode` (Spectate Gen Prevmode) — `f5`

## Default / global (`default`)

- `toggle_contact` (Toggle Contact) — `f11`
- `toggle_chat` (Toggle Chat) — `f12`
- `focus_on_chat_textinput` (Focus On Chat Textinput) — `enter`
- `enable_cursor_ui_2d` (Enable Cursor Ui 2D) — `right alt`

## Party / invite (`invite`)

- `menu_friends_accept_invite` (Menu Friends Accept Invite) — `[`
- `menu_friends_refuse_invite` (Menu Friends Refuse Invite) — `]`
- `menu_friends_ignore_invite` (Menu Friends Ignore Invite) — `]`

## Emotes (`player_emotes`)

- `emote_cs_forward` (Emote Cs Forward) — `np_5`
- `emote_cs_left` (Emote Cs Left) — `np_1`
- `emote_cs_right` (Emote Cs Right) — `np_3`
- `emote_cs_stop` (Emote Cs Stop) — `np_2`
- `emote_cs_yes` (Emote Cs Yes) — `np_4`
- `emote_cs_no` (Emote Cs No) — `np_6`

## Player choice (`player_choice`)

- `pc_interaction_mode` (Pc Interaction Mode) — `f`
- `pc_screen_focus_left` (Pc Screen Focus Left) — `a`
- `pc_screen_focus_right` (Pc Screen Focus Right) — `d`
- `pc_screen_focus_up` (Pc Screen Focus Up) — `w`
- `pc_screen_focus_down` (Pc Screen Focus Down) — `s`
- `pc_personal_thought` (Pc Personal Thought) — `tab`

## Director mode (`view_director_mode`)

- `view_enable_camview_mode` (View Enable Camview Mode) — `f4`
- `view_save_view_1` (View Save View 1) — `np_1`
- `view_save_view_2` (View Save View 2) — `np_2`
- `view_save_view_3` (View Save View 3) — `np_3`
- `view_save_view_4` (View Save View 4) — `np_4`
- `view_save_view_5` (View Save View 5) — `np_5`
- `view_save_view_6` (View Save View 6) — `np_6`
- `view_save_view_7` (View Save View 7) — `np_7`
- `view_save_view_8` (View Save View 8) — `np_8`
- `view_save_view_9` (View Save View 9) — `np_9`
- `view_load_view_1` (View Load View 1) — `np_1`
- `view_load_view_2` (View Load View 2) — `np_2`
- `view_load_view_3` (View Load View 3) — `np_3`
- `view_load_view_4` (View Load View 4) — `np_4`
- `view_load_view_5` (View Load View 5) — `np_5`
- `view_load_view_6` (View Load View 6) — `np_6`
- `view_load_view_7` (View Load View 7) — `np_7`
- `view_load_view_8` (View Load View 8) — `np_8`
- `view_load_view_9` (View Load View 9) — `np_9`
- `view_reset_saved` (View Reset Saved) — `np_0`
- `view_move_target_X_pos` (View Move Target X Pos) — `right`
- `view_move_target_X_neg` (View Move Target X Neg) — `left`
- `view_move_target_Y_pos` (View Move Target Y Pos) — `up`
- `view_move_target_Y_neg` (View Move Target Y Neg) — `down`
- `view_move_target_Z_pos` (View Move Target Z Pos) — `page up`
- `view_move_target_Z_neg` (View Move Target Z Neg) — `page down`
- `view_fov_in` (View Fov In) — `num +`
- `view_fov_out` (View Fov Out) — `np_subtract`
- `view_fstop_in` (View Fstop In) — `home`
- `view_fstop_out` (View Fstop Out) — `end`
- `view_restore_defaults` (View Restore Defaults) — `np_multiply`

---
_227 keyboard bindings parsed (1 4.x overrides applied). ⚠ = patch-volatile category — verify with on-screen hints._
