# Changelog

All notable changes to Klipper Toolchanger Extended will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **TAXY Integration** – AI-based XY calibration as primary method
  - YOLOv8 nozzle detection with ~5µm precision
  - More robust than OpenCV blob detection across lighting conditions
  - [TAXY GitHub](https://github.com/PrintStructor/TAXY)
  - kTAMV remains as legacy/fallback option

### Fixed
- **Initial Tool Z-Offset Bug** (`toolchanger.py`)
  - Initial/reference tool now correctly gets Z-offset of 0.0
  - Previously could inherit non-zero offset from config causing incorrect first layer
  - Added explicit check: `if tool == self.initial_tool: z_offset = 0.0`
  - Ensures initial tool is always the true reference point (Z=0)

- **Thermal Offset Integration** (`macros.cfg`)
  - Fixed PRINT_START macro overwriting thermal expansion compensation
  - `APPLY_NOZZLE_TEMP_OFFSET` now runs AFTER `SET_INITIAL_TOOL`
  - Previously thermal offset was set then immediately cleared by tool initialization
  - Thermal compensation now properly visible in UI and applied to prints

### Planned Features
- Additional dock path profiles (PADS, RODS variations)
- Automatic backup system for configuration
- Web-based calibration wizard
- Multi-printer configuration templates

---

## [1.1.0] - 2026-01-10

### ✨ New Features

#### Batch Calibration Macros
- **`KTAMV_CALIBRATE_ALL_TOOLS_XY`** – Full XY calibration matrix using kTAMV camera
  - Each tool used as initial tool, measures all others
  - 6 × 5 = 30 offset measurements in one run
  - Automatic camera setup per initial tool
- **`BEACON_CALIBRATE_ALL_TOOLS_Z`** – Full Z calibration matrix using Beacon
  - Each tool used as initial tool, measures all others
  - 6 × 5 = 30 Z-offset measurements in one run
  - Automatic heating to 150°C per tool

#### Per-Tool Z Babystepping
- **`SET_TOOL_Z_ADJUST`** – Live Z-offset adjustments during printing
  - Adjustments stored in RAM (no SD card writes during print)
  - Applied immediately if tool is currently active
  - Works for ALL tools including initial/reference tool
- **`SHOW_TOOL_Z_ADJUSTMENTS`** – Display current vs. calibrated offsets
- **`SAVE_TOOL_Z_ADJUSTMENTS`** – Persist adjustments via SAVE_CONFIG
- **`CHECK_TOOL_Z_ADJUSTMENTS`** – For PRINT_END integration

#### Global Z-Offset
- **`GLOBAL_Z_ADJUST`** – Adjust Z-offset for ALL tools equally
  - Perfect for first-layer tuning across all tools
  - `Z=+0.01` / `Z=-0.01` for fine adjustments
  - `RESET=1` to return to 0.0

#### kTAMV Integration (Camera-based XY Calibration)
- Primary XY calibration method using computer vision
- Integration with [kTAMV](https://github.com/PrintStructor/kTAMV) by TypQxQ
- Step-by-step and batch calibration workflows
- Automatic offset saving to printer.cfg

### 📦 New Python Modules
- **`tool_xy_calibration.py`** – XY offset saving for kTAMV integration
  - `SAVE_TOOL_XY_OFFSET` – Manual XY offset save
  - `KTAMV_AUTO_SAVE_OFFSET` – Auto-save from kTAMV measurements
  - `SHOW_TOOL_XY_OFFSETS` – Display calibrated offsets
- **`tool_z_adjust.py`** – Per-tool Z babystepping module
  - Live adjustments without config writes
  - Session tracking for unsaved changes
  - Reset to calibrated values

### 🔧 Improvements

#### Initial Tool Handling
- Initial tool now gets explicit 0.0 Z-offset saved during calibration
- Enables proper babystepping for reference tool
- Symmetric treatment of all tools (no special-casing T0)

#### Calibration Workflows
- Improved kTAMV workflow documentation
- NUDGE remains as backup method when camera unavailable
- Clearer separation between camera-based and probe-based methods

### 📚 Documentation
- Updated README with kTAMV credits and integration info
- Added kTAMV to External Dependencies section
- Updated example config structure (removed shell_command.cfg)
- New calibration command reference in tool_calibration.cfg

### 🗑️ Removed
- `shell_command.cfg` – No longer needed (calibration uses native Python)
- `calibrate_offsets.cfg` – Replaced by `tool_calibration.cfg`

### 🙏 Credits
- **kTAMV** by TypQxQ – Camera-based XY calibration (GPL-3.0)
- **NUDGE** by Zruncho – Physical probe XY calibration (backup method)

---

## [1.0.1] - 2025-11-26

### Fixed
- Fixed pause/resume state corruption in error recovery when tool loss occurs
  after a failed pickup (tool loss now correctly pauses the print again)
- Fixed Z-offset being effectively applied twice during recovery by correcting
  `extra_z_offset = current_z_offset - (tool_z_offset + global_z_offset)`
- Prevented tool loss alarms from triggering on manual tool changes after a
  finished or cancelled print by checking `virtual_sdcard.is_active()` and
  `pause_resume.is_paused` before handling tool loss
  
## [1.0.0] - 2025-11-18

### 🎉 Initial Release

First stable release of Klipper Toolchanger Extended - a production-ready, enhanced fork of viesturz/klipper-toolchanger with advanced safety features and robust error handling.

### ✨ Major Features

#### Safety & Reliability
- **Two-Stage Tool Pickup System**
  - Stage 1: Partial insertion with verification
  - Stage 2: Complete insertion only after successful detection
  - Prevents crashes from false detections or mechanical failures
  
- **Non-Fatal Error Handling**
  - Tool change errors pause print instead of emergency shutdown
  - Allows manual intervention and recovery
  - Automatic position and temperature restoration
  
- **Continuous Tool Presence Monitoring**
  - Real-time monitoring during printing
  - Automatic pause if tool drops mid-print
  - Safety: Heater turned off immediately on tool loss
  
- **Smart Recovery System**
  - `RESUME` command with automatic position restore
  - Saved temperature restoration after errors
  - Graceful recovery from tool change failures

#### Calibration & Offsets
- **XY-Offset Matrix Support**
  - Dynamic offset storage per tool (up to 6 tools)
  - Relative offsets between any tool pairs
  - Automatic offset application during tool changes
  
- **Enhanced Calibration Workflow**
  - Separate XY calibration (NUDGE probe integration)
  - Separate Z calibration (Beacon contact mode)
  - Auto-save to config via shell scripts
  - Initial tool tracking for relative measurements
  
- **Three-Tier Offset System**
  - Global Z-offset for initial tool
  - Relative XY-offsets per tool
  - Relative Z-offsets per tool

#### Advanced Features
- **Per-Tool Configuration**
  - Individual Input Shaper settings per tool
  - Tool-specific parameters and properties
  - Convenience properties for stage access
  
- **Improved Motion Control**
  - Rounded path module integration
  - Restore position with stage-based returns
  - Smooth transitions between states
  
- **Enhanced M-Code Support**
  - M104/M109 with T parameter for multi-tool temperature control
  - M106/M107 with P/T parameter for per-tool fan control

#### Hardware Integration
- **ATOM Toolhead Support**
  - Exclusive design by creator of Reaper Toolhead
  - Simple 4-point dock path
  - Production-tested on 6-tool VORON setup
  
- **Probe Integration**
  - NUDGE probe for XY calibration
  - Beacon RevH for Z calibration and bed meshing
  - Tool presence detection via filament sensors
  
- **LED Status Visualization**
  - Chamber and per-tool LED effects
  - Status feedback (ready, printing, heating, error)
  - Temperature visualization
  
- **KNOMI Display Support**
  - Smart sleep/wake via HTTP API
  - Automatic wake on activity
  - Power-efficient operation

### 📦 Python Modules

Core Klipper extensions included:

- `toolchanger.py` - Main toolchanger logic with two-stage pickup
- `tool.py` - Individual tool management with detection states
- `rounded_path.py` - Smooth curved motion paths
- `tools_calibrate.py` - XY offset calibration with NUDGE probe
- `tool_probe.py` - Per-tool probe support
- `tool_probe_endstop.py` - Tool probe endstop routing
- `tc_beacon_capture.py` - Beacon contact Z-offset capture
- `tc_config_helper.py` - Configuration save helpers
- `tc_save_config_value.py` - Shell script for config auto-save
- `bed_thermal_adjust.py` - Bed surface temperature compensation
- `manual_rail.py` - Manual rail movement utilities
- `multi_fan.py` - Multi-fan controller

### 📚 Documentation

- Comprehensive README with quick start guide
- Example configuration for 6-tool ATOM setup
- Hardware documentation structure
- OrcaSlicer integration guide
- Calibration workflow documentation
- Troubleshooting guides

### 🔧 Configuration Examples

Complete production-tested configuration included:

- `examples/atom-tc-6tool/` - Full 6-tool VORON reference
  - Core toolchanger configuration
  - Individual tool definitions (T0-T5)
  - Calibration macros
  - Print lifecycle macros
  - LED effects configuration
  - Beacon probe integration
  - KNOMI display integration

### 🛠️ Installation & Updates

- Automated installation script (`install.sh`)
- Moonraker update manager integration
- Interactive setup wizard for automatic updates
- Git-based version control

### 📋 Project Structure

```
klipper-toolchanger-extended/
├── klipper/extras/        # Python modules for Klipper
├── examples/              # Reference configurations
├── hardware/              # CAD files and STL structure
├── docs/                  # Documentation
├── install.sh             # Installation script
├── moonraker.conf         # Update manager config example
└── README.md              # Main documentation
```

### 🎯 What's Different from Original

This fork maintains compatibility with viesturz/klipper-toolchanger while adding:

1. **Production Focus** - Tested in real-world multi-tool printing
2. **Safety First** - Non-fatal error handling and recovery
3. **Complete Package** - Full configuration examples, not just modules
4. **Hardware Ready** - Specific ATOM toolhead integration
5. **Better UX** - LED feedback, display integration, smart monitoring
6. **Auto Updates** - Moonraker integration for easy maintenance

### 🙏 Credits

- **Original Toolchanger Framework:** Viesturs Zarins (viesturz)
- **ATOM Toolhead Design:** Creator of Reaper Toolhead
- **NUDGE Probe:** Zruncho (zruncho3d)
- **Enhanced Features & Integration:** PrintStructor

### 📄 License

GPL-3.0 - Same as original klipper-toolchanger project

---

## Version History

### Versioning Strategy

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Release Branches

- `main` - Stable releases only
- `develop` - Development branch for testing new features
- `feature/*` - Feature-specific branches

### How to Update

**Via Moonraker (Recommended):**
- Check for updates in Mainsail/Fluidd interface
- Click "Update" button
- System will automatically run install script

**Manual Update:**
```bash
cd ~/klipper-toolchanger-extended
git pull
./install.sh
sudo systemctl restart klipper
```

**Rollback if Needed:**
```bash
cd ~/klipper-toolchanger-extended
git log  # Find previous version
git checkout v1.0.0  # Or specific commit
./install.sh
sudo systemctl restart klipper
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting enhancements
- Submitting pull requests
- Code standards

---

## Support

- **Issues:** [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)
- **Discussions:** [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)
- **Documentation:** See `/docs` directory

---

[Unreleased]: https://github.com/PrintStructor/klipper-toolchanger-extended/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/PrintStructor/klipper-toolchanger-extended/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/PrintStructor/klipper-toolchanger-extended/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/PrintStructor/klipper-toolchanger-extended/releases/tag/v1.0.0