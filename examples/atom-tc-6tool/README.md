# VORON Toolchanger - 6-Tool ATOM Reference Configuration

**Author:** PrintStructor  
**Version:** 1.0.0  
**Hardware:** VORON 2.4 with 6-tool ATOM dock system

---

## ⚠️ CRITICAL: This is a Real-World Working Configuration

**READ THIS BEFORE USING:**

This configuration contains **MY actual machine values** - including:
- ✋ **CAN UUIDs** - Unique to my EBB boards
- 📐 **Dock positions** - Specific to my physical dock locations  
- 🎯 **Calibrated offsets** - XY/Z offsets tuned for my machine
- 🔧 **Input shaper values** - Resonance frequencies for my frame
- 🌡️ **PID values** - Temperature control tuned for my hotends

**YOU MUST CHANGE THESE VALUES FOR YOUR MACHINE!**

### What You MUST Update:

1. **CAN UUIDs** (in every T0-T5.cfg):
   ```ini
   [mcu et0]
   canbus_uuid: XXXXXXXX  # ← Replace with YOUR board's UUID
   ```
   Find yours with: `~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0`

2. **Dock Positions** (in every T0-T5.cfg):
   ```ini
   params_park_x: 25.3    # ← Your dock X position
   params_park_y: 3.0     # ← Your dock Y position  
   params_park_z: 325.0   # ← Safe Z height for your machine
   ```

3. **Calibrate ALL Offsets** (don't use my values):
   ```gcode
   NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0  # XY offsets
   MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0   # Z offsets
   SAVE_CONFIG
   ```

4. **Run PID Tuning** (per tool):
   ```gcode
   PID_CALIBRATE HEATER=extruder TARGET=260
   PID_CALIBRATE HEATER=extruder1 TARGET=260
   # ... etc for all tools
   ```

**This is a REFERENCE showing what a complete, working config looks like.**  
**Treat it as a template - adjust everything to match YOUR hardware!**

---

## Configuration Overview

This is a complete reference configuration for 6-tool VORON printers using ATOM toolheads.

### Safety Features
- **Two-Stage Tool Pickup** - Verifies tool presence before completing pickup
- **Error Recovery** - Pauses print instead of emergency stop when recoverable errors occur
- **Tool Presence Monitoring** - Detects tool loss during printing and pauses safely
- **Position Restoration** - Automatically restores print position and temperature after recovery

### Key Capabilities
- **Per-Tool Input Shaper** - Individual resonance compensation for each toolhead
- **Automated Calibration** - NUDGE probe for XY offsets, Beacon contact for Z offsets
- **Rounded Motion Paths** - Smooth curved movements for reduced mechanical stress
- **LED Status Visualization** - Real-time feedback via chamber and tool LEDs
- **KNOMI Display Integration** - Smart sleep/wake control for BTT displays

### Hardware Design
This configuration is built for ATOM toolheads (custom-designed by Alex at APDMachine, creator of the Reaper Toolhead) integrated with VORON 2.4 printers.

---

## Hardware Configuration

### Toolchanger System
- **Docks:** 6x ATOM docks (simple 4-point path)
- **Detection:** Filament switch sensors per tool
- **Motion:** Rounded path module for smooth movements

### Toolheads (T0-T5)
- **Boards:** BTT EBB36/42 CAN per tool
- **Extruders:** Moons CSE14HRA1L410A with TMC2209
- **Hotends:** ATC Semitec 104GT-2 thermistors
- **Cooling:** Individual hotend fans + shared CPAP part cooling
- **LEDs:** 3x per tool (1x RGBW logo + 2x RGB nozzle sequins)
- **Displays:** BTT KNOMI round displays (optional)

### Probing System
- **XY Calibration:** NUDGE probe (physical contact)
- **Z Calibration:** Beacon RevH (eddy current + contact mode)
- **Homing:** Sensorless XY, Beacon Z

### Additional Hardware
- **Chamber LEDs:** 64x RGB Neopixels
- **Z-Axis:** Quad gantry with 4x TMC5160 steppers
- **Control Board:** Compatible with RP2040/RP2350

---

## File Structure

### Core Toolchanger Files

```
atom-tc-6tool/
├── toolchanger.cfg              # Main toolchanger config
├── toolchanger_macros.cfg       # Core operation macros
├── calibrate_offsets.cfg        # NUDGE & Beacon calibration
├── macros.cfg                   # Print lifecycle macros
└── README.md                    # This file
```

**toolchanger.cfg:**
- Rounded path module
- Toolchanger core settings (6 tools, ATOM paths)
- Two-stage pickup/dropoff sequences
- Error handling
- M104/M109 temperature overrides

**toolchanger_macros.cfg:**
- Global variables (offsets, state)
- SET_INITIAL_TOOL macro
- Filament sensor control
- Tool presence monitoring
- Recovery macros

**macros.cfg:**
- PRINT_START / PRINT_END
- Pause / Resume / Cancel handling
- Quad Gantry Leveling
- Utility functions

**calibrate_offsets.cfg:**
- NUDGE probe configuration
- XY offset calibration workflow
- Beacon-based Z offset measurement
- Shell scripts for auto-save

### Tool Configurations

```
atom-tc-6tool/
├── T0.cfg                       # Tool 0 (Extruder 0)
├── T1.cfg                       # Tool 1 (Extruder 1)
├── T2.cfg                       # Tool 2 (Extruder 2)
├── T3.cfg                       # Tool 3 (Extruder 3)
├── T4.cfg                       # Tool 4 (Extruder 4)
└── T5.cfg                       # Tool 5 (Extruder 5)
```

Each tool config includes:
- CAN MCU configuration (`canbus_uuid`)
- Extruder & TMC2209 settings
- Heater verification
- Fans (hotend + part cooling references)
- Filament sensors
- Tool macro (T0-T5 command)
- Tool parameters (park position, offsets, input shaper)

### Hardware Integration (Optional)

```
atom-tc-6tool/
├── beacon.cfg                   # Beacon probe + bed mesh
├── tc_led_effects.cfg          # LED status visualization
└── knomi.cfg                   # KNOMI display sleep/wake
```

---

## Quick Start

### 1. Installation

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended
./install.sh
```

### 2. Configuration

Copy these example configs to your `printer.cfg`:

```ini
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger_macros.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/macros.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/calibrate_offsets.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/beacon.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/T0.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/T1.cfg]
# ... T2-T5
```

### 3. Customize for Your Machine

**⚠️ CRITICAL** - Update these values before use:

1. **Dock positions** - `params_park_x/y/z` in each T*.cfg
2. **Safe Y positions** - `params_safe_y` and `params_close_y` in toolchanger.cfg
3. **CAN UUIDs** - `canbus_uuid` in each T*.cfg
4. **Beacon offset** - `x_offset` and `y_offset` in beacon.cfg
5. **NUDGE position** - `NUDGE_MOVE_OVER_PROBE` coordinates in calibrate_offsets.cfg

**Find CAN UUIDs:**
```bash
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

### 4. Initialize Toolchanger

```gcode
G28                              # Home all axes
SET_INITIAL_TOOL TOOL=0          # Set T0 as reference
```

### 5. Calibration Workflow

**XY Offset Calibration (NUDGE):**
```gcode
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
SAVE_CONFIG
```

**Z Offset Calibration (Beacon):**
```gcode
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
# Auto-saved via shell scripts
```

**Adjust Global Z-Offset:**
```gcode
# Fine-tune after first layer test (typical: 0.06-0.12mm)
SET_GCODE_VARIABLE MACRO=globals VARIABLE=global_z_offset VALUE=0.06
```

### 6. First Print

```gcode
PRINT_START BED_TEMP=110 TOOL_TEMP=240 INITIAL_TOOL=0
# ... your print gcode ...
PRINT_END
```

---

## Configuration Details

### Tool Parking Positions

**ATOM Dock Layout (Example):**
```
Tool  | Park X | Park Y | Park Z
------|--------|--------|-------
T0    | 25.3   | 3.0    | 325.0
T1    | 85.9   | 3.0    | 325.0
T2    | 145.9  | 3.0    | 325.0
T3    | 206.0  | 3.0    | 325.0
T4    | 266.1  | 3.0    | 325.0
T5    | 326.0  | 3.0    | 325.0
```

*Note: These are example values - update in each TX.cfg to match your dock positions.*

### Movement Parameters

```ini
params_safe_y: 105           # Safe Y for horizontal moves
params_close_y: 35           # Y close to dock area
params_fast_speed: 27000     # 450 mm/s travel speed
params_path_speed: 3000      # 50 mm/s docking speed
```

### ATOM Dock Path

**4-point path with verification:**
```python
[{'y':9, 'z':1},              # Approach
 {'y':8, 'z':0.5, 'f':0.5},   # Verify (f=0.5 marks verification point)
 {'y':0, 'z':0.5},            # Insert
 {'y':0, 'z':-10}]            # Lock
```

The `'f':0.5` parameter marks where tool detection verification occurs during Stage 1 pickup.

### Offset System

**Three types of offsets:**

1. **Global Z-Offset** (`globals.global_z_offset`)
   - Applied to initial tool only
   - Compensates for nozzle height variation
   - Typical: 0.06-0.12mm

2. **Relative XY-Offsets** (per tool)
   - Example: `t1_xy_offset: -0.022, 0.091`
   - Auto-calibrated via NUDGE probe
   - Relative to initial tool

3. **Relative Z-Offsets** (per tool)
   - Example: `t1_z_offset: -0.10512`
   - Auto-calibrated via Beacon contact
   - Relative to initial tool

**Important:** The initial tool always has XY=0,0 and relative Z=0.00.

---

## Safety Features Explained

### Two-Stage Tool Pickup

**Stage 1: Approach & Verify**
1. Moves to dock and partially inserts tool
2. Stops at verification point (marked with `'f'` in path)
3. Checks tool detection sensor
4. If tool not detected → Error, pause print

**Stage 2: Complete Pickup** (only if verification succeeds)
1. Completes insertion path
2. Returns to safe position
3. Restores previous print position

**Why This Matters:**
- Prevents crashes from false tool detection
- Catches mechanical issues before full insertion
- Allows safe recovery if pickup fails

### Tool Presence Monitoring

During printing, the system continuously monitors the active tool:

```gcode
# Automatically started by PRINT_START
UPDATE_DELAYED_GCODE ID=TOOL_PRESENCE_MONITOR DURATION=2.0
```

**If tool drops:**
1. 🚨 Print pauses immediately
2. 🔥 Heater turns off (safety)
3. 💡 LED status shows ERROR
4. ⚙️ Temperature saved for recovery
5. 👤 User fixes issue and runs RESUME

### Error Recovery

**Scenario:** Tool change fails mid-print

**Automatic Response:**
1. Print pauses automatically
2. Z-axis lifts to safe height
3. LED status shows error (red)
4. Extruder heater turns off

**Manual Recovery:**
1. Fix mechanical issue (reseat tool, clear obstruction, etc.)
2. Run `RESUME` command
3. System automatically:
   - Restores previous temperature
   - Returns to exact print position
   - Continues printing

---

## Troubleshooting

### Tool Detection Fails

**Symptoms:** Tool not detected during pickup

**Solutions:**
1. Check detection sensor: `QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor`
2. Verify dock alignment (mechanical check)
3. Slow down path speed for testing:
   ```ini
   params_path_speed: 300  # 5 mm/s for debugging
   ```
4. Verify `'f'` verification point in dock path

### Offset Drift

**Symptoms:** Tools print at wrong XY positions

**Solutions:**
1. Verify initial tool is set: `SET_INITIAL_TOOL TOOL=0`
2. Re-calibrate XY offsets: `NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0`
3. Check NUDGE probe position hasn't moved
4. Verify mechanical alignment of docks

### Z-Height Inconsistent

**Symptoms:** First layer height varies between tools

**Solutions:**
1. Verify Beacon calibration: `BEACON_CALIBRATE`
2. Re-measure Z offsets: `MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0`
3. Check global_z_offset value
4. Ensure bed mesh is current: `BED_MESH_CALIBRATE ADAPTIVE=1`

### LED Effects Not Working

**Symptoms:** Chamber/tool LEDs stay off or wrong colors

**Solutions:**
1. Check LED power supply
2. Verify LED chain counts match hardware
3. Test individual effect: `SET_LED_EFFECT EFFECT=rainbow_nature`
4. Check pin mappings in `tc_led_effects.cfg`

### KNOMI Displays Won't Wake

**Symptoms:** Displays stay sleeping after activity

**Solutions:**
1. Check network connectivity: `ping knomi-t0.local`
2. Verify firmware v3.0+
3. Manual wake: `KNOMI_WAKE`
4. Check status: `CHECK_KNOMI_STATUS`

---

## Advanced Features

### Per-Tool Input Shaper

Each tool can have individual resonance compensation:

```ini
[tool T0]
params_input_shaper_type_x: 'ei'
params_input_shaper_freq_x: 79.8
params_input_shaper_damping_ratio_x: 0.069
params_input_shaper_type_y: 'mzv'
params_input_shaper_freq_y: 42.6
params_input_shaper_damping_ratio_y: 0.055
```

**Tuning:** Run `SHAPER_CALIBRATE` with T5 active (equipped with ADXL345).

### Chamber LED Sequences

**Startup:** Knight Rider animation → Tool pairs → Rainbow  
**Printing:** Tool logo shows temperature, chamber shows bed temp  
**Complete:** Green blink → Temperature display → Fade to ready

### Enhanced M-Code Support

```gcode
M104 T0 S220        # Set T0 to 220°C
M109 T2 S245        # Heat T2 to 245°C and wait
M106 T1 S255        # Tool 1 part cooling fan full speed
```

---

## Maintenance

### Regular Checks

**Weekly:**
- Clean NUDGE probe contact surface
- Verify tool detection sensors
- Check dock alignment

**Monthly:**
- Re-calibrate XY offsets if drift observed
- Verify Z-offset consistency across tools
- Clean Beacon probe surface

**As Needed:**
- Re-run Input Shaper calibration after mechanical changes
- Update global_z_offset for new nozzles/bed surfaces
- Adjust path speeds if reliability issues occur

### Backup Configuration

```bash
# Backup entire config directory
tar -czf ~/config_backup_$(date +%Y%m%d).tar.gz ~/printer_data/config/

# Backup just toolchanger configs
tar -czf ~/toolchanger_backup_$(date +%Y%m%d).tar.gz ~/printer_data/config/atom/
```

---

## Important Commands Reference

### Tool Selection & Setup
```gcode
T0-T5                           # Select tool
SET_INITIAL_TOOL TOOL=0         # Set reference tool before printing
INITIALIZE_TOOLCHANGER          # Manual initialization
```

### Calibration
```gcode
NUDGE_FIND_TOOL_OFFSETS         # XY offset calibration
MEASURE_TOOL_Z_OFFSETS          # Z offset calibration
NUDGE_MOVE_OVER_PROBE           # Position over NUDGE for testing
```

### Status & LED Control
```gcode
STATUS_READY                    # Ready state (rainbow)
STATUS_PRINTING TOOL=X          # Printing state
STATUS_HEATING                  # Heating state
STATUS_PART_READY               # Completion sequence
SET_LED_EFFECT EFFECT=name      # Set specific effect
STOP_LED_EFFECTS                # Turn off all
```

### KNOMI Display Control
```gcode
KNOMI_WAKE                      # Wake displays
KNOMI_SLEEP                     # Sleep displays
CHECK_KNOMI_STATUS              # Show status
```

### Testing & Debug
```gcode
TOOLCHANGE_DEMO                 # 20 random tool changes
DEBUG_TOOL_DETECTION            # Display detection status
```

---

## Files to Customize

**Must Configure:**
1. **TX.cfg** - Update `canbus_uuid` and `params_park_*` positions
2. **toolchanger.cfg** - Adjust `params_safe_y`, `params_close_y`, speeds
3. **calibrate_offsets.cfg** - Update NUDGE position in `NUDGE_MOVE_OVER_PROBE`
4. **toolchanger_macros.cfg** - Set `global_z_offset` after calibration

**Optional:**
5. **beacon.cfg** - Update `home_xy_position` and mesh parameters
6. **tc_led_effects.cfg** - Customize LED effects and colors
7. **knomi.cfg** - Configure display wake/sleep behavior

---

## Related Documentation

- **Main Project Repository:** [github.com/PrintStructor/klipper-toolchanger-extended](https://github.com/PrintStructor/klipper-toolchanger-extended)
- **OrcaSlicer Setup Guide:** `ORCASLICER_SETUP.md` (in this directory)
- **Python Module Documentation:** See `/docs/` directory
- **Klipper Configuration Reference:** [klipper3d.org/Config_Reference.html](https://www.klipper3d.org/Config_Reference.html)

---

## Credits

**ATOM Toolhead System:**  
Custom-designed by Alex at APDMachine (creator of the Reaper Toolhead) for this toolchanger project.

**Base Toolchanger Framework:**  
[viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) by Viesturs Zarins

**NUDGE Probe:**  
[zruncho3d/nudge](https://github.com/zruncho3d/nudge) by Zruncho

**Enhanced Configuration & Safety Features:**  
PrintStructor - [github.com/PrintStructor](https://github.com/PrintStructor)

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**License:** GPL-3.0