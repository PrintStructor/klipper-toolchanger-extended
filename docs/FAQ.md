# ❓ Frequently Asked Questions (FAQ)

**Quick answers to common questions**

---

## 📋 Table of Contents

1. [General Questions](#general-questions)
2. [Hardware Questions](#hardware-questions)
3. [Software & Configuration](#software--configuration)
4. [Calibration & Operation](#calibration--operation)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Features](#advanced-features)

---

## General Questions

### What is klipper-toolchanger-extended?

It's an enhanced fork of the original klipper-toolchanger by viesturz, featuring:
- **Two-stage tool pickup** with verification
- **Non-fatal error handling** (pause instead of emergency stop)
- **ATOM toolhead** integration
- **Per-tool input shaper**
- **LED effects** and KNOMI display support
- **Beacon + NUDGE** calibration integration

**Based on:** [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)

---

### Can I use other toolheads besides ATOM?

**Yes!** The system is designed to be hardware-agnostic. 

**However:**
- ATOM toolheads are specifically optimized for this setup
- ATOM is an exclusive design by the creator of the Reaper Toolhead
- Other toolheads require custom dock configurations

**What you need for any toolhead:**
- Physical docking mechanism (magnets, mechanical lock, etc.)
- Tool detection sensor
- Proper path definition for dock/undock

---

### How many tools can I use?

**Minimum:** 2 tools (for multi-tool functionality)  
**Maximum:** Theoretically unlimited

**Practical limits:**
- **2-3 tools:** Simple setups, limited dock space
- **4-6 tools:** Sweet spot (ATOM standard)
- **7+ tools:** Possible but requires careful planning

**Considerations for many tools:**
- Dock space availability
- Tool change time increases
- Complexity of path planning
- Cable management (CAN-bus recommended)

---

### Do I need CAN-bus?

**No, but highly recommended.**

**Without CAN (USB):**
- ✅ Works fine for 2-3 tools
- ❌ Cable management nightmare with 4+ tools
- ❌ Limited by USB bandwidth
- ❌ Physical USB connection complexity

**With CAN:**
- ✅ Clean cable routing (2 wires per tool)
- ✅ Reliable communication
- ✅ Scales well to 6+ tools
- ✅ Industry standard

**Recommendation:** Use CAN-bus for 4+ tools, USB acceptable for 2-3.

---

### Is this compatible with my printer?

**Compatible with:**
- ✅ Klipper firmware
- ✅ CoreXY kinematics (VORON 2.4, Trident, etc.)
- ✅ Other kinematics (Cartesian, Delta - with adaptation)
- ✅ Custom printers with proper docking space

**Requirements:**
- Sufficient Z-height for tool docking
- Space for tool docks (front, back, or side)
- Ability to detect tool presence (sensors)

**Not compatible with:**
- ❌ Marlin firmware
- ❌ Stock printers without modifications

---

### What makes this "extended" vs. the original?

| Feature | Original | Extended |
|---------|----------|----------|
| Basic toolchanging | ✅ | ✅ |
| Two-stage pickup | ❌ | ✅ |
| Non-fatal errors | ❌ | ✅ |
| Tool presence monitoring | ❌ | ✅ |
| ATOM integration | ❌ | ✅ |
| Per-tool input shaper | ❌ | ✅ |
| LED effects | ❌ | ✅ |
| KNOMI displays | ❌ | ✅ |
| Beacon integration | ❌ | ✅ |
| OrcaSlicer profiles | ❌ | ✅ |

---

## Hardware Questions

### Do I need NUDGE probe?

**No, but it simplifies XY calibration.**

**Alternatives:**
- **Manual calibration:** Print alignment test patterns
- **Vision-based:** Camera + image recognition (advanced)
- **Mechanical jigs:** Custom alignment tools
- **Beacon only:** For Z-offsets (still need XY method)

**NUDGE benefits:**
- Automatic XY offset calibration
- Repeatable and accurate
- Quick re-calibration
- See: [zruncho3d/nudge](https://github.com/zruncho3d/nudge)

---

### Which probe types are supported?

**For Z-homing and bed mesh:**
- ✅ **Beacon** (eddy current + contact mode)
- ✅ **BLTouch / CR-Touch**
- ✅ **Inductive probes**
- ✅ **Klicky / Euclid** (dock-based)
- ✅ **Cartographer**

**For XY calibration:**
- ✅ **NUDGE** (nozzle contact probe)
- ✅ **Manual alignment methods**

**Note:** Beacon is recommended for its contact mode Z-calibration feature.

---

### Can I mix different extruder types?

**Yes!** Each tool can have completely different hardware:

**Example setup:**
- T0: Direct drive with 0.4mm nozzle
- T1: Bowden with 0.6mm nozzle  
- T2: Direct drive with 0.2mm nozzle

**Each tool independently configures:**
- Extruder type and gear ratio
- Temperature ranges
- Pressure advance
- Max extrusion rate
- Input shaper values

---

### Do I need filament sensors?

**Yes, for tool detection.**

**Usage:**
- **Primary:** Detect if tool is picked up
- **Secondary:** Optional filament runout detection

**Types:**
- Simple switch sensors (recommended)
- Optical sensors
- Magnetic sensors

**Installation:**
- One sensor per tool
- Triggers when tool is mounted
- Must be reliable (safety critical)

---

### Can I use IDEX with this?

**Yes, via cascading toolchangers.**

**Setup:**
- Main toolchanger for IDEX carriages
- Child toolchanger (MMU) on one carriage

**Configuration:**
```ini
[toolchanger mmu]
parent_tool: T0    # IDEX carriage
# MMU filaments as child tools
```

**See:** `parent_tool` documentation in [CONFIGURATION.md](CONFIGURATION.md)

---

### What LEDs are supported?

**Compatible LED types:**
- ✅ WS2812B (NeoPixel)
- ✅ SK6812 (RGBW)
- ✅ WS2811
- ✅ APA102 (optional)

**Common uses:**
- Chamber lighting with status
- Per-tool logo LEDs
- Nozzle illumination
- Dock status indicators

**Requirements:**
- LED-effects plugin (or built-in Klipper support)
- Proper power supply (5V, 60mA per LED)

---

## Software & Configuration

### Which slicer should I use?

**Recommended: OrcaSlicer**
- ✅ Native multi-tool support
- ✅ Advanced features (wipe tower, tool sequencing)
- ✅ Profile examples provided
- ✅ Active development

**Also compatible:**
- ✅ PrusaSlicer (similar to Orca)
- ✅ SuperSlicer
- ⚠️ Cura (limited multi-tool support)

**See:** [ORCASLICER_SETUP.md](../examples/atom-tc-6tool/ORCASLICER_SETUP.md)

---

### Does it work with Mainsail / Fluidd?

**Yes, both are fully compatible!**

- ✅ All G-code commands work
- ✅ Macro buttons supported
- ✅ Status monitoring
- ✅ Web interface control

**No special configuration needed** - standard Klipper integration.

---

### Is Moonraker update manager supported?

**Yes!** Configured automatically by `install.sh`.

**Features:**
- Auto-update checking
- One-click updates
- Version tracking
- Rollback support

**Check status:**
```yaml
# In Mainsail: Machine → Update Manager
# Should show "klipper-toolchanger-extended"
```

---

### Can I use Klipper Screen?

**Yes!** Standard Klipper Screen works.

**Note:** Some custom toolchanger commands may need button mapping.

**Example panels:**
```yaml
# Add to KlipperScreen.conf
[menu __main __toolchanger]
name: Toolchanger
icon: toolchanger

[menu __main __toolchanger __t0]
name: Select T0
method: printer.gcode.script
params: {"script":"T0"}
```

---

### How do I backup my configuration?

**Manual backup:**
```bash
tar -czf ~/config_backup_$(date +%Y%m%d).tar.gz ~/printer_data/config/
```

**Automated (recommended):**
- Use GitHub sync (via Mainsail/Fluidd)
- Set up automatic backups
- Keep multiple versions

**What to backup:**
- All `.cfg` files
- Calibration data
- Macro customizations
- Saved offsets

---

## Calibration & Operation

### How often should I calibrate?

**Initial Setup:**
- Full calibration required

**Regular Maintenance:**

| Type | Frequency | Trigger |
|------|-----------|---------|
| XY offsets | Monthly | Or if drift noticed |
| Z offsets | Monthly | Or after nozzle changes |
| Global Z | Per material | First layer tuning |
| Input shaper | Quarterly | Or after hardware changes |
| Dock positions | Rarely | Only if mechanically changed |

**Quick checks:**
- Print test pattern weekly
- Verify offsets if quality degrades

---

### What if my offsets drift?

**Common causes:**
1. **Mechanical loosening** → Tighten bolts
2. **Dock movement** → Re-secure docks
3. **Probe drift** → Re-mount NUDGE/Beacon
4. **Temperature effects** → Let printer heat soak before calibration

**Solutions:**
- Re-run calibration: `NUDGE_FIND_TOOL_OFFSETS`
- Check mechanical rigidity
- Use thread locker on critical fasteners
- Calibrate at operating temperature

---

### Can I calibrate without NUDGE?

**Yes, manual methods available:**

**Method 1: Test prints**
1. Print alignment pattern with T0
2. Switch to T1, print over same pattern
3. Measure XY misalignment
4. Manually enter offsets

**Method 2: Microscope/Camera**
1. Position each nozzle over same point
2. Use microscope to measure position
3. Calculate offsets mathematically

**Method 3: Paper method**
1. Position nozzles at same XY
2. Use paper drag test for Z
3. Measure differences

**NUDGE advantages:**
- Automated process
- Higher accuracy
- Repeatable results
- Faster

---

### How long does a tool change take?

**Typical times:**

| Speed Setting | Tool Change Time |
|---------------|------------------|
| Safe (1800 mm/min) | 8-12 seconds |
| Normal (3000 mm/min) | 5-7 seconds |
| Fast (27000 mm/min travel) | 3-5 seconds |

**Factors affecting time:**
- Movement speeds configured
- Distance to docks
- Path complexity
- Pre-heating enabled

**Optimization:**
- Use fast travel speeds
- Pre-heat next tool during change
- Optimize dock positions
- Use rounded paths

---

### What is "initial tool" and why do I need it?

**Initial tool** = Reference tool for offset calculations.

**Why it matters:**
- T0 (initial tool) has offsets = 0, 0, 0
- All other tools measured relative to T0
- Changing initial tool invalidates existing offsets

**Best practices:**
- Always use T0 as initial tool
- Set before every print: `PRINT_START ... INITIAL_TOOL=0`
- Don't change initial tool once calibrated
- If you must change, re-calibrate all offsets

---

### Can I print with just one tool?

**Yes!** Multi-tool system works perfectly for single-tool prints.

**Advantages of always having toolchanger:**
- Swap tools for different materials
- Change nozzle sizes easily
- Keep different filament colors loaded
- Emergency backup if one tool fails

**Single-tool workflow:**
```gcode
PRINT_START ... INITIAL_TOOL=0
# Print uses only T0
PRINT_END
```

---

## Troubleshooting

### Tool gets stuck during pickup/dropoff

**Quick fixes:**
1. **Reduce speed:** `params_path_speed: 300`
2. **Check alignment:** Manual jog to dock position
3. **Clean dock:** Remove debris/filament
4. **Verify path:** Path matches dock geometry

**See detailed solutions:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md#tool-change-failures)

---

### Detection says tool present when it's not

**Cause:** Sensor inverted or faulty

**Quick fix:**
```ini
# In TX.cfg, toggle inversion:
detection_pin: !T0:PG11    # Add or remove !
```

**Verify:**
```gcode
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
```

---

### Offsets seem random/incorrect

**Likely causes:**
1. **Initial tool not set** → Run `SET_INITIAL_TOOL TOOL=0`
2. **Nozzles dirty** → Clean and re-calibrate
3. **Mechanical issue** → Check tightness
4. **Wrong probe position** → Verify NUDGE placement

**Always:**
- Set initial tool before calibration
- Clean nozzles before calibration
- Run calibration when printer heat-soaked

---

### Print failed mid-way, can I resume?

**Yes, with proper error handling!**

**If using custom `error_gcode`:**
```ini
[toolchanger]
error_gcode:
    PAUSE    # Pauses instead of emergency stop
```

**Recovery procedure:**
1. Fix the issue (reseat tool, clear jam, etc.)
2. Run `RESUME` command
3. Print continues automatically

**Without custom error_gcode:**
- Klipper emergency stops
- Must restart print from beginning

---

### CAN-bus shows wrong UUIDs

**Cause:** UUIDs changed after reflashing boards

**Solution:**
```bash
# Find new UUIDs
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0

# Update each tool config
[mcu T0]
canbus_uuid: NEW_UUID_HERE
```

**Tip:** Label boards physically with their UUID

---

## Advanced Features

### What is "Two-Stage Pickup"?

**Safety feature** that verifies tool presence during pickup.

**How it works:**
1. **Stage 1:** Partial insertion → Check sensor → Stop if not detected
2. **Stage 2:** Complete insertion (only if Stage 1 passed)

**Benefits:**
- Prevents crashes from missed pickups
- Early detection of problems
- Allows safe recovery

**Configuration:**
- Mark verification point with `'f':0.5` in path
- Requires tool detection sensor

**See:** [ATOM README](../examples/atom-tc-6tool/README.md#two-stage-tool-pickup)

---

### What is "Rounded Path" module?

**Smooths toolchange movements** with curved paths.

**Benefits:**
- Reduced vibrations
- Less mechanical stress
- Smoother motion
- Quieter operation

**Usage:**
```ini
[rounded_path]

# In pickup_gcode, use ROUNDED_G0 instead of G0
ROUNDED_G0 X100 Y50 Z10
```

**See:** [rounded_path.md](rounded_path.md)

---

### Can I have different input shaper per tool?

**Yes!** Each tool can have unique resonance compensation.

**Configuration:**
```ini
[tool T0]
params_input_shaper_type_x: ei
params_input_shaper_freq_x: 79.8
# ... etc

[toolchanger]
after_change_gcode:
    {% if tool.params_input_shaper_freq_x %}
        SET_INPUT_SHAPER SHAPER_FREQ_X={tool.params_input_shaper_freq_x}
    {% endif %}
```

**Why useful:**
- Different toolhead masses
- Different mounting rigidity
- Optimize each tool individually

---

### What is "Tool Presence Monitoring"?

**Real-time detection** during printing.

**What it does:**
- Continuously checks if tool is still attached
- Detects if tool falls off mid-print
- Automatically pauses print if tool lost
- Prevents damage from continuing without tool

**Configuration:**
```gcode
# Automatically enabled in PRINT_START
UPDATE_DELAYED_GCODE ID=TOOL_PRESENCE_MONITOR DURATION=2.0
```

---

### Can I customize LED effects?

**Absolutely!** Full LED control available.

**Example effects:**
- Tool status colors
- Temperature indication
- Progress visualization
- Error states (red)
- Ready states (green/blue)

**Customization:**
```ini
# In tc_led_effects.cfg
[led_effect my_custom_effect]
# Define your custom animations
```

**See:** Example in `examples/atom-tc-6tool/tc_led_effects.cfg`

---

### How does the OrcaSlicer post-processing script work?

**Automatic tool shutdown** after last use.

**Problem solved:**
- OrcaSlicer keeps unused tools at 100°C standby
- Wastes energy
- Unnecessary heat

**Solution:**
- Script scans G-code for last tool usage
- Inserts `M104 S0 T{tool}` to turn off completely
- Saves ~50W per unused tool

**Installation:**
```
Post-processing scripts:
/usr/bin/python3 "/home/pi/orcaslicer_tool_shutdown.py"
```

**See:** [ORCASLICER_SETUP.md](../examples/atom-tc-6tool/ORCASLICER_SETUP.md#post-processing-script-auto-tool-shutdown)

---

### Can I use this for an MMU?

**Yes!** Two approaches:

**1. Direct MMU as tools:**
- Each filament = one tool
- MMU hardware handles filament loading
- Toolchanger handles switching logic

**2. Cascading (IDEX + MMU):**
- Physical toolheads as parent tools
- MMU filaments as child tools

**Configuration depends on MMU type:**
- ERCF
- Prusa MMU
- Tradrack
- Custom MMU

---

## Still Have Questions?

**Check these resources:**

1. **Documentation:**
   - [Quick Start Guide](QUICKSTART.md)
   - [Configuration Guide](CONFIGURATION.md)
   - [Calibration Guide](CALIBRATION.md)
   - [Troubleshooting Guide](TROUBLESHOOTING.md)

2. **Community:**
   - [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)
   - [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)

3. **Original Project:**
   - [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**License:** GPL-3.0
