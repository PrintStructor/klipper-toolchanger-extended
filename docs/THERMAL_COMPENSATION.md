# Thermal Expansion Compensation Guide

**Advanced Z-Offset Accuracy for Multi-Tool Printing**

This guide explains the nozzle thermal expansion compensation system in klipper-toolchanger-extended, which automatically adjusts Z-offsets based on nozzle temperature to compensate for thermal expansion.

---

## Table of Contents

1. [Why Thermal Compensation?](#1-why-thermal-compensation)
2. [How It Works](#2-how-it-works)
3. [Calibration Procedure](#3-calibration-procedure)
4. [Using Thermal Compensation](#4-using-thermal-compensation)
5. [Understanding the Results](#5-understanding-the-results)
6. [Troubleshooting](#6-troubleshooting)
7. [Advanced Topics](#7-advanced-topics)

---

## 1. Why Thermal Compensation?

### The Problem

When you calibrate Z-offsets using Beacon or other probes, the calibration is typically done at a specific temperature (reference temperature = 150°C). However, during actual printing:

- Different materials print at different temperatures (PLA: 200°C, ABS: 240°C, PC: 270°C)
- Nozzles expand as they heat up
- Thermal expansion changes the effective nozzle length
- Z-offset measured at 150°C is not accurate at 270°C

**Example:**
```
Calibration at 150°C: Z-offset = -0.1503mm
Printing at 270°C:    Nozzle expanded by ~0.068mm
Effective Z-offset:   -0.1503mm + 0.068mm = -0.0823mm
```

Without compensation, your first layer will be **0.068mm too high** (68 microns).

### Typical Thermal Expansion

| Temperature Delta | Brass Nozzle Expansion | Effect on First Layer |
|-------------------|------------------------|----------------------|
| +50°C (150→200°C) | ~28µm | Barely noticeable |
| +90°C (150→240°C) | ~51µm | Poor adhesion |
| +120°C (150→270°C) | ~68µm | Print fails |

Different nozzle materials expand at different rates:
- **Brass:** ~0.56µm/°C (most common)
- **Hardened Steel:** ~0.48µm/°C (less expansion)
- **Copper:** ~0.64µm/°C (more expansion)

### The Solution

The thermal compensation system:
1. **Measures** the expansion coefficient for each tool
2. **Calculates** the temperature-dependent offset
3. **Applies** the correction automatically during printing
4. **Adapts** to different printing temperatures

---

## 2. How It Works

### System Components

**1. Calibration Module (`beacon_diagnostics.cfg`):**
- `BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET` - Measures expansion coefficient
- Heats nozzle to multiple temperatures
- Records Z-offset at each temperature
- Calculates linear coefficient (mm/°C)

**2. Application Module (`beacon_diagnostics.cfg`):**
- `APPLY_NOZZLE_TEMP_OFFSET` - Applies temperature-based correction
- Reads current nozzle temperature
- Calculates offset based on coefficient
- Uses `Z_ADJUST` to add compensation (non-destructive)

**3. Storage (`variables.cfg`):**
- `nozzle_expansion_coefficient_t0` through `t5`
- Reference temperature (150°C)
- Coefficients persist across reboots

### Calculation Method

```python
ΔTemp = Current_Nozzle_Temp - Reference_Temp  # e.g., 270°C - 150°C = 120°C
Z_Compensation = ΔTemp × Coefficient            # e.g., 120°C × 0.00057 mm/°C = 0.0684mm
```

The compensation is **added** to the base Z-offset via `SET_GCODE_OFFSET Z_ADJUST`, so it doesn't overwrite calibrated values.

### Integration with Print Workflow

**PRINT_START sequence:**
```gcode
1. G28 Z CALIBRATE=1         # Initial Z calibration at probe temp
2. Heat nozzle to print temp  # e.g., 270°C
3. SET_INITIAL_TOOL           # Set base Z-offset (Z=0 for initial tool)
4. APPLY_NOZZLE_TEMP_OFFSET   # Add thermal compensation
5. Start printing             # Final Z = Base + Thermal + Adjustments
```

**Critical:** `APPLY_NOZZLE_TEMP_OFFSET` must run **after** `SET_INITIAL_TOOL` to avoid being overwritten.

---

## 3. Calibration Procedure

### Prerequisites

- Beacon probe installed and working
- Tools already calibrated with base Z-offsets
- Clean nozzles (no plastic residue)
- Stable printer temperature (allow 15min warmup)

### Step-by-Step Calibration

**1. Home and initialize:**
```gcode
G28
SET_INITIAL_TOOL TOOL=0
```

**2. Run thermal calibration for T0:**
```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0
```

**What happens:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nozzle Temperature Offset Calibration (T0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1/5: Heating to 150°C (reference)...
Collected 10 samples, 0.0023mm std
Reference Z-offset: 2.3456mm

Step 2/5: Heating to 180°C...
Collected 10 samples, 0.0019mm std
Z-offset: 2.3627mm (delta: +0.0171mm)

Step 3/5: Heating to 210°C...
Collected 10 samples, 0.0021mm std
Z-offset: 2.3798mm (delta: +0.0342mm)

Step 4/5: Heating to 240°C...
Collected 10 samples, 0.0018mm std
Z-offset: 2.3969mm (delta: +0.0513mm)

Step 5/5: Heating to 270°C...
Collected 10 samples, 0.0020mm std
Z-offset: 2.4140mm (delta: +0.0684mm)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calibration Results (T0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Linear fit: y = 0.000570x - 0.0829
Coefficient: 0.000570 mm/°C (5.7µm per °C)
R² score: 0.9987 (excellent fit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Saved to variables.cfg as:
  nozzle_expansion_coefficient_t0 = 0.000570
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**3. Repeat for all tools:**
```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=1
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=2
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=3
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=4
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=5
```

**4. Verify stored coefficients:**
```gcode
SHOW_NOZZLE_TEMP_COEFFICIENTS  # (if available, otherwise check variables.cfg)
```

### Expected Calibration Time

- **Per tool:** ~15-20 minutes
- **All 6 tools:** ~90-120 minutes
- **One-time process** (unless nozzles are changed)

### Quality Indicators

**Good calibration:**
- R² score > 0.995 (linear fit is excellent)
- Standard deviation < 0.003mm per temperature
- Coefficient in range 0.0004 - 0.0008 mm/°C

**Poor calibration (redo if):**
- R² score < 0.990 (non-linear behavior)
- Standard deviation > 0.005mm (unstable readings)
- Coefficient < 0.0002 or > 0.001 mm/°C (unusual)

---

## 4. Using Thermal Compensation

### Automatic Application (Recommended)

Thermal compensation is **automatically applied** in `PRINT_START`:

```gcode
[gcode_macro PRINT_START]
gcode:
    # ... heating and setup ...

    SET_INITIAL_TOOL TOOL={initial_tool}  # Set base Z-offset

    # Apply thermal compensation AFTER tool initialization
    APPLY_NOZZLE_TEMP_OFFSET TOOL={initial_tool}

    # ... continue with print ...
```

No manual intervention needed - just start your print!

### Manual Application

For testing or special scenarios:

**Apply for current tool:**
```gcode
APPLY_NOZZLE_TEMP_OFFSET
```

**Apply for specific tool:**
```gcode
APPLY_NOZZLE_TEMP_OFFSET TOOL=2
```

**Clear compensation:**
```gcode
CLEAR_NOZZLE_TEMP_OFFSET
```

### Tool Changes During Print

When changing tools mid-print, thermal compensation is automatically recalculated:

```
T0 @ 270°C → Compensation: +0.0684mm
T1 @ 240°C → Compensation: +0.0513mm (different coefficient)
```

Each tool has its own coefficient, so compensation adapts to the active tool.

---

## 5. Understanding the Results

### Console Output Explained

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thermal Offset Applied (T0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nozzle temp:    270.4°C          ← Current nozzle temperature
Reference:      150.0°C          ← Calibration reference temp
ΔT:             120.4°C          ← Temperature difference
Coefficient:    0.00056944 mm/°C ← Tool-specific expansion rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Z offset:       +0.0686mm (68.6µm) ← Applied compensation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What this means:**
- Nozzle is **120.4°C** hotter than calibration temperature
- Thermal expansion: **0.57µm per degree Celsius**
- Total compensation: **+68.6 microns**
- This value is **added** to your base Z-offset

### UI Display

After `APPLY_NOZZLE_TEMP_OFFSET`, you should see the offset in:

**Mainsail/Fluidd:**
```
Z-Offset: +0.0686mm
```

**KlipperScreen:**
```
Offset Z: +0.069
```

If you don't see the offset, check:
1. PRINT_START order (APPLY after SET_INITIAL_TOOL)
2. Console for error messages
3. Coefficient is not 0.0 (run calibration first)

### Interaction with Other Offsets

**Final Z-offset calculation:**
```
Final Z = Base Z + Thermal Compensation + Live Adjustments

Example for T1:
  Base Z-offset:     -0.1503mm  (from MEASURE_TOOL_Z_OFFSETS)
  Thermal comp:      +0.0686mm  (from APPLY_NOZZLE_TEMP_OFFSET)
  Live adjustment:   +0.0200mm  (from SET_TOOL_Z_ADJUST)
  ──────────────────────────────
  Final Z-offset:    -0.0617mm
```

All three systems work together:
1. **Base Z** sets the foundation
2. **Thermal** adapts to temperature
3. **Live adjustments** allow fine-tuning

---

## 6. Troubleshooting

### Thermal Offset Not Applied

**Symptoms:**
- Console shows "Thermal Offset Applied" but UI shows Z=0
- First layer too high despite thermal compensation

**Causes & Fixes:**

1. **Wrong macro order in PRINT_START:**
   ```gcode
   # WRONG - thermal offset gets overwritten
   APPLY_NOZZLE_TEMP_OFFSET
   SET_INITIAL_TOOL TOOL=0  # ← This resets Z to 0

   # CORRECT - thermal offset persists
   SET_INITIAL_TOOL TOOL=0
   APPLY_NOZZLE_TEMP_OFFSET  # ← Applied after tool init
   ```

2. **Coefficient is 0.0 (not calibrated):**
   ```
   ⚠️ T2 has no thermal expansion calibration!
   Run: BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=2
   ```
   Solution: Run calibration for that tool

3. **Wrong tool specified:**
   ```gcode
   # If T2 is active but you apply for T0:
   APPLY_NOZZLE_TEMP_OFFSET TOOL=0  # ← Wrong tool!

   # Correct - apply for active tool:
   APPLY_NOZZLE_TEMP_OFFSET  # Auto-detects T2
   ```

### Coefficient Seems Wrong

**Too high (> 0.001 mm/°C):**
- Mechanical play in toolhead
- Loose Beacon mount
- Bed expansion interfering
- **Action:** Check mechanical stability, recalibrate

**Too low (< 0.0002 mm/°C):**
- Hardened steel nozzle (expected ~0.48µm/°C)
- Calibration error
- **Action:** Verify nozzle material, recalibrate if brass

**Negative coefficient:**
- Severe mechanical issue
- Beacon probe malfunction
- **Action:** Check probe wiring, mechanical components

### First Layer Still Inconsistent

**After applying thermal compensation:**

1. **Check base Z-offsets are correct:**
   ```gcode
   MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
   ```

2. **Verify bed mesh is active:**
   ```gcode
   BED_MESH_PROFILE LOAD=default
   ```

3. **Test without thermal compensation:**
   ```gcode
   CLEAR_NOZZLE_TEMP_OFFSET
   # Start test print
   ```
   If first layer improves, coefficient may be wrong

4. **Use live adjustments for fine-tuning:**
   ```gcode
   SET_TOOL_Z_ADJUST Z=+0.01  # Tiny adjustments
   ```

### Calibration Fails or Gives Errors

**"Probe triggered during move":**
- Bed too close to nozzle at high temp
- Z-offset drift during heating
- **Action:** Increase initial Z position, allow thermal stabilization

**"Temperature timeout":**
- Heater power too low
- Thermal runaway protection triggered
- **Action:** Check heater configuration, PID tuning

**"Standard deviation too high":**
- Mechanical vibrations
- Bed expansion issues
- Inconsistent contact
- **Action:** Wait for thermal stabilization, check mechanics

---

## 7. Advanced Topics

### Customizing Temperature Points

Default calibration temperatures: 150°C, 180°C, 210°C, 240°C, 270°C

To customize (requires macro editing):

```gcode
[gcode_macro BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET]
variable_temp_points: [150, 200, 250, 300]  # Custom temps
```

**Recommendations:**
- Always include 150°C (reference temperature)
- Use temperatures you actually print at
- More points = better linear fit (but longer calibration)
- Max safe temp depends on your hotend (check specs!)

### Per-Material Coefficients

Different materials don't change the coefficient (it's a property of the nozzle, not the filament). However:

**Printing temperature affects compensation:**
```
PLA @ 200°C:  ΔT = 50°C  → Compensation = +28µm
ABS @ 240°C:  ΔT = 90°C  → Compensation = +51µm
PC  @ 270°C:  ΔT = 120°C → Compensation = +68µm
```

Same coefficient, different compensation based on print temperature.

### Coefficient Averaging Across Tools

If all tools use identical nozzles, coefficients should be similar:

```
T0: 0.000570 mm/°C
T1: 0.000568 mm/°C  ← Within ±5% is normal
T2: 0.000573 mm/°C
...
```

**Large variation (>10%) indicates:**
- Different nozzle materials/brands
- Mechanical differences between tools
- Calibration errors

### Integration with Bed Thermal Expansion

**Important:** Beacon measures nozzle-to-bed distance. If your bed expands:

```
Nozzle expansion:  +68µm (at 270°C)
Bed expansion:     +20µm (if heated bed expands)
Net Z-offset:      +48µm (measured difference)
```

For heated beds with significant expansion:
- Calibrate with bed at print temperature
- Or use `bed_thermal_adjust` module (if available)
- Compensation captures the **net** expansion seen by the probe

### Batch Thermal Calibration

To calibrate all tools in one run, create a custom macro:

```gcode
[gcode_macro CALIBRATE_ALL_THERMAL]
gcode:
    {% for tool in range(6) %}
        RESPOND MSG="Calibrating T{tool}..."
        BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL={tool}
        G4 P30000  # 30 second cooldown between tools
    {% endfor %}
    RESPOND MSG="All thermal calibrations complete!"
```

**Total time:** ~2 hours for 6 tools

### Verifying Coefficient Accuracy

**Method 1: Manual test**
```gcode
1. Home and set initial tool
2. G28 Z CALIBRATE=1 (at 150°C)
3. Note Z-offset value
4. Heat to 270°C
5. G28 Z CALIBRATE=1 (at 270°C)
6. Note new Z-offset value
7. Calculate: (Z₂ - Z₁) / (270-150) = coefficient
```

Compare calculated coefficient with stored value.

**Method 2: First layer test**
```gcode
1. Print test pattern at 200°C
2. Print same pattern at 270°C
3. Measure first layer height with caliper
4. Difference should match thermal compensation
```

### Temperature Sensor Accuracy

Thermal compensation relies on accurate temperature readings:

**Check thermistor calibration:**
```gcode
# Heat to 150°C
M104 S150
M109 S150

# Use IR thermometer on nozzle tip
# Compare readings - should be within ±3°C
```

If temperature readings are off by 10°C+:
- Run PID tuning
- Check thermistor type in config
- Verify wiring and connections

Inaccurate temperature = incorrect compensation!

---

## Summary

**Key Takeaways:**

1. **Thermal compensation is essential** for accurate Z-offsets across different printing temperatures
2. **One-time calibration** per tool (unless nozzles are changed)
3. **Automatic application** in PRINT_START (no manual intervention)
4. **Works with other systems:** Base Z-offsets + Thermal + Live adjustments
5. **Typical coefficient:** 0.0004 - 0.0008 mm/°C for brass nozzles

**Quick Reference:**

```gcode
# Calibrate (once per tool)
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0

# Apply (automatic in PRINT_START)
APPLY_NOZZLE_TEMP_OFFSET

# Clear (for testing)
CLEAR_NOZZLE_TEMP_OFFSET
```

For general calibration workflows, see [CALIBRATION.md](CALIBRATION.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

**Last updated:** 2026-01-17
