# Troubleshooting

This document collects common problems when setting up and running
`klipper-toolchanger-extended` and how to diagnose / fix them.

It is organized roughly in the order you will hit issues:

1. Klipper fails to start
2. Tools / boards won’t connect
3. Tool pickup / dropoff problems
4. Tool presence / sensors
5. Calibration macros failing
6. Print / recovery issues
7. Slicer & workflow quirks

Always keep an eye on **`klippy.log`** – it is your best friend when
things go wrong.

---

## 1. Klipper Fails to Start

### 1.1. “Error loading module 'toolchanger_extended'”

**Symptoms:**

- Klipper refuses to start
- Log shows something like:
  - `Error loading module 'toolchanger_extended'`
  - Python import errors

**Possible causes & fixes:**

- The repo was not installed correctly:
  - Re-run:

    ```bash
    cd ~/klipper-toolchanger-extended
    ./install.sh
    ```

  - Make sure the script completes without errors.

- You updated Klipper but not this repo:
  - `git pull` in `klipper-toolchanger-extended`
  - Re-run `./install.sh`
  - Restart Klipper

- Wrong `extra` module path:
  - Check your `klippy.log` for where Klipper expects extras
  - Verify that the symlink created by `install.sh` points there

---

### 1.2. “Error parsing config” / “Unknown section”

**Symptoms:**

- Web UI shows config error
- Log mentions:
  - `Unknown section [toolchanger]`
  - `Unknown command 'SET_TOOL'`
  - Similar

**Possible causes & fixes:**

- You included `toolchanger_macros.cfg` / `T*.cfg` but not `toolchanger.cfg`:
  - Make sure you have:

    ```ini
    [include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger.cfg]
    ```

- Typo in `[include ...]` path:
  - Check path spelling carefully
  - Use the full relative path from your `printer.cfg` location

- Old cached config:
  - Restart Klipper from UI
  - If needed, restart the Klipper service on the host

---

## 2. Tools / Boards Won’t Connect

### 2.1. MCU Not Found / Timeout

**Symptoms:**

- Log shows:
  - `MCU 'tool0' shutdown`
  - `Timeout trying to connect to MCU 'tool0'`
- Temperature reads as `0.0` or `error`

**Possible causes & fixes:**

- Wrong `canbus_uuid` / `serial`:
  - Run `ls /dev/serial/by-id/` (for USB)
  - Use `canbus_query.py` (for CAN)
  - Update each `[mcu toolX]` section in `T*.cfg` accordingly

- Incorrect USB permissions:
  - Compare with your working main MCU
  - Ensure user running Klipper has access to the device

- Board not powered:
  - Check 24V / 12V / 5V supply
  - Verify LEDs on the toolhead boards

---

### 2.2. Temperature / Heater Errors

**Symptoms:**

- `ADC out of range`
- `Heater extruder tool0 not configured`
- `Extruder not heating`

**Possible causes & fixes:**

- Wrong `sensor_type` or `sensor_pin`:
  - Compare with your known-good single-extruder config
  - Make sure you use the same thermistor type and wiring

- Section names mismatch:
  - If your macros expect `extruder tool0`, but your config says `[extruder]` only:
    - Rename the section to match
    - Or adapt the macros

- PID not tuned:
  - Run a PID tune for each toolhead if needed

---

## 3. Tool Pickup / Dropoff Problems

### 3.1. Tool Crashes into Dock

**Symptoms:**

- Nozzle or carriage hits the dock walls
- Dock flexes or tool pops out violently

**Possible causes & fixes:**

- Bad `dock_x`, `dock_y`, `dock_z` values:
  - Manually move to those coordinates with low speed:
    - `G1 X... Y... Z... F600`
  - Adjust until positioning is safe
  - Only then re-test automatic pickup

- Wrong `safe_z`:
  - If `safe_z` is too low, moves over docks may hit hardware
  - Increase `safe_z` in `toolchanger.cfg`

- Acceleration too high:
  - Temporarily reduce:
    ```gcode
    SET_VELOCITY_LIMIT VELOCITY=100 ACCEL=1500
    ```

---

### 3.2. Tool Fails to Engage / Drop

**Symptoms:**

- Tool partially docks but doesn’t lock
- Tool doesn’t drop off completely
- Pickup fails repeatedly

**Possible causes & fixes:**

- Mechanical alignment off:
  - Check that the dock is:
    - Square to the axes
    - At the correct height
    - Firmly mounted (no wobble)
  - Loosen, adjust, re-tighten

- Dock positions slightly off:
  - Use jog controls to find the “sweet spot”
  - Update `dock_x`, `dock_y`, `dock_z` in the relevant `T*.cfg`

- Approach / retract speeds too high:
  - Reduce `dock_speed` in `toolchanger.cfg`
  - Re-test

---

### 3.3. Two-Stage Pickup Fails Repeatedly

**Symptoms:**

- Macro reports:
  - `Tool pickup verification failed`
- Tool may appear correctly mounted but system aborts

<p align="center">
  <img src="images/ATOM-PICKUP_FAILURE_1080.gif" alt="Pickup Failure Recovery" width="600">
  <br>
  <em>Example: Automatic recovery from pickup failure</em>
</p>

**Possible causes & fixes:**

- Tool presence sensor logic inverted:
  - Toggle the `tool_sensor_inverted` parameter
  - Watch sensor state in console during manual attach/detach

- Sensor not wired or broken:
  - Check continuity / wiring
  - Use a multimeter if needed

- Wrong `tool_sensor_pin`:
  - Confirm the actual pin used
  - Update config

---

## 4. Tool Presence / Sensors

### 4.1. False Tool Loss During Printing

**Symptoms:**

- Printer pauses with message like:
  - `Active tool T1 lost - check tool attachment`
- Tool is actually still attached

**Possible causes & fixes:**

- Noisy / bouncing sensor:
  - Increase `tool_presence_timeout` (e.g. 2–3 seconds)
  - Add filtering if possible (hardware or software debounce)

- Loose connector:
  - Check mechanical connection at the board and sensor
  - Re-seat or re-solder as needed

- Wrong logic level:
  - `tool_sensor_inverted` may be wrong
  - Verify sensor’s idle / active levels

---

### 4.2. Tool Sensor Always On or Always Off

**Symptoms:**

- Sensor state never changes, regardless of tool position

**Possible causes & fixes:**

- Pin misconfigured:
  - Check for typos in `tool_sensor_pin`
  - Make sure no other section uses that pin

- Sensor failure or wiring issue:
  - Test sensor stand-alone
  - Check for 5V/24V vs 3.3V compatibility

---

## 5. Calibration Macros Failing

### 5.1. `NUDGE_FIND_TOOL_OFFSETS` Errors

**Symptoms:**

- Macro aborts early
- Error like:
  - `Unknown command 'SET_INITIAL_TOOL'`
  - Or moves don’t make sense

**Possible causes & fixes:**

- `SET_INITIAL_TOOL` not called beforehand:
  - Always start with:
    ```gcode
    SET_INITIAL_TOOL TOOL=0
    ```
  - Replace `0` with your reference tool if different

- Wrong include order:
  - Ensure `toolchanger.cfg` and `toolchanger_macros.cfg` are included
    before any macros that use them

- Dock positions extremely wrong:
  - Make sure coarse dock positions are reasonable first
  - Fix any collisions before running calibration

---

### 5.2. `MEASURE_TOOL_Z_OFFSETS` Errors

**Symptoms:**

- Probing fails
- Macro aborts with probe-related errors

**Possible causes & fixes:**

- Probe not configured or not working:
  - Test probe:
    - `PROBE` / `QUERY_PROBE`
    - Run a standard Z calibration on T0
  - Fix probe first

- Wrong probe offsets:
  - If probe is off by a lot, moves may be unsafe
  - Make sure X/Y probe offset is roughly correct

- Tools not fully seated:
  - A loose tool will give inconsistent Z offsets
  - Fix mechanical issues before calibration

---

## 6. Print & Recovery Issues

### 6.1. Resume Puts Nozzle in Wrong Place

**Symptoms:**

- After `RESUME`, nozzle:
  - Comes back to an incorrect XY position
  - Scrapes the print

**Possible causes & fixes:**

- Incomplete state restoration:
  - Check your `PAUSE` / `RESUME` macros
  - Make sure they:
    - Save the current position
    - Restore it before resuming
  - Compare with reference macros in `toolchanger_macros.cfg`

- Manual intervention without re-sync:
  - If you manually jog or change tools during a pause:
    - Use the provided recovery macros to re-sync
    - Or re-home and carefully restart the job

---

### 6.2. Heater Shut Down on Tool Loss (Expected but Surprising)

**Symptoms:**

- A tool is reported lost
- Its heater is turned off automatically

<p align="center">
  <img src="images/ATOM-TOOL_LOSS_720.gif" alt="Tool Loss Detection and Recovery" width="600">
  <br>
  <em>Example: Automatic detection and recovery from tool loss during print</em>
</p>

**Explanation:**

- This is an intentional safety feature:
  - If a tool is no longer attached, heating it can be dangerous
  - The system shuts off the heater to avoid damage or fire risk

**What to do:**

1. Fix the mechanical issue (reattach tool, tighten screws, etc.)
2. Re-run:
   - Tool pickup & verification
   - Any needed calibration
3. Restart the print or use recovery macros if appropriate

---

### 6.3. Random Emergency Stops

**Symptoms:**

- Printer halts with Klipper shutdown
- Messages about MCU errors, stepper shutdown, etc.

**Possible causes & fixes:**

- Not specific to this fork – treat as usual Klipper issues:
  - Power instability
  - Overcurrent / stepper driver errors
  - Temperature faults
  - USB / CAN dropouts

Fix these first, then re-test toolchanger behavior.

---

## 7. Slicer & Workflow Issues

### 7.1. Slicer Uses Its Own Toolchange G-Code

**Symptoms:**

- Slicer injects custom toolchange macros
- Conflicts with fork’s `T0` … `Tn` macros
- Unexpected behavior between tool changes

**Fix:**

- Configure slicer to:
  - Use **plain `T0`, `T1`, …`** for tool changes  
  - Call your central `PRINT_START` / `PRINT_END` macros
  - Avoid per-toolchange custom G-code (leave it to the fork’s macros)

---

### 7.2. First Tool Not Selected at Print Start

**Symptoms:**

- Print starts with no tool mounted
- Or wrong tool used for first layer

**Fix:**

- In your `PRINT_START` macro:
  - Explicitly select a tool, e.g.:

    ```gcode
    T0
    ```

  - Or set the initial tool based on slicer variable if you use one

- Make sure your slicer:
  - Either always starts with T0
  - Or you handle first tool selection in `PRINT_START`

---

### 7.3. Different Temperatures Per Tool Not Honored

**Symptoms:**

- All tools use the same temperature
- Slicer settings per tool appear ignored

**Possible causes & fixes:**

- Single `extruder` section used in slicer profile:
  - Ensure your slicer:
    - Has one extruder definition per tool
    - Sends temperatures to the correct extruder / tool

- Macro interference:
  - Check `PRINT_START` / `TOOLCHANGE` macros for hard-coded temps
  - Replace them with slicer-provided values or per-tool logic

---

## 8. General Debugging Tips

- Always test **one tool at a time** before full multi-tool runs.
- Start with:
  - Homing
  - Manual moves
  - Dry toolchanges (cool bed, no filament)
- Only then add:
  - Calibration
  - Real prints

When stuck:

1. Re-read the relevant section of:
   - `QUICKSTART.md`
   - `CONFIGURATION.md`
   - `CALIBRATION.md`
2. Check `klippy.log` for the **first error**, not the last line.
3. Simplify:
   - Disable non-essential features temporarily
   - Test a minimal scenario
4. Reintroduce complexity step by step.

Once the basics are stable, the extended safety and recovery features will
give you a much more forgiving and robust toolchanger experience.
