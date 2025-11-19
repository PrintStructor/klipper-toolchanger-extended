# ⚡ Quick Start Guide

**Get your toolchanger running in under an hour!**

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Klipper** installed and working
- ✅ **VORON 2.4** or similar **CoreXY** printer
- ✅ **CAN-Bus** setup (highly recommended) or USB connections
- ✅ **At least 2 toolheads** mechanically installed
- ✅ **Tool detection sensors** (filament sensors or microswitches)
- ✅ **SSH access** to your Klipper host

**⏱️ Estimated Time:** 45-60 minutes

---

## 🚀 Step 1: Installation (5 minutes)

### Clone the Repository

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
```

### Run the Installer

```bash
cd ~/klipper-toolchanger-extended
./install.sh
```

**What this does:**
- ✅ Installs Python modules to Klipper's extras directory
- ✅ Configures Moonraker update manager
- ✅ Creates symlinks for easy updates

### Restart Klipper

```bash
sudo systemctl restart klipper
```

**Verify installation:**
- Check Mainsail/Fluidd for errors
- Look for "klipper ready" status

---

## 🔧 Step 2: Basic Configuration (20 minutes)

### 2.1 Add Core Includes to printer.cfg

Open your `printer.cfg` and add at the top:

```ini
#####################################################################
# Klipper Toolchanger Extended
#####################################################################

[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger_macros.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/macros.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/calibrate_offsets.cfg]

# Add your tools (minimum 2)
[include klipper-toolchanger-extended/examples/atom-tc-6tool/T0.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/T1.cfg]
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T2.cfg]  # Add more as needed

# Optional: Hardware integration
[include klipper-toolchanger-extended/examples/atom-tc-6tool/beacon.cfg]  # If using Beacon
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/tc_led_effects.cfg]  # If using LEDs
```

### 2.2 Find Your CAN UUIDs

For each toolhead with a CAN board:

```bash
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

**Example output:**
```
Found canbus_uuid=abc123def456, Application: Klipper
Found canbus_uuid=789ghi012jkl, Application: Klipper
```

### 2.3 Configure Each Tool

**Copy the example configs to your config directory:**

```bash
mkdir -p ~/printer_data/config/toolchanger
cp ~/klipper-toolchanger-extended/examples/atom-tc-6tool/*.cfg ~/printer_data/config/toolchanger/
```

**Edit each tool file (T0.cfg, T1.cfg, etc.):**

Open `T0.cfg` and update:

```ini
[mcu T0]
canbus_uuid: abc123def456  # ← YOUR UUID HERE!

[tool T0]
tool_number: 0
params_park_x: 25.3        # ← YOUR DOCK POSITION
params_park_y: 3.0         # ← YOUR DOCK POSITION
params_park_z: 325.0       # ← YOUR DOCK HEIGHT
```

**⚠️ CRITICAL:** Measure your dock positions accurately!
- Use `GET_POSITION` to record current XYZ
- Park each toolhead manually over its dock
- Write down the coordinates

**Repeat for T1, T2, etc.**

### 2.4 Configure Safe Positions

Edit `toolchanger.cfg`:

```ini
[toolchanger]
params_safe_y: 105        # ← Safe Y for horizontal moves (clear of docks)
params_close_y: 35        # ← Y position close to dock area
```

**How to determine:**
- `params_safe_y`: Y position where toolhead can move X freely without hitting docks
- `params_close_y`: Y position just in front of docks

### 2.5 Save and Restart

```gcode
SAVE_CONFIG
RESTART
```

---

## 🎯 Step 3: First Initialization (10 minutes)

### 3.1 Home Your Printer

```gcode
G28
```

**Verify:** All axes home successfully without errors.

### 3.2 Set Initial Tool

```gcode
SET_INITIAL_TOOL TOOL=0
```

**What this does:**
- Sets T0 as the reference tool (XY offsets = 0, 0)
- All other tools will be calibrated relative to T0
- This is your "master" tool

### 3.3 Test Tool Detection

For each tool, verify detection works:

```gcode
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
QUERY_FILAMENT_SENSOR SENSOR=T1_filament_sensor
```

**Expected output:**
- With tool present: `filament_detected: True`
- Without tool: `filament_detected: False`

**🚨 Troubleshooting:**
- If inverted, add `!` to pin in TX.cfg: `switch_pin: !PG12`
- Check wiring and sensor functionality

### 3.4 Test First Tool Change

**Manually position toolhead near T0 dock:**

```gcode
G0 X25 Y10 Z330 F3000  # Adjust to your dock area
```

**Test dock/undock:**

```gcode
TEST_TOOL_DOCKING
```

**What happens:**
1. Tool drops off at dock
2. Returns to safe position
3. Picks up tool again
4. Returns to start position

**🚨 If this fails:**
- Check dock positions are correct
- Verify path in toolchanger.cfg matches your hardware
- Manually jog through dock path to verify clearances

---

## 📐 Step 4: Calibration (30 minutes)

### 4.1 Prepare NUDGE Probe

**Position the probe:**
- Place NUDGE probe on bed in accessible location
- Note approximate X, Y coordinates

**Update in `calibrate_offsets.cfg`:**

```ini
[gcode_macro NUDGE_MOVE_OVER_PROBE]
gcode:
    G0 X150 Y150 Z10 F6000  # ← YOUR PROBE POSITION
```

**Test positioning:**

```gcode
G28
SET_INITIAL_TOOL TOOL=0
T0
NUDGE_MOVE_OVER_PROBE
```

**Verify:** Nozzle should be roughly above probe center (±2mm is fine).

### 4.2 Calibrate XY Offsets

**Ensure nozzles are clean!** Calibration accuracy depends on clean nozzles.

```gcode
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
```

**What happens:**
1. T0 locates probe center (establishes reference)
2. Switches to T1, finds probe center
3. Calculates XY offset between T0 and T1
4. Repeats for all configured tools
5. Prompts to save config

**Expected output example:**
```
T0: XY offset = 0.000, 0.000 (reference tool)
T1: XY offset = -0.022, 0.091
T2: XY offset = 0.015, -0.033
```

**Save the results:**

```gcode
SAVE_CONFIG
```

### 4.3 Calibrate Z Offsets

**Using Beacon probe:**

```gcode
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
```

**What happens:**
1. T0 performs Beacon contact (establishes Z reference)
2. Switches to T1, performs Beacon contact
3. Calculates Z offset difference
4. Repeats for all tools
5. Auto-saves to config files via shell script

**Expected output example:**
```
T0: Z offset = 0.00000 (reference tool)
T1: Z offset = -0.10512
T2: Z offset = 0.05234
```

### 4.4 Tune Global Z-Offset

The global Z-offset fine-tunes first layer height for the initial tool.

**Run a first layer test print with T0:**

```gcode
G28
BED_MESH_CALIBRATE
T0
G0 X100 Y100 Z0.2 F3000
# Print a small square or line
```

**Adjust based on first layer:**
- Too squished → increase value: `0.08` → `0.10`
- Too high → decrease value: `0.08` → `0.06`

**Set the value:**

```gcode
SET_GCODE_VARIABLE MACRO=globals VARIABLE=global_z_offset VALUE=0.08
SAVE_CONFIG
```

**Typical range:** 0.06 - 0.12mm

---

## 🖨️ Step 5: First Multi-Tool Print (10 minutes)

### 5.1 Configure OrcaSlicer

See the detailed [OrcaSlicer Setup Guide](../examples/atom-tc-6tool/ORCASLICER_SETUP.md).

**Quick setup:**

1. **Machine Start G-code:**
   ```gcode
   PRINT_START BED_TEMP=[first_layer_bed_temperature] TOOL_TEMP={first_layer_temperature[initial_tool]} INITIAL_TOOL=[initial_tool]
   ```

2. **Machine End G-code:**
   ```gcode
   PRINT_END
   ```

3. **Change Filament G-code:**
   ```gcode
   M104 S{temperature[next_extruder]} T[next_extruder]
   ```

### 5.2 Slice a Test Object

**Recommendations:**
- Start simple: 2 tools, 2 colors
- Small object (< 50mm)
- Low layer count (< 30 layers)
- Moderate tool changes (< 20 changes)

**Test models:**
- Calibration cube with logo in different color
- Multi-color spiral vase
- Simple 2-part assembly

### 5.3 Start the Print

```gcode
PRINT_START BED_TEMP=110 TOOL_TEMP=240 INITIAL_TOOL=0
```

**Monitor the first few layers:**
- Tool changes complete successfully
- No crashes or detection errors
- Layers adhere properly
- Offsets look correct

### 5.4 Success! 🎉

**Congratulations!** You now have a working multi-tool 3D printer.

**Share your success:**
- Post pictures in discussions
- Report any issues found
- Contribute improvements

---

## ✅ Quick Start Checklist

Use this checklist to track your progress:

- [ ] **Installation**
  - [ ] Repository cloned
  - [ ] install.sh executed
  - [ ] Klipper restarted without errors

- [ ] **Configuration**
  - [ ] Core configs included in printer.cfg
  - [ ] CAN UUIDs found and entered
  - [ ] Dock positions measured and configured
  - [ ] Safe Y positions configured
  - [ ] Config saved and Klipper restarted

- [ ] **Initialization**
  - [ ] Printer homed successfully
  - [ ] Initial tool set (T0)
  - [ ] Tool detection verified for all tools
  - [ ] TEST_TOOL_DOCKING successful

- [ ] **Calibration**
  - [ ] NUDGE probe positioned
  - [ ] XY offsets calibrated and saved
  - [ ] Z offsets calibrated and saved
  - [ ] Global Z-offset tuned for first layer

- [ ] **First Print**
  - [ ] OrcaSlicer configured
  - [ ] Test object sliced
  - [ ] Print completed successfully

---

## 🆘 Quick Troubleshooting

### "Toolchanger not initialized"
**Solution:** Run `INITIALIZE_TOOLCHANGER` or `SET_INITIAL_TOOL TOOL=0`

### Tool detection fails
**Solution:** 
- Check sensor with `QUERY_FILAMENT_SENSOR`
- Verify wiring and pin configuration
- Try inverting pin: `switch_pin: !PG12`

### Tool gets stuck during pickup
**Solution:**
- Verify dock positions are correct
- Reduce path speed: `params_path_speed: 300`
- Manually test path motions

### XY offsets seem wrong
**Solution:**
- Ensure initial tool was set before calibration
- Clean nozzles thoroughly
- Re-run `NUDGE_FIND_TOOL_OFFSETS`

### First layer height inconsistent between tools
**Solution:**
- Re-calibrate Z offsets
- Check Beacon probe calibration
- Adjust global_z_offset

---

## 📚 Next Steps

Now that your toolchanger is running, explore these guides:

### For Configuration
- [**Configuration Guide**](CONFIGURATION.md) - Detailed parameter reference
- [**Calibration Guide**](CALIBRATION.md) - Advanced calibration techniques

### For Troubleshooting
- [**Troubleshooting Guide**](TROUBLESHOOTING.md) - Comprehensive problem solving
- [**FAQ**](FAQ.md) - Common questions answered

### For Advanced Features
- [Tool Probe System](tool_probe.md) - Configure custom probes
- [Rounded Path](rounded_path.md) - Smooth motion paths
- [LED Effects](../examples/atom-tc-6tool/tc_led_effects.cfg) - Visual feedback

### Community
- [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)
- [Report Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)
- [Contribute](../CONTRIBUTING.md)

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**License:** GPL-3.0
