# Klipper Toolchanger - Enhanced Fork

**Author:** PrintStructor  
**GitHub:** https://github.com/PrintStructor  
**Original Project:** https://github.com/viesturz/klipper-toolchanger (by Viesturs Zarins)

---

## Overview

This is an enhanced fork of Viesturz's excellent klipper-toolchanger project, adding advanced features for production multi-tool printing with robust error handling and recovery systems.

### Base Project (Viesturz)

The original klipper-toolchanger by Viesturs Zarins provides the core framework for Klipper-based toolchangers, including:
- Multi-tool management and coordination
- Tool parking and retrieval sequences
- Offset calibration system (NUDGE probe integration)
- Flexible gcode templating

**Original Repository:** https://github.com/viesturz/klipper-toolchanger

---

## Key Enhancements (This Fork)

### 1. **Two-Stage Pickup System**
- **Stage 1:** Approach and partial insertion with verification
- **Stage 2:** Complete insertion only after successful tool detection
- Prevents crashes from false detections or mechanical failures

### 2. **Non-Fatal Error Handling**
- Tools report errors without shutting down Klipper
- Print pauses instead of emergency stop
- Allows manual intervention and recovery

### 3. **Tool Detection State Management**
- Three states: PRESENT, ABSENT, UNAVAILABLE
- Real-time monitoring during printing
- Automatic pause if tool drops

### 4. **XY-Offset Matrix Support**
- Dynamic offset storage per tool (up to 6 tools)
- Relative offsets between any tool pairs
- Automatic offset application during tool changes

### 5. **Advanced Recovery System**
- RESUME with automatic position restore
- Saved temperature restoration after error
- Graceful recovery from tool change failures

### 6. **Per-Tool Configuration**
- Individual Input Shaper settings per tool
- Tool-specific parameters and properties
- Convenience properties for stage access

### 7. **Enhanced Calibration Workflow**
- Separate XY calibration (NUDGE probe)
- Separate Z calibration (Beacon contact)
- Auto-save to config with shell scripts
- Initial tool tracking for relative measurements

### 8. **Improved Motion Control**
- Rounded path module integration
- Restore position with stage-based returns
- Smooth transitions between states

---

## Hardware Requirements

- Klipper firmware (v0.11.0+)
- Multi-tool setup with tool detection sensors
- NUDGE probe or similar for XY calibration
- Beacon probe (or equivalent) for Z calibration

---

## Installation

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger.git
```

### 2. Link Klipper Modules

```bash
cd ~/klipper-toolchanger
./install.sh
```

Or manually:
```bash
ln -sf ~/klipper-toolchanger/klipper/extras/*.py ~/klipper/klippy/extras/
```

### 3. Configure Klipper

Add to your `printer.cfg`:

```ini
[toolchanger]
# See example config files in printer_data/config/atom/
```

### 4. Restart Klipper

```bash
sudo systemctl restart klipper
```

---

## Configuration

See the example configuration in `/printer_data/config/atom/` for a complete 6-tool VORON setup including:

- `toolchanger.cfg` - Core toolchanger configuration
- `toolchanger_macros.cfg` - Essential operation macros
- `calibrate_offsets.cfg` - NUDGE & Beacon calibration
- `T0.cfg` through `T5.cfg` - Individual tool configurations
- `beacon.cfg` - Beacon probe configuration
- `tc_led_effects.cfg` - LED status visualization
- `knomi.cfg` - KNOMI display integration

---

## Quick Start

### 1. Define Tools

```ini
[tool T0]
tool_number: 0
extruder: extruder
detection_pin: ^et0:PB9
params_park_x: 25.3
params_park_y: 3.0
params_park_z: 325.0
```

### 2. Initialize Toolchanger

```gcode
SET_INITIAL_TOOL TOOL=0  ; Set T0 as reference tool
```

### 3. Select Tool

```gcode
T1  ; Switch to Tool 1
```

### 4. Calibrate Offsets

**XY Calibration (NUDGE):**
```gcode
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
```

**Z Calibration (Beacon):**
```gcode
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
```

**Save:**
```gcode
SAVE_CONFIG
```

---

## Error Recovery

If a tool change fails:

1. **Automatic:** Print pauses, displays error
2. **Manual:** Fix mechanical issue (reseat tool, clear jam, etc.)
3. **Resume:** Use `RESUME` command
   - Heater automatically restored to previous temperature
   - Position automatically restored
   - Printing continues

---

## Advanced Features

### Tool Presence Monitoring

Continuously monitors active tool during printing:

```gcode
; Automatically started by PRINT_START
UPDATE_DELAYED_GCODE ID=TOOL_PRESENCE_MONITOR DURATION=2.0
```

If tool drops mid-print:
- Heater turned off immediately (safety)
- Print pauses
- LED status shows error
- User notified

### Recovery System

```gcode
RESUME  ; Smart resume with:
        ; - Temperature restoration
        ; - Position restoration  
        ; - Automatic re-prime
```

### Calibration Mode

Disable offset application during calibration:

```python
SET_GCODE_VARIABLE MACRO=globals VARIABLE=toolchanger_calibration_mode VALUE=1
```

---

## Documentation

- **Configuration Guide:** `/printer_data/config/atom/README.md`
- **OrcaSlicer Setup:** `/printer_data/config/atom/ORCASLICER_SETUP.md`
- **Calibration Workflow:** See `calibrate_offsets.cfg` header
- **Python Module Docs:** See docstrings in `/klipper/extras/`

---

## Credits & License

### Original Author
**Viesturs Zarins** (viesturz)  
Original Project: https://github.com/viesturz/klipper-toolchanger  
License: GNU General Public License v3.0

### Enhanced Fork
**PrintStructor**  
Enhanced Fork: https://github.com/PrintStructor/klipper-toolchanger  
License: GNU General Public License v3.0

This project is licensed under the GNU General Public License v3.0. See LICENSE file for details.

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly on real hardware
4. Submit pull request with detailed description

---

## Support

- **Issues:** https://github.com/PrintStructor/klipper-toolchanger/issues
- **Discussions:** https://github.com/PrintStructor/klipper-toolchanger/discussions
- **Original Project:** https://github.com/viesturz/klipper-toolchanger

---

## Changelog

### v3.0 - Enhanced Fork
- Two-stage pickup system
- Non-fatal error handling
- Tool detection state management
- XY-offset matrix support
- Advanced recovery system
- Per-tool configuration
- Enhanced calibration workflow

### v2.x - Original (Viesturz)
- Base toolchanger functionality
- NUDGE probe integration
- Tool parking system
- Offset calibration

---

**⚠️ Hardware Note:** This fork is designed for and tested on VORON toolchanger setups with ATOM-style docks. Configuration may need adjustment for other dock systems (PADS, RODS, etc.).
