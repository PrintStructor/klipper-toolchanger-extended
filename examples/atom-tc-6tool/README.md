# ATOM TC 6-Tool Example Configuration

## Overview
Complete working configuration for a 6-tool VORON toolchanger using the ATOM dock system.

## Hardware
- **Toolheads**: 6x BTT EBB36/42 CAN toolheads
- **Dock System**: ATOM docks (simple 4-point pickup/dropoff path)
- **Probe**: Beacon RevH (eddy current, contact + proximity modes)
- **XY Calibration**: NUDGE physical probe
- **Z Calibration**: Beacon contact detection
- **Tool Detection**: Per-tool microswitches

## Files Included

### Core Configuration
- `toolchanger.cfg` - Main toolchanger logic, dock paths, tool change sequences
- `toolchanger_macros.cfg` - Global variables, initial tool setup, utilities
- `calibrate_offsets.cfg` - XY (NUDGE) and Z (Beacon) offset calibration
- `beacon.cfg` - Beacon probe configuration, sensorless homing helpers

### Tool Definitions
- `T0.cfg` through `T5.cfg` - Individual tool configurations
  - CAN MCU settings
  - Extruder & TMC drivers
  - Fans & sensors
  - Per-tool parameters (park positions, input shaper, offsets)

## Quick Start

### 1. Installation
```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger.git
cd klipper-toolchanger
./install.sh
```

### 2. Configuration
Copy these example configs to your `printer.cfg`:
```ini
[include klipper-toolchanger/examples/atom-tc-6tool/toolchanger.cfg]
[include klipper-toolchanger/examples/atom-tc-6tool/toolchanger_macros.cfg]
[include klipper-toolchanger/examples/atom-tc-6tool/calibrate_offsets.cfg]
[include klipper-toolchanger/examples/atom-tc-6tool/beacon.cfg]
[include klipper-toolchanger/examples/atom-tc-6tool/T0.cfg]
[include klipper-toolchanger/examples/atom-tc-6tool/T1.cfg]
# ... T2-T5
```

### 3. Customize for Your Machine
**CRITICAL** - Update these values before use:
- Dock positions: `params_park_x/y/z` in each T*.cfg
- Safe Y positions: `params_safe_y` and `params_close_y` in toolchanger.cfg
- CAN UUIDs: `canbus_uuid` in each T*.cfg
- Beacon offset: `x_offset` and `y_offset` in beacon.cfg
- NUDGE position: `NUDGE_MOVE_OVER_PROBE` coordinates in calibrate_offsets.cfg

### 4. Calibration Workflow
```
# 1. Set initial tool
SET_INITIAL_TOOL TOOL=0

# 2. Calibrate XY offsets (all tools relative to T0)
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0

# 3. Calibrate Z offsets (all tools relative to T0)
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0

# 4. Save results
SAVE_CONFIG
```

## Key Features

### Two-Stage Pickup
- Stage 1: Insert until verification point, verify tool presence
- Stage 2: Complete insertion only if verification succeeds
- Prevents crashes if tool didn't dock properly

### Rounded Paths
- Uses `ROUNDED_G0` for smooth curved movements
- Reduces mechanical stress and improves reliability

### Z-Offset Management
- T0 as reference (offset = 0)
- All other tools have relative Z-offsets
- `global_z_offset` applied to initial tool for Beacon compensation

### Safety Features
- Tool presence monitoring during prints
- Automatic pause if tool drops
- Z-stepper current boost during tool changes
- Error handling with safe Z-lift

## Important Commands

### Tool Selection
```
T0-T5                    # Select tool
SET_INITIAL_TOOL TOOL=0  # Set reference tool before printing
```

### Calibration
```
NUDGE_FIND_TOOL_OFFSETS  # XY offset calibration
MEASURE_TOOL_Z_OFFSETS   # Z offset calibration
```

### Testing
```
TOOLCHANGE_DEMO          # 20 random tool changes (testing)
```

## Dock Path Configuration

Current ATOM dock path (4 points):
```python
params_atom_dock_path: [
    {'y':9, 'z':1},           # Approach position
    {'y':8, 'z':0.5, 'f':0.5}, # Verification point (tool detected here)
    {'y':0, 'z':0.5},          # Engage position
    {'y':0, 'z':-10}           # Final park position
]
```

The `'f':0.5` parameter marks the verification point where tool presence is checked.

## Notes

### Speeds
- Fast travel: 450 mm/s (27000 mm/min)
- Dock path: 50 mm/s (3000 mm/min)
- Reduce for testing or if experiencing crashes

### Input Shaper
Per-tool configuration supported - each tool can have unique resonance settings.

### Extruder Temperature Control
Enhanced M104/M109 macros support per-tool temperatures:
```gcode
M104 T0 S220  # Set T0 to 220°C
M109 T2 S245  # Heat T2 to 245°C and wait
```

## Troubleshooting

### Tool Detection Fails
- Check detection pin wiring
- Verify `detection_pin` in T*.cfg
- Test with `QUERY_ENDSTOPS`

### Dock Position Misalignment
- Manually move to each dock and note positions
- Update `params_park_x/y/z` in T*.cfg
- Verify Z is high enough to clear all tools

### XY Offset Calibration Issues
- Heat nozzles to 180°C for consistent thermal expansion
- Ensure NUDGE probe is at correct height
- Check `spread` parameter if probe triggers too early

## Credits
Based on [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)

Modified and enhanced by **PrintStructor**
