# Configuration

The example in `examples/atom-tc-6tool/` is a complete, working printer
configuration. This page lists what you must adapt and what the important
settings do. Values not mentioned here can usually stay as they are.

## Files

| File | Content |
|---|---|
| `printer.cfg` | Main config: MCUs, motion, bed, includes. Calibrated offsets are stored at the bottom (`SAVE_CONFIG` block) |
| `atom/toolchanger.cfg` | `[toolchanger]` settings and the tool change sequence (pickup in two stages, dropoff, error handling) |
| `atom/T0.cfg` … `T5.cfg` | One file per tool: toolhead MCU, extruder, fans, sensors, dock position, input shaper |
| `atom/toolchanger_macros.cfg` | `TC_INIT`, `SET_INITIAL_TOOL`, `PARK_TOOLHEAD`, `PICKUP_TOOL`, `TOOLCHANGE_DEMO` |
| `atom/tool_calibration.cfg` | NUDGE probe hardware (`[tools_calibrate]`), TAXY, NUDGE and Beacon calibration macros, Z adjust |
| `atom/nudge_ring.cfg` | NUDGE ring calibration |
| `atom/beacon.cfg` | Beacon probe |
| `atom/beacon_diagnostics.cfg` | Thermal compensation, probe and gantry tests |
| `atom/tc_led_effects.cfg`, `atom/knomi.cfg` | LED status and KNOMI displays (optional) |
| `atom/clean_nozzle.cfg` | Nozzle wipe on a silicone wiper |
| `macros.cfg` | `PRINT_START`, `PRINT_END`, toolchanger-aware `PAUSE`/`RESUME`/`CANCEL_PRINT`, filament load/unload |
| `variables.cfg` | Calibration data written by macros (`[save_variables]`) |
| `ouroboros_xy.cfg`, `printer_closedloop_xy.cfg` | Closed-loop X/Y option, see [CLOSED_LOOP_UPGRADE.md](CLOSED_LOOP_UPGRADE.md) |

`macros.cfg` and `printer.cfg` also contain things that only exist on the author's
printer (HelixScreen display, games on the display, bed fans). Remove what you do
not have.

## Must change

1. **MCUs:** `serial` of the main board in `printer.cfg`, `canbus_uuid` of every
   toolhead board in `T<n>.cfg`.
2. **Pins:** heaters, thermistors, fans, detection pins, if your boards differ.
3. **Dock positions:** `params_park_x`, `params_park_y`, `params_park_z` per tool.
4. **NUDGE probe:** `pin` and position in `[tools_calibrate]` and in
   `NUDGE_MOVE_OVER_PROBE`, if you use one.
5. **Fan names** in the calibration macros (`fan0`, `BedFans`), if yours differ.
6. **Calibration values:** delete the author's offsets (the `#*# [tool T<n>]`
   entries at the bottom of `printer.cfg`) and the contents of `variables.cfg`,
   then calibrate your own.

## `[toolchanger]` (atom/toolchanger.cfg)

| Setting | Example | Meaning |
|---|---|---|
| `params_max_tool_count` | 6 | Number of tools |
| `params_safe_y` | 110 | Y position that is safe for moves in X in front of the docks |
| `params_close_y` | 35 | Y position just in front of the docks |
| `params_fast_speed` | 27000 | Travel speed in mm/min. Lower it for the first tests |
| `params_path_speed` | 3000 | Speed of the dock path in mm/min |
| `params_atom_dock_path` | list | Moves in and out of the dock, relative to the dock position |
| `verify_tool_pickup` | true | Check the tool sensor after the first pickup stage |
| `initialize_on` | first-use | Initialise on the first tool command |
| `on_axis_not_homed` | home | Home automatically before a tool change |
| `t_command_restore_axis` | z | Return to the previous Z after a change |

The tool change itself is G-code in `pickup_gcode_stage1`, `pickup_gcode_stage2`,
`dropoff_gcode`, `before_change_gcode`, `after_change_gcode` and `error_gcode`.
Between the two pickup stages the module checks the tool sensor.

## `[tool T<n>]` (atom/T<n>.cfg)

| Setting | Meaning |
|---|---|
| `tool_number`, `extruder` | Tool number and its extruder section |
| `detection_pin` | Tool sensor on the toolhead board, usually with pull-up (`^`) |
| `debounce_delay` | Filter against sensor glitches from vibration (0.1 s) |
| `params_park_x/y/z` | Dock position |
| `params_input_shaper_*` | Input shaper of this tool, applied on every tool change |

XY and Z offsets are not entered by hand; the calibration writes them.

## `[tools_calibrate]` (NUDGE probe)

| Setting | Example | Meaning |
|---|---|---|
| `pin` | `^PG10` | NUDGE probe input |
| `spread` | 4 | Distance from the pin centre where probing starts |
| `lower_z` | 0.5 | How far below the pin top the nozzle probes |
| `speed` / `lift_speed` | 2 / 4 | Probing speeds |
| `samples` | 3 | Samples used for the result |
| `samples_discard` | 1 | Extra samples dropped from each end (outlier filter): 3 + 2 × 1 = 5 probes |
| `samples_result` | median | `median` or `average` |
| `samples_tolerance` | 0.03 | Maximum spread of the samples used |
| `samples_tolerance_retries` | 10 | Retries before giving up |
| `sample_retract_dist` | 2.5 | Retract between samples |

## Checklist before the first print

- [ ] Klipper starts without errors.
- [ ] `DEBUG_TOOL_DETECTION` is correct with an empty shuttle and with every tool.
- [ ] Every tool changes reliably at reduced speed, then at full speed.
- [ ] `PAUSE`/`RESUME` work during a test print.
- [ ] XY, Z and thermal compensation are calibrated ([Calibration](CALIBRATION.md)).
