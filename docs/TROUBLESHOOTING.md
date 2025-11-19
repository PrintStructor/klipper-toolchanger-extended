# 🚨 Troubleshooting Guide

**Comprehensive problem diagnosis and solutions**

---

## 📋 Table of Contents

1. [Diagnosis Flowchart](#diagnosis-flowchart)
2. [By Symptom](#by-symptom)
3. [By Component](#by-component)
4. [Error Messages](#error-messages)
5. [Log Analysis](#log-analysis)
6. [Getting Support](#getting-support)

---

## Diagnosis Flowchart

```
[Problem Occurred]
       ↓
Does Klipper start?
  NO → See: Klipper Won't Start
  YES → Continue
       ↓
Is toolchanger initialized?
  NO → See: Toolchanger Not Initialized
  YES → Continue
       ↓
Does tool detection work?
  NO → See: Tool Detection Issues
  YES → Continue
       ↓
Do tool changes complete?
  NO → See: Tool Change Failures
  YES → Continue
       ↓
Are offsets correct?
  NO → See: Offset Problems
  YES → System Working!
```

---

## By Symptom

### 🔴 Klipper Won't Start

#### Symptom
- Mainsail/Fluidd shows "Klipper not connected"
- Red "Disconnected" status
- No response to commands

#### Common Causes

**1. Python Module Import Errors**

Check log:
```bash
tail -50 ~/printer_data/logs/klippy.log | grep -i error
```

**Solution:**
```bash
# Re-run installation
cd ~/klipper-toolchanger-extended
./install.sh
sudo systemctl restart klipper
```

**2. Configuration Syntax Errors**

**Symptoms in log:**
```
Option 'invalid_param' is not valid in section 'toolchanger'
```

**Solution:**
- Review recent config changes
- Comment out suspicious sections
- Restart Klipper after each change
- Check spelling of parameter names

**3. Missing Include Files**

**Symptoms:**
```
Unable to open config file '/path/to/file.cfg'
```

**Solution:**
- Verify file path is correct
- Check file exists: `ls -la /path/to/file.cfg`
- Fix path or create missing file

---

### 🟠 Toolchanger Not Initialized

#### Symptom
- Error: "Toolchanger not initialized"
- `T0`, `T1` commands not available
- `QUERY_TOOLCHANGER` shows "uninitialized"

#### Diagnosis

```gcode
QUERY_TOOLCHANGER
```

**Expected output:**
```
toolchanger status: ready
tool: T0
tool_number: 0
```

**If shows "uninitialized":**

#### Solutions

**1. Manual Initialization**

```gcode
SET_INITIAL_TOOL TOOL=0
```

**2. Check Initialization Settings**

```ini
[toolchanger]
initialize_on: first-use    # or 'home' or 'manual'
```

**3. Verify Tools Are Configured**

```gcode
# Should show multiple tools
QUERY_TOOLCHANGER
```

If only 1 tool shown, check:
- At least 2 tool configs included
- Tool numbers are unique
- No syntax errors in tool configs

---

### 🟡 Tool Detection Issues

#### Symptom
- "Tool not detected" errors
- Tool pickup fails verification
- Detection sensor not responding

#### Diagnosis Steps

**Step 1: Query Sensor Directly**

```gcode
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
```

**Expected:**
- With tool: `filament_detected: True`
- Without tool: `filament_detected: False`

**Step 2: If Inverted (opposite of expected)**

**Solution:**
```ini
# In TX.cfg, toggle pin inversion
detection_pin: !T0:PG11    # Add ! if missing
# or
detection_pin: T0:PG11     # Remove ! if present
```

**Step 3: If No Response / Always Same**

**Check wiring:**
- Continuity test with multimeter
- Verify pin number in config matches board
- Check crimps and connectors

**Check pin configuration:**
```ini
detection_pin: ^T0:PG11    # ^ = pullup
detection_pin: !T0:PG11    # ! = inverted
detection_pin: ^!T0:PG11   # Both
```

**Test manually:**
```bash
# Monitor pin state in real-time
# In Klipper console, watch:
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
# Manually trigger sensor, observe changes
```

---

### 🔵 Tool Change Failures

#### Symptom
- Tool gets stuck during pickup/dropoff
- Crashes into dock or other objects
- "Tool change aborted" errors

#### Diagnosis by Stage

**Stage 1: Before Movement**

**Error:** "Axis not homed"

**Solution:**
```gcode
G28    # Home all axes
```

Or set auto-home:
```ini
[toolchanger]
on_axis_not_homed: home
```

---

**Stage 2: During Dropoff**

**Error:** Tool doesn't release properly

**Causes:**
- Incorrect dock position
- Path issues
- Mechanical binding

**Solution:**
1. **Verify dock position:**
   ```gcode
   # Manually jog to dock
   G0 X{park_x} Y{park_y} Z{park_z} F1000
   # Should be perfectly aligned
   ```

2. **Reduce speed for testing:**
   ```ini
   params_path_speed: 300    # Very slow (5mm/s)
   ```

3. **Check path definition:**
   ```python
   # In toolchanger.cfg
   # Example: ATOM 4-point path
   [{'y':9, 'z':1},           # Approach
    {'y':8, 'z':0.5, 'f':0.5}, # Verify point
    {'y':0, 'z':0.5},         # Insert
    {'y':0, 'z':-10}]         # Lock
   ```

---

**Stage 3: During Pickup**

**Error:** "Probe triggered prior to movement"

**Meaning:** Tool detection triggered before pickup started

**Causes:**
1. Tool sensor not actually empty (tool stuck)
2. Sensor wiring short
3. Pin configuration inverted

**Solution:**
```gcode
# 1. Verify sensor reads False without tool
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor

# 2. If reads True when empty, invert pin
# In TX.cfg:
detection_pin: !T0:PG11    # Add !

# 3. Check for mechanical issues
# Manually remove tool completely
# Clean dock area
```

---

**Error:** "Tool not detected after pickup"

**Meaning:** Verification failed (Two-Stage Pickup)

**Causes:**
1. Tool not fully inserted
2. Sensor not triggering
3. Path doesn't reach verification point

**Solution:**

1. **Check path has verification point:**
   ```python
   {'y':8, 'z':0.5, 'f':0.5}  # The 'f':0.5 marks verification
   ```

2. **Test sensor at verification position:**
   ```gcode
   # Move to verification position manually
   G0 X{park_x} Y8 Z{park_z+0.5}
   QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
   # Should read True
   ```

3. **Adjust verification position:**
   - Move 'f' earlier if triggering late
   - Move 'f' later if triggering early

---

### 🟢 Offset Problems

#### Symptom
- Tools print at wrong XY positions
- Z-height inconsistent between tools
- Layer shifts when switching tools

#### XY Offset Issues

**Diagnosis:**

```gcode
# Print a test object with multiple tools
# Check if features align properly
```

**Causes:**

**1. Initial tool not set**

**Solution:**
```gcode
SET_INITIAL_TOOL TOOL=0
# Must run before calibration and before each print
```

**2. Offsets not calibrated**

**Solution:**
```gcode
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
SAVE_CONFIG
```

**3. Offsets drifting over time**

**Causes:**
- Mechanical loosening (check bolts)
- Dock position changed
- Probe moved

**Solution:**
- Tighten all mechanical connections
- Re-calibrate: `NUDGE_FIND_TOOL_OFFSETS`
- Run weekly offset verification

**4. Nozzles not clean during calibration**

**Effect:** Offsets contain errors from debris

**Solution:**
- Clean all nozzles thoroughly
- Heat and wipe with brass brush
- Re-calibrate with clean nozzles

---

#### Z-Offset Issues

**Diagnosis:**

```gcode
# Print first layer with different tools
# Check if height varies between tools
```

**Symptoms:**
- First layer too high with some tools
- First layer too low with others
- Inconsistent squish

**Solutions:**

**1. Re-calibrate Z-offsets**

```gcode
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
```

**2. Check Beacon probe calibration**

```gcode
BEACON_CALIBRATE
```

**3. Adjust global Z-offset**

```gcode
# Fine-tune first layer height for initial tool
SET_GCODE_VARIABLE MACRO=globals VARIABLE=global_z_offset VALUE=0.08
SAVE_CONFIG
```

**Typical values:** 0.06 - 0.12mm

**4. Verify bed mesh is current**

```gcode
BED_MESH_CALIBRATE
# Or for adaptive:
BED_MESH_CALIBRATE ADAPTIVE=1
```

---

### 🟣 CAN-Bus Problems

#### Symptom
- Tools not found
- "MCU connection timeout"
- Intermittent disconnections

#### Diagnosis

**1. Query CAN-bus:**

```bash
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

**Expected:** Shows all tool MCUs

**2. Check CAN interface:**

```bash
ip link show can0
```

**Expected:** Shows "UP" state

**If down:**
```bash
sudo ip link set can0 up type can bitrate 500000
```

#### Common Issues

**1. Wrong UUID in config**

**Symptom:** MCU not found after UUID changes

**Solution:**
```bash
# Find current UUIDs
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0

# Update in TX.cfg
[mcu TX]
canbus_uuid: YOUR_NEW_UUID_HERE
```

**2. CAN termination resistor**

**Symptom:** Unreliable communication, random disconnects

**Solution:**
- Verify 120Ω termination at both ends of CAN bus
- Use multimeter to check resistance between CANH and CANL
- Should read ~60Ω with bus powered off

**3. CAN bus too long**

**Symptom:** Errors increase with distance

**Solution:**
- Keep CAN runs under 5 meters for 500kbps
- Use twisted pair cable
- Reduce bitrate if longer runs needed:
  ```bash
  sudo ip link set can0 type can bitrate 250000
  ```

**4. Electrical noise**

**Symptom:** Random errors, especially during heater cycles

**Solution:**
- Route CAN cables away from heater wires
- Add ferrite beads to CAN cable
- Ensure proper grounding

---

### 🔴 LED Effects Not Working

#### Symptom
- LEDs stay off
- Wrong colors displayed
- Effects don't change

#### Diagnosis

**1. Check LED power:**
- Verify 5V power supply
- Check current capacity (60mA per LED)
- Test with multimeter

**2. Test individual LED:**

```gcode
SET_LED LED=chamber_leds RED=1.0 GREEN=0 BLUE=0 INDEX=1
```

**If no response:**
- Check data pin connection
- Verify LED type in config (WS2812, SK6812, etc.)
- Test with different index

**3. Check LED chain counts:**

```ini
[neopixel chamber_leds]
pin: PB0
chain_count: 64    # ← Must match physical LED count
```

**4. Verify LED effects installed:**

```bash
ls -la ~/printer_data/config/ | grep led
```

**Should see:** `tc_led_effects.cfg` or similar

---

### 🟡 KNOMI Display Issues

#### Symptom
- Displays won't wake
- No connection to display
- Firmware version errors

#### Diagnosis

**1. Check network connectivity:**

```bash
ping knomi-t0.local
ping knomi-t1.local
# etc for each display
```

**2. Verify firmware version:**

KNOMI firmware v3.0+ required for sleep/wake features

**3. Test manual wake:**

```gcode
KNOMI_WAKE
```

**4. Check status:**

```gcode
CHECK_KNOMI_STATUS
```

#### Solutions

**1. Update KNOMI firmware:**
- Follow BTT instructions for firmware update
- Use v3.0 or newer

**2. Configure static IP:**
- Prevents hostname resolution issues
- Edit `knomi.cfg` with IP instead of hostname

**3. Increase timeout:**

```ini
[gcode_macro KNOMI_WAKE]
variable_timeout: 5    # Increase if slow network
```

---

## By Component

### Toolchanger Core Module

**Check module loaded:**

```bash
ls ~/klipper/klippy/extras/ | grep tool
```

**Should see:**
- `toolchanger.py`
- `tool.py`
- `tools_calibrate.py`
- etc.

**If missing:**
```bash
cd ~/klipper-toolchanger-extended
./install.sh
sudo systemctl restart klipper
```

---

### NUDGE Probe

**Common issues:**

**1. "Probe triggered prior to movement"**

**Cause:** Nozzle already touching probe

**Solution:**
- Increase starting height
- Check `lower_z` parameter
- Verify probe isn't too tall

**2. Inconsistent results**

**Cause:** Dirty nozzle or probe

**Solution:**
- Clean nozzle with brass brush
- Clean probe contact surface
- Re-run calibration

**3. "Probe did not trigger"**

**Cause:** Not making contact

**Solution:**
- Increase `lower_z` parameter
- Reduce `spread` if too far from center
- Check probe wiring

---

### Beacon Probe

**Common issues:**

**1. "Beacon not responding"**

**Check connection:**
```gcode
BEACON_QUERY
```

**2. Contact mode not working**

**Verify calibration:**
```gcode
BEACON_CALIBRATE
```

**3. Z-offsets inaccurate**

**Re-calibrate contact threshold:**
```gcode
BEACON_CALIBRATE
# Then re-measure tool offsets
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
```

---

### Input Shaper (Per-Tool)

**Issue:** Input shaper not applying per tool

**Check `after_change_gcode`:**

```ini
[toolchanger]
after_change_gcode:
    {% if tool.params_input_shaper_freq_x %}
        SET_INPUT_SHAPER SHAPER_FREQ_X={tool.params_input_shaper_freq_x}
    {% endif %}
```

**Verify it's being called:**
```gcode
# After tool change, check:
GET_INPUT_SHAPER
# Should match tool's parameters
```

---

## Error Messages

### "Toolchanger not initialized"

**Meaning:** Toolchanger system needs initialization

**Solution:**
```gcode
SET_INITIAL_TOOL TOOL=0
```

---

### "Tool X not found"

**Meaning:** Requested tool number not configured

**Check:**
- Tool file included in printer.cfg?
- `tool_number` parameter set correctly?
- No duplicate tool numbers?

---

### "Axis not homed"

**Meaning:** Required axes not homed before tool change

**Solution:**
```gcode
G28    # Home all axes
```

---

### "Tool not detected after pickup"

**Meaning:** Two-stage pickup verification failed

**Causes:**
1. Tool not fully seated
2. Detection sensor not working
3. Path doesn't reach verification point

**See:** [Tool Change Failures](#tool-change-failures)

---

### "Move out of range"

**Meaning:** Requested position outside printer limits

**Check:**
- Dock positions within printer bounds?
- `position_max` in stepper config sufficient?
- Z-height adequate for tool changes?

**Solution:**
```ini
# Increase limits if needed
[stepper_x]
position_max: 350    # Increase if needed

[stepper_z]
position_max: 340    # Must clear tools at full height
```

---

## Log Analysis

### Reading klippy.log

**View recent errors:**
```bash
tail -100 ~/printer_data/logs/klippy.log | grep -i error
```

**View toolchanger activity:**
```bash
tail -100 ~/printer_data/logs/klippy.log | grep -i tool
```

**Watch live log:**
```bash
tail -f ~/printer_data/logs/klippy.log
```

---

### Key Log Patterns

**Normal tool change:**
```
Toolchanger: Dropping off tool T0
Toolchanger: Picking up tool T1
Toolchanger: Tool change complete
```

**Detection failure:**
```
Tool T1: Detection failed - tool not detected
Toolchanger: Two-stage pickup verification failed
```

**Path execution:**
```
Tool T1: Executing pickup path
Tool T1: Path point: X=25.3 Y=9.0 Z=326.0
Tool T1: Path point: X=25.3 Y=8.0 Z=325.5 (verify)
Tool T1: Verification passed
```

---

### Common Log Errors

**"Option 'parameter_name' in section 'section' must be specified"**

**Meaning:** Required parameter missing

**Solution:** Add the missing parameter to config

---

**"Unable to parse option 'parameter_name' in section 'section'"**

**Meaning:** Invalid value format

**Solution:** Check value syntax (quotes, numbers, etc.)

---

**"Unknown command: COMMAND_NAME"**

**Meaning:** Command not defined or module not loaded

**Solution:**
- Check spelling
- Verify module installed
- Ensure macro defined

---

## Getting Support

### Before Asking for Help

Gather this information:

1. **System Info:**
   ```bash
   # Klipper version
   cd ~/klipper && git log -1 --oneline
   
   # Toolchanger version
   cd ~/klipper-toolchanger-extended && git log -1 --oneline
   ```

2. **Configuration:**
   - Your `toolchanger.cfg`
   - One tool config (TX.cfg)
   - Relevant sections of `printer.cfg`

3. **Logs:**
   ```bash
   # Last 200 lines of log with errors
   tail -200 ~/printer_data/logs/klippy.log | grep -B5 -A5 -i error > ~/error_log.txt
   ```

4. **Behavior:**
   - Exact error message
   - What you expected to happen
   - What actually happened
   - Steps to reproduce

---

### Where to Get Help

**GitHub Issues:**
- Bug reports: [New Issue](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)
- Use provided template
- Include all gathered information

**GitHub Discussions:**
- General questions: [Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)
- Configuration help
- Tips and tricks

**Discord/Community:**
- Real-time chat (if available)
- Quick questions
- Community experience sharing

---

### Useful Commands for Support

```bash
# System info
uname -a
python3 --version

# Klipper status
sudo systemctl status klipper

# Config backup
tar -czf ~/config_backup.tar.gz ~/printer_data/config/

# Full log
cat ~/printer_data/logs/klippy.log | tail -500 > ~/klippy_full.log

# CAN bus status
ip link show can0
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

---

## Quick Reference: Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Not initialized | `SET_INITIAL_TOOL TOOL=0` |
| Wrong detection | Toggle `!` on `detection_pin` |
| Offsets wrong | `NUDGE_FIND_TOOL_OFFSETS` |
| Z-height off | `MEASURE_TOOL_Z_OFFSETS` |
| Tool stuck | Reduce `params_path_speed` |
| CAN timeout | Check UUIDs, termination |
| Axis not homed | `G28` |
| LED not working | Check power, chain_count |

---

## Related Documentation

- [**Quick Start Guide**](QUICKSTART.md) - Initial setup
- [**Configuration Guide**](CONFIGURATION.md) - Parameter reference
- [**Calibration Guide**](CALIBRATION.md) - Calibration procedures
- [**FAQ**](FAQ.md) - Common questions

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**License:** GPL-3.0
