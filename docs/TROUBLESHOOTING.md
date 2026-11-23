# Troubleshooting

Start with these two commands; they answer most questions:

```gcode
DEBUG_TOOL_DETECTION     # what Klipper thinks is mounted vs. what the sensors see
SHOW_TOOL_Z_ADJUSTMENTS  # current Z adjustments of all tools
```

Toolchanger errors appear as red lines starting with `!! Toolchanger Error:` in the
Mainsail/Fluidd console. The full log is `~/printer_data/logs/klippy.log`.

---

## Tool changes

### "Tool state mismatch: Klipper expects T0, sensors report none. Nothing was moved."

Klipper's idea of the mounted tool differs from the sensors, typically because a
tool was taken off or put on by hand. As a safety measure no tool change runs
in this state: otherwise the printer would try to dock an empty shuttle into an
occupied dock, or pick up a tool with another one still attached.

Fix:

1. Check the shuttle: is the right tool on it, or none?
2. `DEBUG_TOOL_DETECTION`: `Detected Tool` must match reality. If it shows a tool
   although the shuttle is empty, a sensor is stuck or pressed.
3. `INITIALIZE_TOOLCHANGER`: takes over the state from the sensors. With an empty
   shuttle it reports `Shuttle reported empty, clearing stale state of tool T<n>`.
4. Start the tool change again. With an empty shuttle the next pickup runs gently
   (`Empty shuttle: gentle pickup of tool T<n>`).

During a print this error pauses the print; outside a print it only reports.

### "Tool pickup verification failed (stage1)"

The tool sensor did not report the tool after the first pickup stage. The print
pauses, the tool temperature is saved, and the console shows recovery steps:

1. Attach the tool to the shuttle by hand.
2. Move to the safe Y position shown in the message (`G0 Y<safe_y> F6000`).
3. `RESUME`: heats the tool back up and continues.

If this happens often: check the dock position of this tool (`params_park_x/y/z`
in `T<n>.cfg`), the dock mounting and the sensor.

### "Tool mismatch: expected T2, detected T3"

A different tool than requested was picked up. Usually a tool sits in the wrong
dock. Put it back, run `INITIALIZE_TOOLCHANGER`, then continue.

### "Multiple tools detected"

More than one detection sensor is active. A sensor is stuck, or a docked tool
presses on its switch. Check with `DEBUG_TOOL_DETECTION` which ones report
`detect_state: 1`.

### Tool hits the dock

- Move to the dock position by hand, slowly (`G1 X.. Y.. Z.. F600`), and correct
  `params_park_x/y/z` of this tool.
- Lower `params_fast_speed` and `params_path_speed` in `toolchanger.cfg` while
  testing.
- Check that the dock is square and does not wobble.

### Toolchanger stays in ERROR state

`INITIALIZE_TOOLCHANGER` resets it. `INITIALIZE_TOOLCHANGER RECOVER=1` additionally
moves back to the position before the error (only with a tool mounted).

---

## Tool detection

### Print pauses with "Tool lost" although the tool is attached

The sensor flickered. Check the connector and the wiring at the toolhead board.
`debounce_delay` in `[tool T<n>]` (default in the example: 0.1 s) filters short
glitches from vibration.

### Sensor never changes

Check the pin name in `detection_pin` and whether the pull-up (`^`) is needed.
Test by hand: put the tool on, `DEBUG_TOOL_DETECTION`, take it off, run it again.

---

## Calibration

### "Probe samples exceed samples_tolerance" (NUDGE)

The contact points scatter more than `samples_tolerance` in `[tools_calibrate]`.

- Clean the nozzle; unload filament for calibration runs.
- Check that the NUDGE pin moves freely and springs back.
- With `samples_discard: 1` a single outlier is already ignored; repeated failures
  point to a real problem, not bad luck.

### NUDGE measurement goes wrong, nozzle is stuck on the pin

Hot filament residue can stick to the pin and drag it along. The calibration
macros therefore run the part fan at 25 % and the bed fans at 100 % while probing.
If you changed the fan names, adapt `SET_FAN_SPEED` in the NUDGE macros.

### Ring calibration saves nothing

- `Ring adjust: missing measurements`: a measurement failed. Repeat the run.
- Ring closure above `MAX_CLOSURE`: the measurements do not fit together. Run
  `FIRMWARE_RESTART`, check probe and nozzles, repeat. Do not simply raise the limit.

### Offsets are suddenly several millimetres

Never print with them. Typical causes: wrong reference tool, a loose tool, probe
problem. Restore the previous values from a `printer-<date>.cfg` backup (written
by every `SAVE_CONFIG`) or with `NUDGE_RESTORE_OFFSETS SAVE=1`, then find the cause.

### First layer differs between tools

1. Check the thermal compensation: `SHOW_NOZZLE_TEMP_OFFSET`. A coefficient of 0
   means this tool is not calibrated yet.
2. Repeat the Z calibration of this tool with a clean nozzle.
3. For small differences use babystepping (`SET_TOOL_Z_ADJUST`) and save it.

---

## Klipper does not start

- `Section 'toolchanger' is not a valid config section`: the Python modules
  are not linked. Run `./install.sh` again and check
  `ls -l ~/klipper/klippy/extras/toolchanger.py`.
- `Unknown command` for a macro: an `[include]` is missing or the path is wrong.
- Timeout to a toolhead MCU: wrong `canbus_uuid` (find it with
  `~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0`) or no power on
  the toolhead board.

---

## Getting help

Open an issue with the Klipper version, the relevant config files, the console
output and what you expected to happen.
