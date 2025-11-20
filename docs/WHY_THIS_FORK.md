# About This Fork

## What This Is

This is an extension of [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) that adds:

**1. Additional Safety Features**
- Two-stage pickup with intermediate verification
- Continuous tool presence monitoring during prints
- Pause-based error handling for recoverable issues
- Automatic heater shutoff on tool loss

**2. Complete Working Configuration**
- 6-tool VORON 2.4 setup with ATOM toolheads
- All macros and safety checks pre-configured
- Documented hardware specifications
- LED status integration

**3. Guided Calibration**
- NUDGE probe for XY offset calibration
- Beacon contact probe for Z offset calibration
- Automated measurement workflows
- Configuration saved via SAVE_CONFIG

---

## Technical Differences from Base Project

### viesturz/klipper-toolchanger provides:

- **Core toolchanger logic** - Fundamental state management and operations
- **Flexible tool/dock abstraction** - Generic framework for any hardware
- **Basic pickup/dropoff framework** - Essential movement sequences
- **Minimal configuration approach** - Toolkit for building custom solutions

This is an excellent foundation for experimentation and custom implementations.

### This fork adds:

- **Verification step between pickup stages** - Approach → verify sensor → commit
- **Background tool presence checking** - Monitors tool attachment during printing
- **Error recovery macros** - Structured procedures for common failure modes
- **Complete example configuration** - All macros, safety checks, and settings
- **Hardware-specific documentation** - ATOM toolheads, CPAP cooling, wiring
- **Calibration workflows** - Command-driven offset measurement and storage

---

## Who This Is For

### Use this fork if:

✅ You're building a 6-tool VORON with ATOM-style toolheads  
✅ You want a working starting configuration to adapt  
✅ You prefer documented examples over starting from scratch  
✅ You value safety features like verification and monitoring  
✅ You want guided calibration procedures

### Use viesturz/klipper-toolchanger base if:

✅ You have completely custom hardware  
✅ You want maximum flexibility in implementation  
✅ You prefer minimal frameworks over complete examples  
✅ You enjoy building systems from first principles  
✅ Your hardware doesn't match the ATOM reference design

### Use TypQxQ implementations if:

✅ You need virtual tool support (logical tools vs physical)  
✅ You're building MMU-style systems  
✅ You want different architectural approaches  
✅ Your use case benefits from that project's specific features

**All of these projects have merit** - this fork simply provides one specific approach with additional safety features and a complete reference implementation for a particular hardware setup.

---

## Realistic Expectations

### This fork provides:

✅ **Working configuration for specific hardware** - 6-tool VORON with ATOM toolheads  
✅ **Additional safety checks** - Two-stage pickup, presence monitoring, recovery  
✅ **Documented calibration process** - Step-by-step XY and Z offset procedures  
✅ **Real-world tested configuration** - Actually used on a production machine  
✅ **Complete macro set** - All necessary toolchange operations pre-configured

### This fork does NOT:

❌ **Magically work on all hardware** - Configuration is hardware-specific  
❌ **Eliminate all toolchange risks** - Mechanical precision still required  
❌ **Replace proper alignment** - Docks must still be positioned correctly  
❌ **Work without configuration** - You must adjust values for your machine  
❌ **Prevent all failures** - Some issues still require manual intervention

---

## What "Complete Configuration" Means

**Most toolchanger projects provide:**
- Python modules for core logic
- Example tool/dock definitions
- Basic pickup/dropoff macros
- "Configure the rest yourself"

**This fork provides:**
- All of the above, plus:
- Pre-configured safety macros
- LED status visualization
- Display integration (KNOMI)
- Temperature management
- Error recovery procedures
- OrcaSlicer integration examples
- Per-tool input shaper profiles
- Complete 6-tool printer.cfg example

**Why this matters:**

Instead of spending weeks implementing safety features, macro logic, and calibration workflows, you start with a working system and adapt it to your specific hardware dimensions, sensor pins, and CAN UUIDs.

This doesn't eliminate configuration work - it reduces it from "build everything" to "adjust values for your setup."

---

## Setup Time Expectations

### Hardware Build
**Several weeks to months** (if building toolchanger from scratch)
- Designing or sourcing toolheads
- Building dock stations
- Installing tool detection sensors
- Wiring umbilicals or cable chains
- Mechanical alignment
- Testing pickup/dropoff reliability

### Software Configuration
**1-2 days** (with this fork's complete config)
- Copying configuration files
- Adjusting dock positions for your hardware
- Setting CAN UUIDs for your toolhead boards
- Configuring probe offsets
- Tuning movement speeds
- Verifying sensor operation

### Calibration
**2-3 hours** (initial XY + Z for all 6 tools)
- Homing and setting initial tool
- Running NUDGE XY offset calibration
- Running Beacon Z offset calibration
- Verifying offsets with test prints
- Fine-tuning if needed

### Tuning & Testing
**Ongoing**
- Speed/acceleration optimization
- Recalibration after maintenance
- Adjusting dock positions
- Fixing mechanical issues
- Learning your system's quirks

---

## Safety Features Explained

### Two-Stage Pickup

Standard pickup approaches the dock and engages the tool in one continuous motion. If alignment is slightly off or a sensor isn't working, you don't know until the tool is already moving away from the dock.

**This fork's two-stage approach:**

1. **Approach and pre-engage** - Move to dock, partial engagement
2. **Verify tool detection** - Check sensor confirms tool presence
3. **Complete engagement** - Finish pickup only if verification passes
4. **Abort if failed** - Return tool to dock and maintain previous tool state

**When this helps:**
- Dock position slightly off after thermal cycling
- Tool not fully seated in dock
- Sensor wiring issue or bad connection
- Mechanical misalignment

**Result:** Catches problems before committing to moves with an unverified tool.

---

### Tool Presence Monitoring

During printing, the system periodically checks that the active tool is still attached.

**If tool loss is detected:**
1. Pause the print immediately
2. Shut off the lost tool's heater (fire/damage prevention)
3. Move to safe Z height (protect part and bed)
4. Display error and wait for user intervention

**When this helps:**
- Tool not fully locked in shuttle
- Mechanical failure during print
- Vibration loosens tool over time
- Impact dislodges tool

**Result:** Prevents dragging an unattached hotend across your print or creating a fire hazard.

---

### Error Recovery Instead of Emergency Stops

Many toolchanger setups treat most errors as fatal:
> "Error detected → Emergency stop → Print lost → Start over"

This fork uses pause-based recovery:
> "Error detected → Pause safely → Preserve state → Allow recovery → Resume"

**Recoverable scenarios:**
- Tool detection sensor glitch (transient)
- Tool not properly seated after pickup
- Dock position slightly misaligned
- User intervention needed

**Recovery workflow:**
1. System pauses and moves to safe position
2. User investigates issue
3. User fixes problem (re-seat tool, adjust dock, etc.)
4. User runs recovery macro if needed
5. System resumes print from paused position

**When recovery isn't possible:**
- Some failures are still fatal (crashes, major mechanical failure)
- Recovery depends on the specific error
- User judgment required to decide if recovery is safe

---

## Hardware Requirements

This configuration is designed for:

**Printer Base:**
- VORON 2.4 or similar CoreXY
- MGN12 linear rails (X-axis)
- Carbon fiber or aluminum X-extrusion
- Standard CoreXY kinematics

**Toolheads:**
- ATOM toolhead system (or mechanically compatible)
- 236g per complete tool (with extruder, hotend, sensors)
- Tool detection sensor on each tool
- Individual heater cartridges and thermistors
- CAN bus toolhead boards

**Shuttle:**
- Lightweight shuttle assembly (~52g)
- CPAP blower centrally mounted
- Beacon probe mounted on shuttle
- Pin-and-bushing pickup mechanism (ClickChanger/Stealthchanger style)

**Probing:**
- Beacon contact probe (Z-offsets and bed meshing)
- NUDGE probe (XY offset calibration)

**Docks:**
- 6 dock stations positioned around print area
- Tool detection sensors or switches
- Mechanical alignment features

**Optional:**
- KNOMI display for status
- LED strips for visual feedback
- Per-tool filament sensors

**Different hardware will require substantial modifications** to dock positions, pickup sequences, and safety checks.

---

## Calibration Overview

### XY Offset Calibration (NUDGE)

Each tool's nozzle position differs slightly from the others. XY offsets compensate for these differences.

**Automated workflow:**
```gcode
G28                                    # Home
SET_INITIAL_TOOL TOOL=0                # Choose reference tool (any tool)
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0 # Automated XY calibration
```

**What happens:**
1. System picks up reference tool
2. Prints calibration patterns with reference tool
3. Picks each other tool in sequence
4. User manually aligns each tool to reference patterns using NUDGE
5. System calculates and stores XY offsets
6. Configuration saved via SAVE_CONFIG

**Time:** ~30-45 minutes for 6 tools

---

### Z Offset Calibration (Beacon)

Each tool's Z position relative to the bed differs slightly. Z offsets compensate for these differences.

**Automated workflow:**
```gcode
G28                                    # Home
SET_INITIAL_TOOL TOOL=0                # Reference tool (same as XY calibration)
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0  # Automated Z calibration
```

**What happens:**
1. System homes and heats tools
2. For each tool:
   - Pick up tool
   - Move to calibration position
   - Use Beacon contact to measure Z position
   - Store offset relative to reference tool
3. Configuration saved via SAVE_CONFIG

**Time:** ~30-45 minutes for 6 tools

---

## Common Questions

### "Do I need all 6 tools configured?"

No. You can run with fewer tools by:
- Commenting out unused tool includes in printer.cfg
- Adjusting tool count in toolchanger.cfg
- Only calibrating the tools you're using

The configuration scales from 2 to 6+ tools.

---

### "Can I use this with different toolheads?"

Possibly, but requires modifications:
- Dock designs must physically fit your toolheads
- Pickup/dropoff sequences may differ
- Tool detection sensor locations may change
- Movement paths need adjustment
- Weights affect speeds and accelerations

If your hardware is significantly different, you may be better served by starting with the viesturz base and building custom configs.

---

### "What if I don't have CPAP cooling?"

The CPAP cooling is specific to this hardware reference. If you have:
- Per-tool fans: Configure them in each tool's config
- Different shuttle cooling: Adjust macros accordingly
- No shuttle cooling: Remove those configuration sections

The cooling system is hardware-specific and easily adapted.

---

### "Is this plug-and-play?"

**No.** This provides:
- Working configuration for specific hardware
- All necessary macros and safety features
- Documented calibration workflows

You must still:
- Build the physical toolchanger
- Adjust all dock positions for your machine
- Set your specific CAN UUIDs and sensor pins
- Calibrate XY and Z offsets
- Tune speeds and accelerations
- Test thoroughly before production use

This significantly reduces configuration work but doesn't eliminate it.

---

### "How often do I need to recalibrate?"

**Recalibration typically needed:**
- After changing a nozzle
- After adjusting dock positions
- After replacing or modifying a tool
- After significant maintenance (belt changes, etc.)
- If print quality degrades with specific tools

**Recalibration usually NOT needed:**
- Between prints with the same tools
- After filament changes
- After normal successful prints
- After minor bed tramming

**Z-offset drift** is normal over time. Periodic recalibration (weekly/monthly depending on usage) maintains optimal first layer quality.

---

## Design Credits

This project builds on work by many contributors:

**Core Framework:**
- viesturz/klipper-toolchanger - Original implementation and fundamental logic

**Hardware Design Influences:**
- **ATOM Toolhead** - Custom-designed by Alex at APDMachine (creator of Reaper Toolhead)
- **Shuttle Mechanism** - Based on ClickChanger/Stealthchanger pin-and-bushing concepts
- **Dock Design** - Inspired by Modular Docks, redesigned for this application

**This Fork:**
- Additional safety features, complete configuration, and documentation by PrintStructor

---

## Next Steps

**If this fork matches your needs:**
1. Review the [QUICKSTART.md](QUICKSTART.md) guide
2. Check hardware requirements in [ATOM Example Config](../examples/atom-tc-6tool/README.md)
3. Follow installation instructions in [CONFIGURATION.md](CONFIGURATION.md)
4. Complete calibration via [CALIBRATION.md](CALIBRATION.md)

**If you're unsure:**
- Compare with other toolchanger projects
- Review the complete configuration in `examples/atom-tc-6tool/`
- Ask questions in community forums
- Consider your hardware compatibility

**If this doesn't match your needs:**
- Explore viesturz/klipper-toolchanger for maximum flexibility
- Look at TypQxQ implementations for different approaches
- Build a custom solution for your specific hardware

All paths are valid - choose what works best for your project.

---

**Last updated:** 2025-11-20  
**Version:** 1.0.0
