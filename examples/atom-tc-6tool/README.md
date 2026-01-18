# ATOM TC-6 Example Configuration

This directory contains a complete, production-tested configuration for a 6-tool VORON 2.4 printer equipped with ATOM toolheads.

---

## Overview

**Hardware:**
- VORON 2.4 350mm CoreXY printer
- 6× ATOM toolheads (~236g each with extruder)
- Lightweight shuttle (~52g) with CPAP cooling
- Beacon RevH probe for Z-offset calibration
- USB camera for kTAMV XY calibration
- CAN bus communication (EBB36/42 boards)
- Per-tool filament sensors
- LED status effects (chamber + per-tool)

**Software Features:**
- Two-stage tool pickup with verification
- Continuous tool presence monitoring
- Pause-based error recovery
- Per-tool Z babystepping
- Nozzle thermal expansion compensation
- Batch calibration (XY + Z for all tools)
- kTAMV camera-based XY calibration (enhanced fork)

---

## File Structure

```
atom-tc-6tool/
├── README.md                    ← You are here
├── CALIBRATION_GUIDE.md         ← Step-by-step calibration workflow
├── printer.cfg                  ← Main printer config
├── macros.cfg                   ← High-level user macros (PRINT_START, etc.)
├── ktamv-macros.cfg             ← kTAMV integration macros
├── mainsail.cfg                 ← Mainsail UI integration
├── variables.cfg                ← Persistent variables (offsets, coefficients)
├── crowsnest.conf               ← Camera configuration for kTAMV
└── atom/                        ← Toolchanger-specific configs
    ├── toolchanger.cfg          ← Core toolchanger setup
    ├── toolchanger_macros.cfg   ← Pickup/dropoff/recovery macros
    ├── tool_calibration.cfg     ← Calibration workflows (XY/Z/Thermal)
    ├── T0.cfg … T5.cfg          ← Individual tool definitions
    ├── beacon.cfg               ← Beacon probe configuration
    ├── beacon_diagnostics.cfg   ← Thermal compensation & diagnostics
    ├── knomi.cfg                ← KNOMI display integration (optional)
    └── tc_led_effects.cfg       ← LED status effects
```

---

## Quick Start

### Prerequisites

1. **Hardware assembled and wired**
   - All 6 tools installed in docks
   - Tool detection sensors working
   - Beacon probe mounted on shuttle
   - USB camera installed and focused

2. **Required Klipper extensions installed:**
   - [kTAMV (Enhanced Fork)](https://github.com/PrintStructor/kTAMV)
   - [Beacon Klipper](https://github.com/beacon3d/beacon_klipper)
   - [klipper-toolchanger-extended](https://github.com/PrintStructor/klipper-toolchanger-extended)

3. **Recommended extensions:**
   - [Shake&Tune](https://github.com/Frix-x/klippain-shaketune)
   - [Klipper LED Effect](https://github.com/julianschill/klipper-led_effect)

### Installation

**Option 1: Use existing installation (via installer)**

The `install.sh` script copies these configs to:
```
~/printer_data/config/ATOM-toolchanger-examples/
```

You can then include them from your `printer.cfg`:
```ini
[include ATOM-toolchanger-examples/atom/toolchanger.cfg]
[include ATOM-toolchanger-examples/atom/toolchanger_macros.cfg]
# ... etc
```

**Option 2: Manual copy**

```bash
cd ~/printer_data/config
cp -r ~/klipper-toolchanger-extended/examples/atom-tc-6tool atom-config
```

Then include from `printer.cfg`:
```ini
[include atom-config/atom/toolchanger.cfg]
[include atom-config/atom/toolchanger_macros.cfg]
# ... etc
```

**Option 3: Symlink (advanced)**

```bash
cd ~/printer_data/config
ln -s ~/klipper-toolchanger-extended/examples/atom-tc-6tool atom-config
```

Symlinks allow pulling updates via git, but edits affect the repo.

---

## Configuration Steps

### 1. Adjust Hardware-Specific Values

**Critical values to customize in `atom/toolchanger.cfg`:**

```ini
[toolchanger]
max_tool_count: 6                    # Number of tools
initialize_on: manual                # When to initialize
require_tool_present: True           # Safety check

[gcode_macro globals]
variable_global_z_offset: 0.00       # Base Z-offset (usually 0 with thermal comp)
```

**Per-tool configs (`atom/T0.cfg` … `T5.cfg`):**

```ini
[tool T0]
tool_number: 0
extruder: extruder                   # Extruder name
fan: multi_fan T0_partfan            # Part cooling fan
zone: 210,50,300,150                 # Safe zone coordinates

# Pickup/dropoff positions (MUST BE ADJUSTED TO YOUR PRINTER!)
pickup_position: 3.0,347.5           # Dock entry position
dropoff_position: 3.0,347.5          # Dock exit position
```

**Test pickup/dropoff positions manually before running macros!**

### 2. Configure Camera (kTAMV)

Edit `crowsnest.conf`:
```ini
[cam nozzle]
mode: camera-streamer
resolution: 1280x720                 # High res for accuracy
max_fps: 15                          # Smooth preview
device: /dev/video0                  # USB camera device
```

Restart crowsnest: `sudo systemctl restart crowsnest`

Verify camera at: `http://your-printer-ip/webcam2/`

### 3. Configure Beacon Probe

Edit `atom/beacon.cfg`:
```ini
[beacon]
serial: /dev/serial/by-id/usb-Beacon_...   # Your Beacon serial
x_offset: 0                          # Beacon X offset from nozzle
y_offset: 22                         # Beacon Y offset from nozzle
mesh_main_direction: x
mesh_runs: 2
```

Calibrate Beacon:
```gcode
BEACON_CALIBRATE
```

### 4. Test Tool Detection

```gcode
G28
INITIALIZE_TOOLCHANGER

# Manually test each tool
SELECT_TOOL T=0
SELECT_TOOL T=1
# ... etc
```

Check console for detection messages.

### 5. Run Calibration

See **[CALIBRATION_GUIDE.md](CALIBRATION_GUIDE.md)** for complete workflow.

**Summary:**
```gcode
# 1. Camera calibration
KTAMV_CALIB_CAMERA

# 2. XY offset calibration (all tools)
KTAMV_CALIBRATE_ALL_TOOLS_XY

# 3. Z offset calibration (all tools)
BEACON_CALIBRATE_ALL_TOOLS_Z

# 4. Thermal expansion calibration (per tool)
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0
# ... repeat for T1-T5
```

---

## Key Features Explained

### Two-Stage Tool Pickup

Standard pickup is risky - if detection fails, the tool may not be properly seated.

**This config uses two-stage pickup:**
1. **Approach** - Move to dock, partial engagement
2. **Verify** - Check tool detection sensor
3. **Complete** - Full engagement if verification passes
4. **Abort** - Keep current tool if verification fails

Configured in `atom/toolchanger_macros.cfg`:
```ini
[gcode_macro _TOOL_PICKUP_STAGE_2]
# Verification logic between stages
```

### Thermal Expansion Compensation

Nozzles expand when heated, changing Z-offset by ~0.5-0.7µm per °C.

**Example:**
- Calibration at 150°C
- Printing at 270°C
- Temperature delta: 120°C
- Expansion: ~68µm (0.068mm)

**Automatic compensation** in PRINT_START:
```gcode
APPLY_NOZZLE_TEMP_OFFSET TOOL={initial_tool}
```

Calibrate once per tool:
```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0
```

Coefficients stored in `variables.cfg`:
```ini
nozzle_expansion_coefficient_t0 = 0.00057
```

See: [THERMAL_COMPENSATION.md](../../docs/THERMAL_COMPENSATION.md)

### Per-Tool Z Babystepping

Adjust Z-offset live during printing without recalibration:

```gcode
# Adjust current tool
SET_TOOL_Z_ADJUST Z=+0.02

# Adjust specific tool
SET_TOOL_Z_ADJUST TOOL=2 Z=-0.01

# Adjust all tools equally
GLOBAL_Z_ADJUST Z=+0.01

# Save when satisfied
SAVE_TOOL_Z_ADJUSTMENTS
```

Adjustments are RAM-based until saved.

### Batch Calibration

Calibrate all tools in one run instead of manually doing each:

**XY Calibration (requires kTAMV):**
```gcode
KTAMV_CALIBRATE_ALL_TOOLS_XY
```
- Each tool becomes initial tool
- Measures all other tools relative to it
- 6 × 5 = 30 XY offset measurements
- Full offset matrix for redundancy

**Z Calibration (requires Beacon):**
```gcode
BEACON_CALIBRATE_ALL_TOOLS_Z
```
- Each tool becomes initial tool
- Measures all other tools relative to it
- 6 × 5 = 30 Z-offset measurements
- Averages for maximum accuracy

**Time:** ~2-3 hours for both XY + Z batch calibration

### LED Status Effects

Visual feedback during toolchanger operations:

- **STATUS_READY** - Idle state (white)
- **STATUS_HEATING** - Tool heating (orange)
- **STATUS_PRINTING** - Active printing (green)
- **STATUS_ERROR** - Error state (red flashing)
- **STATUS_KTAMV** - kTAMV calibration (chamber OFF, nozzle RED)

Configured in `atom/tc_led_effects.cfg`

---

## Macros Reference

### Print Lifecycle

```gcode
PRINT_START BED_TEMP=110 TOOL_TEMP=240 INITIAL_TOOL=0
# - Heats bed and tool
# - Homes all axes
# - Quad gantry leveling
# - Adaptive bed mesh
# - Applies thermal compensation
# - Prime line

PRINT_END
# - Parks toolhead
# - Turns off heaters
# - Disables motors
# - Checks for unsaved Z-adjustments

PAUSE
# - Pauses print
# - Parks toolhead
# - Keeps tool attached

RESUME
# - Resumes print
# - Restores position
```

### Tool Selection

```gcode
T0  # Select T0 (can also use T1, T2, etc.)
SELECT_TOOL T=2  # Alternative syntax
SET_INITIAL_TOOL TOOL=0  # Set reference tool
```

### Calibration

```gcode
# Camera calibration
KTAMV_CALIB_CAMERA

# XY calibration (single tool as reference)
KTAMV_CALIBRATE_XY INITIAL_TOOL=0

# XY calibration (full matrix)
KTAMV_CALIBRATE_ALL_TOOLS_XY

# Z calibration (single tool as reference)
BEACON_CALIBRATE_Z INITIAL_TOOL=0

# Z calibration (full matrix)
BEACON_CALIBRATE_ALL_TOOLS_Z

# Thermal calibration (per tool)
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0
```

### Live Adjustments

```gcode
# Per-tool Z adjustment
SET_TOOL_Z_ADJUST Z=+0.02
SET_TOOL_Z_ADJUST TOOL=3 Z=-0.01
SET_TOOL_Z_ADJUST TOOL=2 RESET=1

# Global Z adjustment
GLOBAL_Z_ADJUST Z=+0.01
GLOBAL_Z_ADJUST RESET=1

# Show adjustments
SHOW_TOOL_Z_ADJUSTMENTS

# Save to config
SAVE_TOOL_Z_ADJUSTMENTS
```

### Thermal Compensation

```gcode
# Apply thermal offset (automatic in PRINT_START)
APPLY_NOZZLE_TEMP_OFFSET

# Clear thermal offset
CLEAR_NOZZLE_TEMP_OFFSET
```

---

## Troubleshooting

### Tools Not Detected

**Check:**
- Tool detection sensor wiring
- Sensor in config: `mcu_tool_map: 0:shuttle,1:t0,2:t1,...`
- Manual sensor test: `QUERY_ENDSTOPS`

### Tool Crashes During Pickup

**Check:**
- Dock positions in `T*.cfg`
- Tool zones don't overlap
- Homing works correctly
- Reduce pickup/dropoff speeds temporarily

### XY Offsets Way Off

**Check:**
- Camera focused correctly
- kTAMV server running: `sudo systemctl status ktamv`
- LED lighting (chamber OFF, nozzle RED for best contrast)
- Camera calibration: `KTAMV_CALIB_CAMERA`

### Z-Offset Inconsistent

**Check:**
- Beacon calibration: `BEACON_CALIBRATE`
- Bed mesh is loaded: `BED_MESH_PROFILE LOAD=default`
- Initial tool is set: `SET_INITIAL_TOOL TOOL=0`
- Thermal compensation calibrated per tool

### First Layer Too High/Low

**Try:**
1. Live adjustment: `SET_TOOL_Z_ADJUST Z=±0.02`
2. Recalibrate Z: `BEACON_CALIBRATE_Z INITIAL_TOOL=0`
3. Check thermal compensation: `APPLY_NOZZLE_TEMP_OFFSET`
4. Verify bed mesh: `BED_MESH_CALIBRATE`

---

## Support

**Documentation:**
- [Main README](../../README.md)
- [Calibration Guide](CALIBRATION_GUIDE.md)
- [Thermal Compensation](../../docs/THERMAL_COMPENSATION.md)
- [Troubleshooting](../../docs/TROUBLESHOOTING.md)
- [FAQ](../../docs/FAQ.md)

**Issues:**
- [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)

**Community:**
- VORON Discord - #toolchangers channel
- Klipper Discourse

---

**Last updated:** 2026-01-17
**Tested with:** Klipper v0.12.0+
**Configuration Version:** 1.1.0
