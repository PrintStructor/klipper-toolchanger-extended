# 🔧 Configuration Guide

**Complete parameter reference and configuration best practices**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Minimum Configuration](#minimum-configuration)
3. [Configuration Checklist](#configuration-checklist)
4. [Parameter Reference](#parameter-reference)
5. [Typical Configurations](#typical-configurations)
6. [Advanced Features](#advanced-features)
7. [Validation](#validation)

---

## Overview

The toolchanger system is modular and highly configurable. This guide will help you understand:

- **What parameters are required** vs optional
- **How parameters interact** with each other
- **Best practices** for different hardware setups
- **Common configurations** for reference

### Configuration Philosophy

The system follows these principles:

1. **Sensible Defaults:** Most parameters have defaults suitable for typical setups
2. **Override Hierarchy:** Tool settings override toolchanger settings
3. **Fail-Safe:** Safety features enabled by default
4. **Modular:** Include only what you need

---

## Minimum Configuration

### Required Files

At minimum, you need:

```ini
# In your printer.cfg
[include path/to/toolchanger.cfg]          # Core toolchanger module
[include path/to/toolchanger_macros.cfg]   # Essential macros
[include path/to/T0.cfg]                   # Minimum 1 tool
[include path/to/T1.cfg]                   # Minimum 2 tools total
```

### Required Parameters per Tool

Each tool file **MUST** configure:

```ini
[mcu TX]
canbus_uuid: YOUR_UUID_HERE              # ⚠️ REQUIRED

[extruder]
# Standard Klipper extruder config        # ⚠️ REQUIRED

[tool TX]
tool_number: X                            # ⚠️ REQUIRED (0-N)
extruder: extruder                        # ⚠️ REQUIRED
params_park_x: XX.X                       # ⚠️ REQUIRED
params_park_y: XX.X                       # ⚠️ REQUIRED
params_park_z: XXX.X                      # ⚠️ REQUIRED
```

### Required Toolchanger Parameters

```ini
[toolchanger]
params_safe_y: XXX                        # ⚠️ REQUIRED
params_close_y: XX                        # ⚠️ REQUIRED
```

---

## Configuration Checklist

Use this interactive checklist to ensure proper setup:

### ✅ Phase 1: Installation

- [ ] Repository cloned to `~/klipper-toolchanger-extended`
- [ ] `install.sh` executed successfully
- [ ] Klipper restarted without errors
- [ ] `[toolchanger]` section appears in config reference

### ✅ Phase 2: Core Configuration

- [ ] **toolchanger.cfg** included in printer.cfg
- [ ] **toolchanger_macros.cfg** included
- [ ] **macros.cfg** included (for PRINT_START/END)
- [ ] At least 2 tool files (T0.cfg, T1.cfg) included

### ✅ Phase 3: Hardware Configuration

#### For Each Tool:

- [ ] **CAN UUID** found and entered in `[mcu TX]`
- [ ] **Extruder** fully configured with thermistor, heater, etc.
- [ ] **Hotend fan** configured
- [ ] **Part cooling fan** configured (optional but recommended)
- [ ] **Filament sensor** configured for tool detection
- [ ] **Tool number** assigned (0, 1, 2...)

#### Dock Positions:

- [ ] **params_park_x** measured for each tool
- [ ] **params_park_y** measured for each tool
- [ ] **params_park_z** measured for each tool
- [ ] Positions verified with manual jogging

#### Safe Zones:

- [ ] **params_safe_y** determined (Y where X travel is safe)
- [ ] **params_close_y** determined (Y near docks)
- [ ] Zones verified with manual movements

### ✅ Phase 4: Probing Configuration

- [ ] **Probe type** chosen (NUDGE, Beacon, BLTouch, etc.)
- [ ] **Probe position** determined and configured
- [ ] **Z-probe** configured for homing/mesh
- [ ] **XY calibration probe** configured (if using NUDGE)

### ✅ Phase 5: Optional Features

- [ ] **LED effects** configured (if using)
- [ ] **KNOMI displays** configured (if using)
- [ ] **Input shaper** per tool (if using)
- [ ] **Bed mesh** configured
- [ ] **Quad gantry leveling** configured (for VORON)

### ✅ Phase 6: Testing

- [ ] `QUERY_TOOLCHANGER` shows correct tool count
- [ ] `SET_INITIAL_TOOL TOOL=0` succeeds
- [ ] `TEST_TOOL_DOCKING` completes without errors
- [ ] All tool detection sensors respond correctly
- [ ] Manual tool change (T0 → T1) works

---

## Parameter Reference

### [toolchanger] Section

Complete reference for the `[toolchanger]` configuration section.

#### Core Parameters

```ini
[toolchanger]
```

**Purpose:** Defines the toolchanger instance and its behavior.

---

#### save_current_tool

```ini
save_current_tool: false
```

- **Type:** Boolean
- **Default:** `false`
- **Purpose:** Save currently selected tool to persistent storage on shutdown
- **Use Case:** Resume with correct tool after power loss

**When to use:**
- ✅ Production printers with frequent power interruptions
- ❌ Development/testing setups (can cause confusion)

---

#### initialize_gcode

```ini
initialize_gcode:
    G28           # Example: Home on init
    # Custom initialization sequence
```

- **Type:** GCode macro
- **Default:** Empty
- **Purpose:** Run custom code when toolchanger initializes
- **Available Context:** `printer`, `toolchanger`

**Common uses:**
- Homing sequence
- Load saved tool: `SET_INITIAL_TOOL TOOL={saved_tool}`
- LED status indication

---

#### initialize_on

```ini
initialize_on: first-use
```

- **Type:** Enum: `manual`, `home`, `first-use`
- **Default:** `first-use`
- **Purpose:** When to auto-initialize the toolchanger

**Options:**
- `manual`: Only via `INITIALIZE_TOOLCHANGER` command
- `home`: Automatically on `G28` (homing)
- `first-use`: On first tool selection (recommended)

**Recommendation:** Use `first-use` for most setups.

---

#### verify_tool_pickup

```ini
verify_tool_pickup: True
```

- **Type:** Boolean
- **Default:** `True`
- **Purpose:** Verify tool presence after pickup using detection sensor

**⚠️ SAFETY:** Leave enabled! Prevents crashes from failed pickups.

---

#### require_tool_present

```ini
require_tool_present: False
```

- **Type:** Boolean
- **Default:** `False`
- **Purpose:** Raise error if no tool detected on init or unmount

**When to enable:**
- Tool contains critical sensors (e.g., Z-probe on tool)
- Printer cannot operate without a tool present

---

#### uses_axis

```ini
uses_axis: xyz
```

- **Type:** String (combination of x, y, z)
- **Default:** `xyz`
- **Purpose:** Which axes must be homed before tool changes

**Examples:**
- `xyz`: All axes (recommended)
- `xy`: Only XY (if Z-independent docking)
- `z`: Only Z (unusual)

---

#### on_axis_not_homed

```ini
on_axis_not_homed: abort
```

- **Type:** Enum: `abort`, `home`
- **Default:** `abort`
- **Purpose:** What to do if required axes not homed

**Options:**
- `abort`: Stop and show error (safer)
- `home`: Automatically home axes (convenience)

**Recommendation:** Use `abort` during setup, `home` once stable.

---

#### params_* (Custom Parameters)

```ini
params_safe_y: 105
params_close_y: 35
params_fast_speed: 27000
params_path_speed: 3000
params_park_x: 25.0        # Can be overridden per tool
params_park_y: 3.0         # Can be overridden per tool
params_park_z: 325.0       # Can be overridden per tool
```

- **Type:** Varies (float, int, string)
- **Purpose:** Custom parameters accessible in pickup/dropoff macros
- **Access:** `toolchanger.params_name` or `tool.params_name`

**Common parameters:**

| Parameter | Type | Purpose | Typical Value |
|-----------|------|---------|---------------|
| `params_safe_y` | Float | Y position safe for X travel | 105.0 |
| `params_close_y` | Float | Y position near docks | 35.0 |
| `params_fast_speed` | Int | Travel speed (mm/min) | 27000 |
| `params_path_speed` | Int | Docking speed (mm/min) | 3000 |
| `params_park_x` | Float | Tool dock X position | 25.3 |
| `params_park_y` | Float | Tool dock Y position | 3.0 |
| `params_park_z` | Float | Tool dock Z position | 325.0 |

**Note:** Parameters defined on toolchanger become defaults for all tools. Tools can override individually.

---

#### before_change_gcode

```ini
before_change_gcode:
    STATUS_CHANGING    # Example: Set LED status
    # Runs before every tool change
```

- **Type:** GCode macro
- **Default:** Empty
- **Purpose:** Code to run before every tool change
- **Use Cases:** LED indicators, logging, pre-change movements

---

#### after_change_gcode

```ini
after_change_gcode:
    # Apply per-tool input shaper settings
    {% if tool.params_input_shaper_freq_x %}
        SET_INPUT_SHAPER SHAPER_FREQ_X={tool.params_input_shaper_freq_x}
    {% endif %}
```

- **Type:** GCode macro
- **Default:** Empty
- **Purpose:** Code to run after every tool change
- **Common uses:** 
  - Apply per-tool input shaper
  - Set accelerations
  - Update LED status

---

#### error_gcode

```ini
error_gcode:
    PAUSE                    # Pause instead of emergency stop
    M104 S0 T{tool.tool_number}  # Turn off heater
    STATUS_ERROR             # Set LED to error state
```

- **Type:** GCode macro
- **Default:** Empty (Klipper emergency stop)
- **Purpose:** Custom error handling instead of emergency shutdown

**⚠️ IMPORTANT:** With custom error_gcode, the print can be recovered with `RESUME` after fixing the issue.

---

#### recover_gcode

```ini
recover_gcode:
    # Experimental recovery sequence
```

- **Type:** GCode macro
- **Default:** Empty
- **Purpose:** Run on `INITIALIZE_TOOLCHANGER RECOVER=1`
- **Status:** Experimental

---

#### parent_tool / parent_mounting_mode / parent_unmounting_mode

```ini
parent_tool: T0                      # Name of parent tool
parent_mounting_mode: parent-first   # parent-first | child-first
parent_unmounting_mode: lazy         # child-first | parent-first | lazy
```

- **Purpose:** Cascading toolchanger support (e.g., IDEX + MMU)
- **Advanced Feature:** See cascading documentation

---

#### transfer_fan_speed

```ini
transfer_fan_speed: True
```

- **Type:** Boolean
- **Default:** `True`
- **Purpose:** Maintain fan speed when switching tools

**Behavior:**
- `True`: New tool inherits fan speed from previous tool
- `False`: Each tool starts with fan speed = 0

---

### [tool] Section

Complete reference for individual tool configuration.

```ini
[tool T0]
```

**Purpose:** Define a selectable tool.

---

#### toolchanger

```ini
toolchanger: toolchanger
```

- **Type:** String (toolchanger name)
- **Default:** `toolchanger`
- **Purpose:** Which toolchanger this tool belongs to
- **Use Case:** Multiple toolchanger systems

---

#### extruder

```ini
extruder: extruder
```

- **Type:** String (extruder name)
- **Required:** ✅ YES
- **Purpose:** Name of the extruder to activate with this tool

**For multi-extruder:**
- T0: `extruder`
- T1: `extruder1`
- T2: `extruder2`

---

#### extruder_stepper

```ini
extruder_stepper: tool0_extruder_stepper
```

- **Type:** String (extruder_stepper name)
- **Default:** Empty (use main extruder)
- **Purpose:** Use separate stepper for filament motion

**Use case:** Y-type multi-extruder hotends

---

#### fan

```ini
fan: multi_fan T0_partfan
```

- **Type:** String (fan name)
- **Default:** Empty (use printer's fan)
- **Purpose:** Which fan to use as part cooling for this tool

**Note:** Use `multi_fan` or `fan_generic` type fans for per-tool control.

---

#### detection_pin

```ini
detection_pin: T0:PG11
```

- **Type:** String (MCU pin)
- **Default:** Empty (no detection)
- **Purpose:** Pin for tool presence detection

**Common sensors:**
- Filament switch sensors
- Microswitches
- Hall effect sensors

**Pin configuration:**
- `^PG11` - Pullup enabled
- `!PG11` - Inverted
- `^!PG11` - Both

---

#### tool_number

```ini
tool_number: 0
```

- **Type:** Integer (0-N)
- **Required:** ✅ YES
- **Purpose:** Tool number for T command (e.g., T0, T1)

**Important:** 
- Must be unique per tool
- Creates automatic `T0`, `T1`... macros
- Used for M104/M109 temperature commands

---

#### pickup_gcode

```ini
pickup_gcode:
    # Tool-specific pickup sequence
    G0 X{tool.params_park_x} Y{tool.params_park_y} Z{tool.params_park_z} F{toolchanger.params_fast_speed}
    # More movements...
```

- **Type:** GCode macro
- **Default:** Empty (no pickup)
- **Purpose:** How to pick up this tool

**Available context:**
- `tool` - This tool object
- `toolchanger` - Toolchanger object
- `pickup_tool` - Name of tool being picked up
- `dropoff_tool` - Name of tool being dropped off (if switching)

---

#### dropoff_gcode

```ini
dropoff_gcode:
    # Tool-specific dropoff sequence
```

- **Type:** GCode macro
- **Default:** Empty (no dropoff)
- **Purpose:** How to drop off this tool

---

#### gcode_x_offset / gcode_y_offset / gcode_z_offset

```ini
gcode_x_offset: -0.022
gcode_y_offset: 0.091
gcode_z_offset: -0.105
```

- **Type:** Float (millimeters)
- **Default:** 0.0
- **Purpose:** Tool offset relative to reference tool (T0)

**Important:**
- Reference tool (T0) should have all offsets = 0.0
- Other tools are relative to T0
- Set via calibration (`NUDGE_FIND_TOOL_OFFSETS`, `MEASURE_TOOL_Z_OFFSETS`)

---

#### params_* (Tool-Specific Parameters)

```ini
params_park_x: 25.3
params_park_y: 3.0
params_park_z: 325.0
params_input_shaper_freq_x: 79.8
params_input_shaper_type_x: ei
# Any custom parameter
```

- **Type:** Varies
- **Purpose:** Tool-specific parameters accessible in macros
- **Inheritance:** Inherits from toolchanger, can override

**Access:** `tool.params_name`

---

#### t_command_restore_axis

```ini
t_command_restore_axis: XYZ
```

- **Type:** String (combination of X, Y, Z)
- **Default:** `XYZ`
- **Purpose:** Which axes to restore position after T command

**Examples:**
- `XYZ`: Restore all (default)
- `XY`: Restore only XY
- `Z`: Restore only Z
- `` (empty): Don't restore any

---

### [tools_calibrate] Section

Configuration for NUDGE-based offset calibration.

```ini
[tools_calibrate]
pin: ^PG11                       # Detection pin
spread: 3.5                      # Touch distance from center (mm)
lower_z: 0.2                     # Z distance to lower for contact (mm)
travel_speed: 300                # Travel speed (mm/s)
speed: 2.0                       # Probing speed (mm/s)
lift_speed: 5.0                  # Z lift speed (mm/s)
final_lift_z: 1.0                # Z lift between probes (mm)
sample_retract_dist: 1.0         # Z retract between samples (mm)
samples: 3                       # Number of samples per probe
samples_tolerance: 0.05          # Max variance between samples (mm)
samples_tolerance_retries: 3     # Retry attempts
samples_result: median           # Result method: median | average
trigger_to_bottom_z: 0.0         # Z from trigger to mechanical bottom (mm)
```

**See [CALIBRATION.md](CALIBRATION.md) for detailed usage.**

---

## Typical Configurations

### Small Setup (2-3 Tools)

**Characteristics:**
- Limited dock space
- Simple tool changes
- Manual configuration acceptable

**Recommendations:**
```ini
[toolchanger]
params_fast_speed: 18000      # Slower for safety
params_path_speed: 1800       # Slower docking
verify_tool_pickup: True      # Essential
```

---

### Medium Setup (4-6 Tools) ⭐ ATOM Standard

**Characteristics:**
- Multiple docks in a row
- CAN-bus recommended
- Per-tool features (input shaper, fans)

**Recommendations:**
```ini
[toolchanger]
params_fast_speed: 27000      # Fast travel
params_path_speed: 3000       # Moderate docking
verify_tool_pickup: True      # Essential
transfer_fan_speed: True      # Convenience
```

**Features:**
- Per-tool input shaper
- Individual LED effects
- Beacon/NUDGE calibration

---

### Large Setup (7+ Tools)

**Characteristics:**
- Complex dock arrangements
- Longer tool change times
- Advanced path planning needed

**Recommendations:**
```ini
[toolchanger]
params_fast_speed: 30000      # Very fast travel
params_path_speed: 3000       # Keep docking safe
initialize_on: home           # Auto-init on home
```

**Considerations:**
- Rounded path module highly recommended
- Consider cascading toolchangers
- LED status indicators essential
- Thorough testing required

---

## Advanced Features

### Per-Tool Input Shaper

Apply individual resonance compensation per tool:

```ini
[tool T0]
params_input_shaper_type_x: ei
params_input_shaper_freq_x: 79.8
params_input_shaper_damping_ratio_x: 0.069
params_input_shaper_type_y: mzv
params_input_shaper_freq_y: 42.6
params_input_shaper_damping_ratio_y: 0.055
```

**Apply in after_change_gcode:**
```ini
[toolchanger]
after_change_gcode:
    {% if tool.params_input_shaper_freq_x %}
        SET_INPUT_SHAPER SHAPER_TYPE_X={tool.params_input_shaper_type_x} SHAPER_FREQ_X={tool.params_input_shaper_freq_x} DAMPING_RATIO_X={tool.params_input_shaper_damping_ratio_x}
    {% endif %}
    {% if tool.params_input_shaper_freq_y %}
        SET_INPUT_SHAPER SHAPER_TYPE_Y={tool.params_input_shaper_type_y} SHAPER_FREQ_Y={tool.params_input_shaper_freq_y} DAMPING_RATIO_Y={tool.params_input_shaper_damping_ratio_y}
    {% endif %}
```

---

### Rounded Path Module

Smooth curved movements reduce mechanical stress:

```ini
[rounded_path]

[toolchanger]
# In pickup/dropoff, use ROUNDED_G0 instead of G0
```

**Benefits:**
- Reduced vibrations
- Smoother tool changes
- Less mechanical wear

**See:** [rounded_path.md](rounded_path.md)

---

### Multi-Fan Configuration

Control multiple fans per tool:

```ini
[multi_fan T0_partfan]
fans: T0_fan1, T0_fan2

[tool T0]
fan: multi_fan T0_partfan
```

---

### LED Integration

Visual feedback for tool status:

```ini
[toolchanger]
before_change_gcode:
    STATUS_CHANGING

after_change_gcode:
    STATUS_READY
```

**See:** Example in `tc_led_effects.cfg`

---

### KNOMI Display Integration

BTT KNOMI displays per tool:

```ini
[tool T0]
params_knomi_host: knomi-t0.local
```

**See:** Example in `knomi.cfg`

---

## Validation

### Pre-Flight Checks

Before first use, verify:

```gcode
# 1. Toolchanger recognized
QUERY_TOOLCHANGER

# Expected: Shows tool count, status, etc.

# 2. All tools registered
# Should show T0, T1, T2...

# 3. Detection sensors work
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
QUERY_FILAMENT_SENSOR SENSOR=T1_filament_sensor
# Repeat for all tools

# 4. Initialize
SET_INITIAL_TOOL TOOL=0

# 5. Test docking
TEST_TOOL_DOCKING

# 6. Test tool change
T0
T1
T0
```

---

### Configuration Verification Commands

```gcode
# Display toolchanger status
QUERY_TOOLCHANGER

# Show current tool
# Check: printer.toolchanger.tool

# Show tool offsets
# Check: printer.tool_TX.gcode_x_offset, etc.

# Test tool detection
QUERY_FILAMENT_SENSOR SENSOR=TX_filament_sensor
```

---

### Common Configuration Errors

#### Error: "Toolchanger not initialized"

**Cause:** Toolchanger not initialized before first tool change.

**Solution:**
```gcode
INITIALIZE_TOOLCHANGER
# or
SET_INITIAL_TOOL TOOL=0
```

---

#### Error: "Tool detection failed"

**Cause:** Detection sensor not configured or not working.

**Solution:**
1. Verify `detection_pin` in tool config
2. Test sensor: `QUERY_FILAMENT_SENSOR SENSOR=TX_filament_sensor`
3. Check pin inversion (add or remove `!`)

---

#### Error: "Axis not homed"

**Cause:** Required axes not homed before tool change.

**Solution:**
```gcode
G28  # Home all axes
```

Or set `on_axis_not_homed: home` in toolchanger config.

---

## Configuration Templates

### Template: Minimal 2-Tool Setup

```ini
[include klipper-toolchanger/toolchanger.cfg]

[toolchanger]
params_safe_y: 100
params_close_y: 30

[tool T0]
tool_number: 0
extruder: extruder
params_park_x: 25
params_park_y: 5
params_park_z: 300
detection_pin: ^MCU:PG11

[tool T1]
tool_number: 1
extruder: extruder1
params_park_x: 85
params_park_y: 5
params_park_z: 300
detection_pin: ^MCU:PG12
```

---

### Template: 6-Tool ATOM Setup

**See:** Complete example in `examples/atom-tc-6tool/`

---

## Related Documentation

- [**Quick Start Guide**](QUICKSTART.md) - Get started quickly
- [**Calibration Guide**](CALIBRATION.md) - Offset calibration
- [**Troubleshooting**](TROUBLESHOOTING.md) - Fix common issues
- [**FAQ**](FAQ.md) - Common questions

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**License:** GPL-3.0
