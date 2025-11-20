# Feature Comparison

## Overview

This document compares the features of klipper-toolchanger-extended with other Klipper toolchanger implementations. The goal is to help you understand which solution best fits your specific needs and hardware.

**Note:** All projects mentioned here are valuable contributions to the Klipper toolchanger ecosystem. This comparison focuses on technical differences, not quality judgments.

---

## Projects Compared

**viesturz/klipper-toolchanger**
- Original implementation by viesturz
- Provides core toolchanger logic and framework
- Flexible abstraction for various hardware configurations
- Minimal, toolkit-style approach

**TypQxQ toolchanger implementations**
- Alternative architectural approach
- Virtual tool support
- Different configuration style
- Focus on flexibility and MMU-style systems

**klipper-toolchanger-extended (this fork)**
- Extension of viesturz base
- Additional safety features
- Complete reference configuration
- Specific hardware focus (ATOM toolheads)

---

## Feature Comparison Table

| Feature Category | viesturz base | TypQxQ | This Fork |
|------------------|---------------|--------|-----------|
| **Core Functionality** | | | |
| Tool state management | ✅ | ✅ | ✅ |
| Pickup/dropoff sequences | ✅ | ✅ | ✅ |
| Tool offset handling | ✅ | ✅ | ✅ |
| Configuration framework | ✅ | ✅ | ✅ |
| **Safety Features** | | | |
| Two-stage pickup verification | ❌ | ❌ | ✅ |
| Tool presence monitoring | ❌ | ❌ | ✅ |
| Pause-based error handling | ⚠️ Basic | ✅ | ✅ |
| Heater shutoff on tool loss | ❌ | ❌ | ✅ |
| **Calibration** | | | |
| Manual XY calibration | ✅ | ✅ | ✅ |
| Guided XY calibration | ❌ | ❌ | ✅ |
| Manual Z calibration | ✅ | ✅ | ✅ |
| Guided Z calibration | ❌ | ❌ | ✅ |
| Per-tool input shaper | ❌ | ❌ | ✅ |
| **Configuration** | | | |
| Example configs | ⚠️ Minimal | ⚠️ Basic | ✅ Complete |
| Pre-configured macros | ⚠️ Basic | ⚠️ Basic | ✅ Comprehensive |
| Hardware documentation | ⚠️ Generic | ⚠️ Generic | ✅ Specific |
| **Recovery & Monitoring** | | | |
| Error recovery macros | ❌ | ⚠️ Limited | ✅ Full set |
| LED status integration | ❌ | ❌ | ✅ |
| Display integration | ❌ | ❌ | ✅ (KNOMI) |
| **Hardware Support** | | | |
| Generic hardware | ✅ | ✅ | ✅ |
| Specific reference design | ❌ | ❌ | ✅ (ATOM) |
| Virtual tools | ❌ | ✅ | ❌ |
| MMU-style systems | ⚠️ Possible | ✅ | ❌ |

**Legend:**
- ✅ = Fully supported
- ⚠️ = Partially supported or possible with modifications
- ❌ = Not included

---

## Detailed Feature Differences

### Two-Stage Pickup Verification

**viesturz/TypQxQ:** Tool pickup happens in one continuous motion. If alignment is off or sensors fail, the issue is discovered after the tool has already moved away from the dock.

**This fork:** Adds an intermediate verification step:
1. Approach dock and partially engage
2. Check tool detection sensor
3. Complete engagement only if verified
4. Abort if verification fails

**When this helps:** Catches misalignment, sensor issues, or mechanical problems before committing to moves with an unverified tool.

---

### Tool Presence Monitoring

**viesturz/TypQxQ:** Tool state is updated during pickup/dropoff operations but not continuously monitored during printing.

**This fork:** Adds background monitoring that checks tool presence during prints. If tool loss is detected:
- Pause immediately
- Shut off heater
- Move to safe height
- Alert user

**When this helps:** Prevents crashes if a tool becomes detached during printing due to mechanical issues or improper engagement.

---

### Calibration Workflows

**viesturz/TypQxQ:** Provides manual calibration procedures - measure offsets with calipers or test prints, edit config files manually, restart Klipper, test results.

**This fork:** Adds command-driven calibration:
- `NUDGE_FIND_TOOL_OFFSETS` - Interactive XY calibration with live adjustment
- `MEASURE_TOOL_Z_OFFSETS` - Automated Z calibration using Beacon probe
- Results saved directly via SAVE_CONFIG
- No manual file editing required

**Time comparison:**
- Manual calibration: ~45-60 minutes per tool (measure, edit, test, repeat)
- Guided calibration: ~5-10 minutes per tool (run command, verify, done)

For 6 tools, this reduces initial calibration from ~4-6 hours to ~30-60 minutes total.

---

### Configuration Completeness

**viesturz:** Provides core modules and minimal example configs. Users build their complete configuration from these foundations.

**TypQxQ:** Provides core modules and basic example configs with different architectural approach.

**This fork:** Provides complete, ready-to-adapt configuration including:
- All safety macros pre-configured
- LED status integration
- Display integration (KNOMI)
- Recovery procedures
- Complete 6-tool printer.cfg example
- Documented hardware specifications

**Trade-off:** More complete examples mean less flexibility for custom implementations. Choose based on whether you want a starting point close to your hardware (this fork) or maximum customization freedom (base projects).

---

### Error Recovery

**viesturz:** Basic error handling, mostly relies on emergency stops for failures.

**TypQxQ:** Better error handling with pause capabilities, but limited recovery documentation.

**This fork:** Structured recovery system with:
- Pre-defined recovery macros for common failures
- Preserved print state during pauses
- Documented recovery procedures
- Ability to resume after fixing issues

**Example scenarios:**
- Tool not fully seated after pickup → Pause, re-pick tool, resume
- Tool lost mid-print → Pause, replace tool, rehome, resume
- Dock misalignment → Pause, adjust dock, clear error, resume

---

### Hardware Specificity

**viesturz/TypQxQ:** Generic frameworks designed to work with any hardware through configuration. No specific hardware reference designs.

**This fork:** Specifically designed for and tested with:
- VORON 2.4 CoreXY
- ATOM toolheads (6 tools)
- CPAP shuttle cooling
- Beacon probe
- Pin-and-bushing dock mechanism

**Trade-off:** If your hardware matches the reference design, setup is faster. If your hardware is completely different, you may benefit more from the flexibility of base projects.

---

## Which Project Should You Choose?

### Choose viesturz/klipper-toolchanger if:

✅ You have completely custom hardware  
✅ You want maximum flexibility in implementation  
✅ You prefer building from minimal frameworks  
✅ You enjoy designing your own macro structure  
✅ Your hardware doesn't match any reference design

**Best for:** Custom builds, unique hardware, maximum control

---

### Choose TypQxQ implementations if:

✅ You need virtual tool support  
✅ You're building MMU-style systems  
✅ You prefer their architectural approach  
✅ You want different tool management philosophy  
✅ Your use case benefits from their specific features

**Best for:** Virtual tools, MMU systems, alternative approaches

---

### Choose klipper-toolchanger-extended (this fork) if:

✅ You're building a 6-tool VORON with ATOM-style toolheads  
✅ You want complete example configuration  
✅ You value additional safety features  
✅ You want guided calibration procedures  
✅ You prefer adapting existing configs over building from scratch

**Best for:** ATOM-based builds, VORON printers, users wanting comprehensive starting configs

---

## Configuration Time Comparison

These are realistic estimates based on actual experience:

### Initial Setup (Software Only)

**With viesturz base:**
- Understanding framework: 2-4 hours
- Writing macros: 4-8 hours
- Implementing safety checks: 2-4 hours
- Testing and debugging: 4-8 hours
- **Total: 12-24 hours**

**With this fork:**
- Copying configs: 30 minutes
- Adjusting dock positions: 1-2 hours
- Setting CAN UUIDs and pins: 30 minutes
- Testing basic pickup/dropoff: 1-2 hours
- **Total: 3-5 hours**

**Time saved: ~8-19 hours**

*Note: These times assume you already have the physical hardware built and mechanically working.*

---

### Calibration Time

**Manual calibration (viesturz/TypQxQ default):**
- Per tool: 45-60 minutes
- 6 tools: 4.5-6 hours

**Guided calibration (this fork):**
- Per tool: 5-10 minutes
- 6 tools: 30-60 minutes

**Time saved: ~3-5 hours per full calibration**

*Note: Recalibration is periodic (after nozzle changes, maintenance, etc.)*

---

### Error Recovery Time

**Without recovery features:**
- Error occurs → Print fails → Start over
- Lost time: Entire print (could be hours or days)

**With recovery features:**
- Error occurs → Pause → Fix issue → Resume
- Lost time: 2-10 minutes (depending on issue)

**Value: Depends on print length and frequency of recoverable errors**

For a 20-hour multi-tool print, a single recoverable error saves 20 hours. However, the frequency of such errors depends heavily on your mechanical setup quality and maintenance.

---

## Migration Considerations

### From viesturz to this fork:

**Easy:** You're already familiar with the base framework, just adding safety features and complete configs.

**Steps:**
1. Review this fork's additional safety features
2. Decide which features you want to adopt
3. Copy relevant macros and configs
4. Adjust for your hardware
5. Test thoroughly

---

### From TypQxQ to this fork:

**Moderate:** Different architectural approach requires more substantial changes.

**Consider:**
- Do you need virtual tool support? (This fork doesn't provide it)
- Is your hardware compatible with this fork's reference design?
- Are you willing to restructure your configuration?

If yes to all three, migration is feasible. If no to any, staying with TypQxQ or using viesturz base may be better.

---

### From custom solution to this fork:

**Variable:** Depends on how much your custom solution diverges from this fork's approach.

**Evaluate:**
1. Compare your current features with this fork's features
2. Determine which additional features you want
3. Assess compatibility with your hardware
4. Consider effort to migrate vs. effort to maintain custom solution

---

## Performance Considerations

### Toolchange Speed

All three solutions can achieve similar toolchange speeds - this is primarily determined by:
- Hardware mechanics (dock precision)
- Movement speeds in configuration
- Acceleration limits

**This fork does NOT claim faster toolchanges** - the two-stage verification adds a small delay (typically 0.5-1 second) but increases reliability.

---

### Reliability

Reliability depends on:
1. Mechanical quality of hardware
2. Sensor reliability
3. Software error handling

This fork's additional verification and monitoring features improve software-side reliability, but cannot compensate for poor mechanical design or unreliable sensors.

---

## Realistic Expectations

**What this fork provides:**
- More comprehensive error detection
- Better recovery options when errors occur
- Faster initial setup with complete configs
- Guided calibration procedures

**What this fork does NOT provide:**
- Magical reliability improvements without good hardware
- Faster toolchanges than other implementations
- Elimination of all possible failures
- Plug-and-play operation without configuration

---

## Conclusion

All three approaches (viesturz base, TypQxQ, and this fork) are valid solutions with different strengths:

- **viesturz** = Maximum flexibility, minimal framework
- **TypQxQ** = Virtual tool support, alternative architecture
- **This fork** = Complete configs, additional safety, specific hardware focus

Choose based on:
1. Your hardware setup
2. Your experience level with Klipper
3. Your preference for flexibility vs. completeness
4. Your specific feature requirements

**No single solution is "best"** - they serve different needs and use cases.

---

**Last updated:** 2025-11-20  
**Version:** 1.0.0
