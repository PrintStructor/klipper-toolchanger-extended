# VORON Toolchanger Configuration - 6-Tool ATOM Setup

**Author:** PrintStructor  
**Version:** 3.1  
**Hardware:** VORON 2.4 with 6-tool ATOM dock system

---

## Overview

This directory contains a complete, production-ready configuration for a 6-tool VORON toolchanger using ATOM-style docks. The setup includes advanced features like LED status visualization, KNOMI display integration, and Beacon probe-based calibration.

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
- **Displays:** BTT KNOMI round displays

### Probing System
- **XY Calibration:** NUDGE probe (physical contact)
- **Z Calibration:** Beacon RevH (eddy current + contact mode)
- **Homing:** Sensorless XY, Beacon Z

### Additional Hardware
- **Chamber LEDs:** 64x RGB Neopixels
- **Z-Axis:** Quad gantry with 4x TMC5160 steppers
- **Control Board:** RP2350 with status LED

---

## File Structure

### Core Toolchanger Files

```
atom/
├── toolchanger.cfg              # Main toolchanger config
├── toolchanger_macros.cfg       # Core operation macros
├── calibrate_offsets.cfg        # NUDGE & Beacon calibration
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

**calibrate_offsets.cfg:**
- NUDGE probe configuration
- XY offset calibration workflow
- Beacon-based Z offset measurement
- Shell scripts for auto-save

### Tool Configurations

```
atom/
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

### Hardware Integration

```
atom/
├── beacon.cfg                   # Beacon probe + bed mesh
├── tc_led_effects.cfg          # LED status visualization
└── knomi.cfg                   # KNOMI display sleep/wake
```

**beacon.cfg:**
- Beacon RevH hardware config
- Sensorless XY homing with TMC current adjustment
- Bed mesh (21x21 points, bicubic interpolation)
- Homing helper macros

**tc_led_effects.cfg:**
- 7 sections covering all LED effects
- Hardware definitions (toolheads + chamber)
- Status effects (ready, printing, heating, etc.)
- Temperature visualization
- Startup/shutdown sequences

**knomi.cfg:**
- Hardware sleep mode control (300mA → 50mA)
- HTTP API integration (mDNS)
- Automatic wake on activity
- G-code command overrides

---

## Quick Start

### 1. Initial Setup

**Set CAN UUIDs:**
```bash
# Find your EBB board UUIDs
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

Edit each `TX.cfg` file and update:
```ini
[mcu etX]
canbus_uuid: YOUR_UUID_HERE
```

**Verify NUDGE & Beacon:**
```gcode
QUERY_PROBE                    # Check Beacon
NUDGE_MOVE_OVER_PROBE         # Test NUDGE position
```

### 2. Initialize Toolchanger

```gcode
; Home axes
G28

; Initialize with T0 as reference tool
SET_INITIAL_TOOL TOOL=0
```

### 3. Calibrate Offsets

**XY Calibration (NUDGE):**
```gcode
; Heat all tools to 180°C and measure XY offsets
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0

; Save to config
SAVE_CONFIG
```

**Z Calibration (Beacon):**
```gcode
; Measure Z differences between tools
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0

; Offsets auto-saved via shell scripts
```

**Set Global Z-Offset:**
```gcode
; Adjust global offset for your nozzle height
; Typical range: 0.06-0.12mm
SET_GCODE_VARIABLE MACRO=globals VARIABLE=global_z_offset VALUE=0.06
```

### 4. Test Tool Changes

```gcode
T0  ; Select T0
T1  ; Switch to T1
T2  ; Switch to T2
; etc.
```

### 5. First Print

```gcode
PRINT_START BED_TEMP=110 TOOL_TEMP=240 INITIAL_TOOL=0
; ... your print gcode ...
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

*Note: Update these values in each TX.cfg to match your dock positions.*

### Movement Parameters

**toolchanger.cfg:**
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
 {'y':8, 'z':0.5, 'f':0.5},   # Verify (f=0.5 marks this point)
 {'y':0, 'z':0.5},            # Insert
 {'y':0, 'z':-10}]            # Lock
```

The `'f':0.5` marker indicates where tool detection verification occurs during Stage 1 pickup.

### Offset System

**Three types of offsets:**

1. **Global Z-Offset** (`globals.global_z_offset`)
   - Applied to initial tool only
   - Compensates for nozzle height
   - Typical: 0.06-0.12mm

2. **Relative XY-Offsets** (per tool, stored in initial tool config)
   - Example: `t1_xy_offset: -0.022, 0.091`
   - Auto-calibrated via NUDGE probe
   - Relative to initial tool

3. **Relative Z-Offsets** (per tool, stored in initial tool config)
   - Example: `t1_z_offset: -0.10512`
   - Auto-calibrated via Beacon contact
   - Relative to initial tool

**Important:** The initial tool always has XY=0,0 and relative Z=0.00.

---

## Calibration Workflow

### XY Offset Calibration (NUDGE)

**Requirements:**
- NUDGE probe installed and positioned
- All tools accessible

**Procedure:**
```gcode
1. SET_INITIAL_TOOL TOOL=0
2. NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
3. Wait for completion (~15 minutes)
4. SAVE_CONFIG
```

**What it does:**
- Heats each tool to 180°C
- Measures XY position relative to NUDGE pin
- Calculates offsets relative to initial tool
- Saves to `[tool T0]` config section

### Z Offset Calibration (Beacon)

**Requirements:**
- Beacon calibrated
- XY offsets already calibrated

**Procedure:**
```gcode
1. SET_INITIAL_TOOL TOOL=0
2. MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
3. Wait for completion (~15 minutes)
4. Check results (auto-saved via shell scripts)
```

**What it does:**
- Heats each tool to 180°C
- Uses Beacon contact mode to measure nozzle height
- Calculates Z difference from initial tool
- Auto-saves via shell scripts (no manual SAVE_CONFIG needed)

### Adjusting Global Z-Offset

After first layer test:
```gcode
; If first layer too high → increase
SET_GCODE_VARIABLE MACRO=globals VARIABLE=global_z_offset VALUE=0.08

; If first layer too low → decrease
SET_GCODE_VARIABLE MACRO=globals VARIABLE=global_z_offset VALUE=0.04

; Apply to current print
SET_INITIAL_TOOL TOOL=0
```

---

## Troubleshooting

### Tool Change Fails

**Symptoms:** Tool not detected during pickup

**Solutions:**
1. Check detection sensor: `QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor`
2. Verify dock alignment (mechanical check)
3. Slow down path speed for testing:
   ```ini
   params_path_speed: 300  ; 5 mm/s for debugging
   ```
4. Check `'f'` verification point in dock path

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
5. Reset if needed: `KNOMI_RESET`

---

## Advanced Features

### Tool Presence Monitoring

Automatically monitors active tool during printing:

```gcode
; Started by PRINT_START
UPDATE_DELAYED_GCODE ID=TOOL_PRESENCE_MONITOR DURATION=2.0
```

**Behavior:**
- Checks detect_state every 2 seconds
- If tool drops → pause + turn off heater
- LED status shows ERROR
- User can fix issue and RESUME

### Error Recovery

**Scenario:** Tool change fails mid-print

**Steps:**
1. Print automatically pauses
2. LED status shows error (red)
3. Manually fix issue (reseat tool, etc.)
4. Resume printing: `RESUME`
   - Previous temperature restored
   - Position restored automatically
   - Print continues

### Per-Tool Input Shaper

Each tool has individual resonance compensation:

```ini
[tool T0]
params_input_shaper_type_x: 'ei'
params_input_shaper_freq_x: 79.8
params_input_shaper_damping_ratio_x: 0.069
params_input_shaper_type_y: 'mzv'
params_input_shaper_freq_y: 42.6
params_input_shaper_damping_ratio_y: 0.055
```

**Tuning:** Run `SHAPER_CALIBRATE` with T5 active (has ADXL345).

### Chamber LED Sequences

**Startup:** Knight Rider animation → Tool pairs → Rainbow
**Printing:** Tool logo shows temperature, chamber shows bed temp
**Complete:** Green blink → Temperature display → Fade to ready

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

## Reference

### Key Macros

```gcode
; Setup
SET_INITIAL_TOOL TOOL=X           ; Set reference tool
INITIALIZE_TOOLCHANGER            ; Manual initialization

; Tool Selection
T0, T1, T2, T3, T4, T5           ; Select tool

; Calibration
NUDGE_FIND_TOOL_OFFSETS          ; XY calibration
MEASURE_TOOL_Z_OFFSETS           ; Z calibration
NUDGE_MOVE_OVER_PROBE            ; Position over NUDGE

; Status
STATUS_READY                      ; Ready state (rainbow)
STATUS_PRINTING TOOL=X            ; Printing state
STATUS_HEATING                    ; Heating state
STATUS_PART_READY                 ; Completion sequence

; LED Control
SET_LED_EFFECT EFFECT=name        ; Set specific effect
STOP_LED_EFFECTS                  ; Turn off all

; KNOMI
KNOMI_WAKE                        ; Wake displays
KNOMI_SLEEP                       ; Sleep displays
CHECK_KNOMI_STATUS                ; Show status
```

### Important Files to Customize

1. **TX.cfg** - Update `canbus_uuid` and `params_park_*`
2. **toolchanger.cfg** - Adjust `params_safe_y`, `params_close_y`, speeds
3. **calibrate_offsets.cfg** - Update NUDGE position in `NUDGE_MOVE_OVER_PROBE`
4. **toolchanger_macros.cfg** - Set `global_z_offset`
5. **beacon.cfg** - Update `home_xy_position` and mesh parameters

---

## Related Documentation

- **Main Project:** `/home/pi/klipper-toolchanger/README.md`
- **OrcaSlicer Setup:** `ORCASLICER_SETUP.md` (in this directory)
- **Klipper Docs:** https://www.klipper3d.org/Config_Reference.html

---

**Version:** 3.1  
**Last Updated:** 2025-11-16  
**Author:** PrintStructor
