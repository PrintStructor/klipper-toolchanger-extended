# Documentation Index

This directory contains detailed documentation for all modules in the klipper-toolchanger project.

## Core Modules

### [toolchanger.md](toolchanger.md)
Main toolchanger module documentation. Covers:
- Tool management and coordination
- Two-stage pickup/dropoff system
- Error handling and recovery
- Offset management
- Status tracking

### [tool.py Documentation](toolchanger.md#tool-configuration)
Individual tool configuration and parameters:
- Tool detection
- Extruder and fan management
- Per-tool offsets (XY and Z)
- Recovery procedures

### [tools_calibrate.md](tools_calibrate.md)
Tool offset calibration system:
- XY offset calibration (NUDGE probe)
- Z offset calibration (Beacon contact)
- Initial tool tracking
- Auto-save to config

## Additional Modules

### [tool_probe.md](tool_probe.md)
Per-tool Z-probe support:
- Individual probe pins per tool
- Probe offset management
- Multi-sample probing
- Crash detection

### [rounded_path.md](rounded_path.md)
Smooth travel path generation:
- Cornering optimization
- Speed change reduction
- Arc segment generation
- G0 move replacement

### [bed_thermal_adjust.md](bed_thermal_adjust.md)
Heated bed thermal compensation:
- Temperature loss compensation
- Chamber temperature sensing
- Dynamic target adjustment

### [manual_rail.md](manual_rail.md)
Manual stepper rail control:
- Multi-stepper coordination
- Homing support
- Position management

## Diagrams

### Tool Change Lifecycle
![Lifecycle Diagram](images/Lifecycle.png)

Shows the complete state machine for tool changes, including:
- Initialization
- Tool selection
- Error handling
- Recovery procedures

### Tool Change Sequence
![Sequence Diagram](images/Sequence.png)

Illustrates the detailed sequence of operations during a tool change:
- Stage 1: Approach and detection
- Stage 2: Final insertion
- Position restoration
- Offset application

## Configuration Examples

For complete configuration examples, see the [examples](../examples/) directory.

## Quick Links

- [Main README](../README.md)
- [Installation Guide](../README.md#installation)
- [Configuration Examples](../examples/)
- [GitHub Repository](https://github.com/PrintStructor/klipper-toolchanger)
