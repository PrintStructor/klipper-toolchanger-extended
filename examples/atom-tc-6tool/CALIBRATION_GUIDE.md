# ATOM TC-6 Calibration Guide

**Complete step-by-step calibration workflow for 6-tool ATOM toolchanger**

This guide walks you through calibrating your ATOM TC-6 toolchanger from initial setup to print-ready state. Expected time: 3-4 hours for full calibration.

---

## Prerequisites

Before starting calibration, ensure:

✅ **Hardware:**
- All 6 tools installed and docked correctly
- Tool detection sensors working (test with `QUERY_ENDSTOPS`)
- Beacon probe mounted and connected
- USB camera installed, focused, and accessible
- Printer homed successfully (`G28`)

✅ **Software:**
- [TAXY](https://github.com/PrintStructor/TAXY) installed (recommended) or [kTAMV](https://github.com/TypQxQ/kTAMV)
- TAXY server running: `sudo systemctl status taxy` (or kTAMV: `sudo systemctl status ktamv`)
- Beacon probe configured: `BEACON_CALIBRATE` completed
- All config files from this directory included in `printer.cfg`

✅ **Initial Setup:**
- Dock positions manually tested and safe
- Tool pickup/dropoff works manually (slow speeds)
- Beacon probe readings stable

---

## Calibration Workflow Overview

```
1. Initial Tool Setup         (5 min)
2. Camera Calibration          (10 min)
3. XY Offset Calibration       (60-90 min)
4. Z Offset Calibration        (60-90 min)
5. Thermal Compensation        (90-120 min)
6. Verification                (15 min)
─────────────────────────────────────────
Total Time: 3-4 hours
```

**Methods used:**
- **XY Calibration:** TAXY (AI-based, ~5µm precision) or kTAMV (OpenCV, legacy)
- **Z Calibration:** Beacon (contact probe, 150°C reference)
- **Thermal Calibration:** Beacon (multi-temperature measurement)

---

## Step 1: Initial Tool Setup

### 1.1 Home and Initialize

```gcode
G28                          # Home all axes
INITIALIZE_TOOLCHANGER       # Initialize toolchanger state
```

Expected output:
```
toolchanger initialized, active None
```

### 1.2 Set Initial/Reference Tool

Pick your reference tool (usually T0, but any tool works):

```gcode
SET_INITIAL_TOOL TOOL=0 FORCE_SWITCH=1
```

This tool becomes the baseline (Z-offset = 0.0). All other tools are measured relative to it.

Expected output:
```
✅ Set T0 as initial tool with offsets X=0 Y=0 Z=0.0
```

### 1.3 Verify Tool Switching

Manually test each tool to ensure pickup/dropoff works:

```gcode
T0  # Should already be selected
T1  # Switch to T1
T2  # Switch to T2
# ... etc through T5
T0  # Return to T0
```

**Watch carefully during switches!** If any tool crashes or misaligns, **STOP** and adjust dock positions before continuing.

---

## Step 2: Camera Calibration

### 2.1 Configure LED Lighting

For best TAXY/kTAMV accuracy, use optimal lighting:

```gcode
STATUS_KTAMV
```

This macro:
- Turns OFF chamber LEDs (eliminates reflections)
- Sets nozzle LEDs to FULL RED (maximum contrast)

### 2.2 Verify Camera View

Open camera preview: `http://your-printer-ip/webcam2/`

You should see:
- Nozzle clearly visible
- Dark bed surface
- Good focus (nozzle opening edges sharp)
- Centered in frame (roughly)

### 2.3 Run Camera Calibration

```gcode
KTAMV_CALIB_CAMERA
```

**What happens:**
1. Moves nozzle to calibration position
2. Takes two measurements with known movement distance
3. Calculates mm/pixel ratio
4. Saves to TAXY/kTAMV server config

Expected output:
```
Camera calibration complete: 0.0234 mm/pixel
```

**Typical values:** 0.020 - 0.030 mm/pixel (depends on camera, zoom, distance)

---

## Step 3: XY Offset Calibration

### 3.1 Choose Calibration Method

**Option A: Full Matrix (Recommended for maximum accuracy)**
- Calibrates all tool-to-tool relationships
- Takes longer (~90 min) but provides redundancy
- Use this for first-time calibration

**Option B: Single Reference (Faster)**
- Calibrates all tools relative to one reference tool
- Faster (~30 min) but less redundant
- Use this for re-calibration or touch-ups

### 3.2 Option A: Full Matrix XY Calibration

**This is the recommended method.**

```gcode
KTAMV_CALIBRATE_ALL_TOOLS_XY
```

**What happens:**
```
For each tool (T0-T5) as initial tool:
  1. Heat to 150°C
  2. Set as initial tool
  3. For each other tool:
     - Switch to tool
     - Run TAXY_FIND_NOZZLE_CENTER (or kTAMV_FIND_NOZZLE_CENTER)
     - Record XY offset
  4. Save offsets to config
  5. Cooldown

Total: 6 × 5 = 30 measurements
```

**Timeline:**
- Per tool pair: ~3 min
- Total: ~90 min

**What you'll see:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch XY Calibration (TAXY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Using T0 as initial tool...
  T1: X=-0.0970, Y=0.2180
  T2: X=-0.1010, Y=-0.3770
  T3: X=0.0130, Y=-0.0430
  T4: X=0.0000, Y=-0.0770
  T5: X=0.0490, Y=-0.2850

Using T1 as initial tool...
  T0: X=0.0950, Y=-0.2490
  ...
```

### 3.3 Option B: Single Reference XY Calibration

**Faster alternative for re-calibration:**

```gcode
KTAMV_CALIBRATE_XY INITIAL_TOOL=0
```

**What happens:**
1. Uses T0 as reference (XY = 0,0)
2. Measures T1-T5 relative to T0
3. Saves offsets to config

**Timeline:** ~30 min (5 tool measurements)

### 3.4 Save Results

The macro automatically saves, but verify:

```gcode
SAVE_CONFIG
```

Klipper will restart to apply offsets.

---

## Step 4: Z Offset Calibration

### 4.1 Prerequisites

- XY offsets already calibrated (Step 3 complete)
- Beacon probe configured and working
- Bed cleaned and leveled

### 4.2 Option A: Full Matrix Z Calibration (Recommended)

```gcode
BEACON_CALIBRATE_ALL_TOOLS_Z
```

**What happens:**
```
For each tool (T0-T5) as initial tool:
  1. Heat to 150°C (reference temperature)
  2. Set as initial tool
  3. G28 Z CALIBRATE=1 (initial tool)
  4. For each other tool:
     - Heat to 150°C
     - Switch to tool
     - Measure Z-offset via Beacon
     - Record offset
  5. Save offsets to config
  6. Cooldown

Total: 6 × 6 = 36 measurements
```

**Timeline:**
- Per tool: ~15 min (heating + measurements)
- Total: ~90 min

**What you'll see:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Batch Z Calibration (Beacon)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Using T0 as initial tool...
  T0: 0.0000 mm (initial/reference)
  T1: -0.1503 mm
  T2: -0.1531 mm
  T3: -0.1066 mm
  T4: +0.0019 mm
  T5: +0.0403 mm

Using T1 as initial tool...
  ...
```

### 4.3 Option B: Single Reference Z Calibration

**Faster alternative:**

```gcode
BEACON_CALIBRATE_Z INITIAL_TOOL=0
```

**Timeline:** ~30 min

### 4.4 Understanding Z-Offset Values

**Normal Z-offset range:** -0.3mm to +0.3mm

- **Negative offset** = Tool sits lower than reference tool
- **Positive offset** = Tool sits higher than reference tool
- **0.0000** = Initial/reference tool (always!)

**If offsets > ±0.5mm:**
- Check mechanical alignment
- Verify nozzle lengths are similar
- Re-seat tools in docks

### 4.5 Save Results

```gcode
SAVE_CONFIG
```

Klipper restarts. Z-offsets are now active!

---

## Step 5: Thermal Expansion Compensation

### 5.1 Why Thermal Compensation?

Nozzles expand when heated:
- Calibration at 150°C
- Printing at 270°C = +120°C
- Expansion: ~68µm (0.068mm)

Without compensation, first layer will be **too high**.

### 5.2 Calibrate Thermal Coefficients

Run for **each tool** (T0-T5):

```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0
```

**What happens:**
```
1. Heat to 150°C (reference) → Measure Z
2. Heat to 180°C → Measure Z
3. Heat to 210°C → Measure Z
4. Heat to 240°C → Measure Z
5. Heat to 270°C → Measure Z
6. Calculate linear expansion coefficient
7. Save to variables.cfg
```

**Timeline per tool:** ~15-20 min

**Total for all 6 tools:** ~90-120 min

**What you'll see:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nozzle Temperature Offset Calibration (T0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1/5: Heating to 150°C (reference)...
Reference Z-offset: 2.3456mm

Step 2/5: Heating to 180°C...
Z-offset: 2.3627mm (delta: +0.0171mm)

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calibration Results (T0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coefficient: 0.000570 mm/°C (5.7µm per °C)
R² score: 0.9987 (excellent fit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Expected Coefficient Range

**Normal values:** 0.0004 - 0.0008 mm/°C

- **Brass nozzles:** ~0.00055 - 0.00060 mm/°C
- **Hardened steel:** ~0.00045 - 0.00050 mm/°C
- **R² score:** Should be > 0.995 (good linear fit)

**If coefficient seems wrong:**
- Check mechanical play
- Verify Beacon stability
- Ensure bed isn't expanding significantly
- Re-run calibration

### 5.4 Repeat for All Tools

```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=1
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=2
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=3
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=4
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=5
```

Coefficients are automatically saved to `variables.cfg`.

### 5.5 Verify Stored Coefficients

Check `variables.cfg`:
```ini
nozzle_expansion_coefficient_t0 = 0.00057
nozzle_expansion_coefficient_t1 = 0.00056
nozzle_expansion_coefficient_t2 = 0.00058
# ... etc
```

**All tools should have similar coefficients** (within ±10%) if using identical nozzles.

---

## Step 6: Verification

### 6.1 Verify XY Alignment

**Method 1: Manual mark test**
```gcode
SET_INITIAL_TOOL TOOL=0
G28
G0 X175 Y175 Z0.2 F9000  # Center of bed
M104 S200                 # Heat nozzle
# Wait for heating
# Mark bed with nozzle tip (tiny dot)

# Switch tools and verify they align with mark
T1  # Should align perfectly
T2  # Should align perfectly
# ... etc
```

**Expected:** All tools should hit the same spot within ±0.1mm

**Method 2: Test print**
```gcode
# Print a test pattern with all tools
# Check that lines from different tools align
```

### 6.2 Verify Z Offset

**Method: First layer test across all tools**

```gcode
PRINT_START BED_TEMP=60 TOOL_TEMP=200 INITIAL_TOOL=0
# Print single-layer test pattern
# Switch tools during print
# Observe first layer consistency
```

**Expected:** All tools should have same first layer height/squish

**If inconsistent:**
- Use live adjustment: `SET_TOOL_Z_ADJUST Z=±0.02`
- Save if satisfied: `SAVE_TOOL_Z_ADJUSTMENTS`

### 6.3 Verify Thermal Compensation

**Test at different temperatures:**

```gcode
# Test 1: PLA @ 200°C
PRINT_START BED_TEMP=60 TOOL_TEMP=200 INITIAL_TOOL=0
# Observe first layer

# Test 2: PETG @ 240°C
PRINT_START BED_TEMP=80 TOOL_TEMP=240 INITIAL_TOOL=0
# Observe first layer

# Test 3: PC @ 270°C
PRINT_START BED_TEMP=110 TOOL_TEMP=270 INITIAL_TOOL=0
# Observe first layer
```

**Expected:** First layer quality should be **consistent across temperatures**

**Check console during PRINT_START:**
```
Thermal Offset Applied (T0)
Nozzle temp:    270.4°C
ΔT:             120.4°C
Z offset:       +0.0686mm (68.6µm)
```

If offset is NOT shown, check macro order in PRINT_START.

---

## Step 7: Live Z-Offset Adjustments

After calibration, you can make fine-tuning adjustments during printing without recalibrating.

### 7.1 Per-Tool Adjustments

Adjust individual tools if one is slightly too high/low:

```gcode
# Adjust current tool by +0.02mm
SET_TOOL_Z_ADJUST Z=+0.02

# Adjust specific tool
SET_TOOL_Z_ADJUST TOOL=2 Z=-0.01

# Reset tool to calibrated value
SET_TOOL_Z_ADJUST TOOL=2 RESET=1

# Show all current adjustments
SHOW_TOOL_Z_ADJUSTMENTS
```

**Use case:** T3 is slightly too low, but all other tools are perfect.

### 7.2 Global Adjustments

Adjust ALL tools equally (e.g., different bed surface):

```gcode
# Raise all tools by +0.01mm
GLOBAL_Z_ADJUST Z=+0.01

# Lower all tools by -0.01mm
GLOBAL_Z_ADJUST Z=-0.01

# Show current global offset
GLOBAL_Z_ADJUST

# Reset to 0
GLOBAL_Z_ADJUST RESET=1
```

**Use case:**
- Switched from PEI to textured sheet (+0.05mm)
- All tools too close/far from bed
- Seasonal temperature changes affecting bed expansion

### 7.3 Saving Adjustments

All adjustments are RAM-based until saved:

```gcode
# Save per-tool adjustments to config
SAVE_TOOL_Z_ADJUSTMENTS
```

**Global offset** is intentionally NOT saved automatically - it's meant for temporary changes (different bed surfaces, seasonal adjustments).

### 7.4 When to Use Which Command

| Scenario | Command | Example |
|----------|---------|---------|
| One tool is off | `SET_TOOL_Z_ADJUST` | T3 first layer too low |
| All tools off equally | `GLOBAL_Z_ADJUST` | Switched to textured sheet |
| Different bed surface | `GLOBAL_Z_ADJUST` | PEI → Garolite (+0.05mm) |
| After tool change | `SET_TOOL_Z_ADJUST` | Replaced T4 nozzle |
| Permanent fix | Both + `SAVE_TOOL_Z_ADJUSTMENTS` | Found optimal offset |

---

## Calibration Complete!

### Summary of What Was Calibrated

✅ **Camera:** mm/pixel ratio for TAXY/kTAMV
✅ **XY Offsets:** All tool-to-tool alignments
✅ **Z Offsets:** All tool-to-tool height differences
✅ **Thermal Coefficients:** Nozzle expansion rates per tool

### Saved Data Locations

**`printer.cfg` (SAVE_CONFIG section):**
```ini
[tool T0]
t1_xy_offset = -0.0970, 0.2180
t1_z_offset = -0.1503
# ... etc
```

**`variables.cfg`:**
```ini
nozzle_expansion_coefficient_t0 = 0.00057
nozzle_expansion_coefficient_t1 = 0.00056
# ... etc
```

### When to Re-Calibrate

**XY Offsets:** Re-run when:
- Docks are moved or re-printed
- Toolheads are mechanically changed
- XY misalignment visible in prints

**Z Offsets:** Re-run when:
- Nozzles are changed
- Hotends are modified
- First layer height differs between tools

**Thermal Coefficients:** Re-run when:
- Nozzle material changes (brass → hardened steel)
- Different nozzle brand/type
- Coefficient seems incorrect (first layer temp-dependent)

**Camera:** Re-run when:
- Camera position changes
- Camera lens adjusted
- Zoom or focus changed

---

## Troubleshooting

### TAXY/kTAMV Can't Find Nozzle

**Causes:**
- Bad lighting (chamber LEDs ON, nozzle LEDs OFF)
- Out of focus camera
- Nozzle not in camera view
- Dark/reflective bed surface

**Solutions:**
```gcode
STATUS_KTAMV          # Chamber OFF, Nozzle RED
TAXY_START_PREVIEW    # Check camera view (or KTAMV_START_PREVIEW)
# Adjust camera focus manually
# Ensure dark matte bed surface
```

### Z-Offsets Keep Changing

**Causes:**
- Beacon thermal drift
- Bed thermal expansion
- Loose Beacon mount
- Inconsistent bed mesh
- Different bed surface (e.g., PEI vs textured)

**Solutions:**

**If ALL tools are affected equally:**
```gcode
# Temporary adjustment (not saved)
GLOBAL_Z_ADJUST Z=+0.02

# Or for permanent fix:
GLOBAL_Z_ADJUST Z=+0.02
# Print test, verify, then optionally recalibrate
```

**If offsets are unstable (drift over time):**
1. Allow 15min warmup before calibration
2. Run `BEACON_CALIBRATE` to update model
3. Use consistent bed temperature
4. Check mechanical tightness

### Thermal Coefficient is 0.0

**Cause:** Tool hasn't been calibrated yet

**Solution:**
```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=X
```

### First Layer Too High at High Temps

**Causes:**
- Thermal coefficient wrong
- Thermal compensation not applied
- PRINT_START macro order wrong

**Solutions:**
1. Check console for "Thermal Offset Applied" message
2. Verify macro order: `SET_INITIAL_TOOL` before `APPLY_NOZZLE_TEMP_OFFSET`
3. Re-calibrate thermal coefficient
4. Use live adjustment:
   - Single tool off: `SET_TOOL_Z_ADJUST Z=-0.02`
   - All tools too high: `GLOBAL_Z_ADJUST Z=-0.02`

---

## Advanced: Maintenance Calibration

### Quick Re-Calibration (30 min)

If only one tool changed:

```gcode
# 1. Set unchanged tool as reference
SET_INITIAL_TOOL TOOL=1  # Use a stable tool as reference

# 2. Calibrate changed tool
KTAMV_CALIBRATE_XY INITIAL_TOOL=1
BEACON_CALIBRATE_Z INITIAL_TOOL=1

# 3. Only recalibrate thermal for changed tool
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0  # If T0 changed

# 4. Save
SAVE_CONFIG
```

### Periodic Verification (15 min)

Every ~100 print hours:

```gcode
# 1. Print alignment test pattern
# 2. Visually inspect XY alignment
# 3. If off, re-run XY calibration
# 4. Print first layer test
# 5. If off, use SET_TOOL_Z_ADJUST
```

---

## Next Steps

**After calibration is complete:**

1. **Run a test print** with tool changes
2. **Fine-tune with live adjustments** if needed
3. **Save adjustments** via `SAVE_TOOL_Z_ADJUSTMENTS`
4. **Print real multi-color parts!**

**Recommended test prints:**
- Calibration cube with color changes per layer
- Multi-material mechanical part
- Voron logo (each color = different tool)

---

## Support

**Documentation:**
- [ATOM TC-6 README](README.md)
- [Thermal Compensation Guide](../../docs/THERMAL_COMPENSATION.md)
- [General Calibration Guide](../../docs/CALIBRATION.md)
- [Troubleshooting](../../docs/TROUBLESHOOTING.md)

**Issues:**
- [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)

**Community:**
- VORON Discord - #toolchangers
- Klipper Discourse

---

**Last updated:** 2026-01-17
**Configuration Version:** 1.1.0
