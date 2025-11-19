# Changelog

All notable changes to Klipper Toolchanger Extended will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned Features
- Additional dock path profiles (PADS, RODS variations)
- Automatic backup system for configuration
- Web-based calibration wizard
- Multi-printer configuration templates

---

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

[Unreleased]: https://github.com/PrintStructor/klipper-toolchanger-extended/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PrintStructor/klipper-toolchanger-extended/releases/tag/v1.0.0
