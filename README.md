# Klipper Toolchanger Extended

**Version:** 1.0.0  
**Author:** PrintStructor  
**License:** GPL-3.0  
**Original Project:** [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)

> Production-ready toolchanger system for Klipper with advanced safety features, robust error handling, and complete configuration examples.

---

## 🎯 What Makes This Special

Klipper Toolchanger Extended is an **enhanced fork** of Viesturs Zarins' excellent klipper-toolchanger project, transformed into a complete, production-tested system with focus on **reliability and safety**.

### 🛡️ Unique Safety Features

**Two-Stage Tool Pickup**
- Verifies tool presence **before** completing pickup
- Prevents crashes from false detections
- Catches mechanical issues early

**Non-Fatal Error Handling**
- Pauses print instead of emergency shutdown
- Allows manual intervention and recovery
- Automatic position and temperature restoration

**Continuous Tool Monitoring**
- Real-time presence detection during printing
- Automatic pause if tool drops mid-print
- Safety shutoff of heater on tool loss

**Smart Recovery System**
- One-command recovery with `RESUME`
- Automatic position restoration
- Temperature state preserved

### 🚀 Production Focus

Unlike other toolchanger solutions, this project provides:

✅ **Complete Configuration** - Not just modules, but full working examples  
✅ **Hardware Integration** - Tested with ATOM toolhead system  
✅ **Safety First** - Multiple layers of error detection and recovery  
✅ **Easy Updates** - Moonraker integration for automatic updates  
✅ **Well Documented** - Comprehensive guides and examples  
✅ **Community Tested** - Production-proven on real multi-tool printers

---

## Hardware

### ATOM Toolhead System

This project features the **ATOM toolhead** - an exclusive design created by the developer of the **Reaper Toolhead**, specifically engineered for this toolchanger project.

**Key Features:**
- **Simple 4-Point Dock Path** - Reliable and easy to calibrate
- **Compact Design** - Space-efficient for 6-tool arrays
- **Production Tested** - Proven in high-volume printing
- **CAN Bus Ready** - Designed for BTT EBB36/42 boards
- **Tool Detection Integration** - Built-in sensor mounting

**Reference Hardware:**
- 6x ATOM toolheads with BTT EBB36/42 CAN boards
- NUDGE probe for XY offset calibration
- Beacon RevH probe for Z calibration and bed meshing
- Per-tool filament detection sensors
- Optional: KNOMI displays, LED effects

**Hardware Files:**
CAD files and STL files for the ATOM toolhead will be available in the [`hardware/`](hardware/) directory. See [hardware documentation](hardware/README.md) for details.

---

## 📦 What's Included

### Python Modules (Klipper Extensions)

Complete set of Klipper modules for advanced toolchanger operation:

- **`toolchanger.py`** - Core two-stage pickup logic with error handling
- **`tool.py`** - Individual tool management and detection states
- **`tools_calibrate.py`** - NUDGE probe XY offset calibration
- **`rounded_path.py`** - Smooth curved motion paths
- **`tool_probe.py`** - Per-tool Z probe support
- **`tc_beacon_capture.py`** - Beacon contact Z-offset capture
- **`bed_thermal_adjust.py`** - Thermal compensation for long prints
- **`manual_rail.py`** - Manual rail control utilities
- **`multi_fan.py`** - Advanced multi-fan controller
- Plus additional helper modules

### Configuration Examples

**Complete 6-Tool ATOM Reference:**
- Full working configuration in [`examples/atom-tc-6tool/`](examples/atom-tc-6tool/)
- Individual tool configs (T0-T5)
- Print lifecycle macros (PRINT_START, PRINT_END, PAUSE, RESUME)
- Calibration workflows (XY with NUDGE, Z with Beacon)
- LED status visualization
- KNOMI display integration
- OrcaSlicer setup guide

### Documentation

- **[Main Documentation Hub](docs/README.md)** - Central navigation
- **[Hardware Documentation](hardware/README.md)** - CAD files and assembly
- **[ATOM Reference Guide](examples/atom-tc-6tool/README.md)** - Complete setup guide
- **[Changelog](CHANGELOG.md)** - Version history and changes
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

---

## 🚀 Quick Start

### Requirements

- **Klipper:** v0.11.0 or newer
- **Python:** 3.7+ (included with Klipper)
- **Hardware:** Multi-tool/toolchanger 3D printer
- **Sensors:** Tool detection strongly recommended
- **Host:** Raspberry Pi or similar Linux SBC

### Installation

**1. Clone the repository:**
```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended
```

**2. Run installation script:**
```bash
./install.sh
```

The script will:
- Symlink Python modules to Klipper extras
- Offer to configure Moonraker auto-updates
- Restart Klipper service

**3. Add to your printer.cfg:**
```ini
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger_macros.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/macros.cfg]
# ... add tool configs T0-T5 ...
```

**4. Customize for your hardware:**
- Update dock positions in each `TX.cfg`
- Set CAN UUIDs for your toolhead boards
- Configure probe offsets
- Adjust movement speeds

**5. Calibrate:**
```gcode
G28                                    # Home
SET_INITIAL_TOOL TOOL=0                # Set reference tool
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0 # Calibrate XY
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0  # Calibrate Z
```

**For detailed setup, see:** [ATOM Example Configuration Guide](examples/atom-tc-6tool/README.md)

---

## 📖 Key Concepts

### Tool Detection States

Tools have three detection states:
- **PRESENT** (1) - Tool is detected and ready
- **ABSENT** (0) - Tool is not detected
- **UNAVAILABLE** (-1) - Detection sensor not configured

### Offset System

Three-tier offset management:

1. **Global Z-Offset** - Applied to initial tool (typically 0.06-0.12mm)
2. **Relative XY-Offsets** - Per tool, relative to initial tool
3. **Relative Z-Offsets** - Per tool, relative to initial tool

The initial tool always has XY=0,0 and relative Z=0.

### Two-Stage Pickup

**Stage 1: Approach & Verify**
```
1. Move to dock
2. Partially insert tool
3. Check detection sensor at verification point
4. If not detected → Error, pause
```

**Stage 2: Complete (only if Stage 1 succeeds)**
```
1. Complete insertion
2. Return to safe position
3. Restore previous position
4. Continue operation
```

### Error Recovery

**When tool change fails:**
1. Print automatically pauses
2. Z-axis lifts to safe height
3. Extruder heater turns off
4. LED shows error status (if configured)

**To recover:**
1. Fix mechanical issue
2. Run `RESUME` command
3. System restores temperature and position
4. Print continues

---

## 🎓 Documentation

### Getting Started
- **[Installation Guide](#installation)** - This page
- **[ATOM Example Setup](examples/atom-tc-6tool/README.md)** - Complete reference
- **[Quick Start Video](#)** - Coming soon

### Configuration Reference
- **[Toolchanger Module](docs/toolchanger.md)** - Core configuration
- **[Tools Calibrate](docs/tools_calibrate.md)** - XY offset calibration
- **[Tool Probe](docs/tool_probe.md)** - Per-tool probe setup
- **[Rounded Path](docs/rounded_path.md)** - Motion path configuration

### Advanced Topics
- **[Custom Dock Paths](docs/tool_paths.md)** - Creating custom paths
- **[Error Handling](docs/toolchanger.md#error-handling)** - Understanding errors
- **[LED Integration](examples/atom-tc-6tool/README.md#led-effects)** - Status visualization

### Support & Community
- **[GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)** - Bug reports
- **[GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)** - Q&A and ideas
- **[Contributing Guide](CONTRIBUTING.md)** - Help improve the project

---

## 🔄 Updates & Versioning

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR** - Incompatible API changes
- **MINOR** - New features (backwards-compatible)
- **PATCH** - Bug fixes (backwards-compatible)

### Automatic Updates (Moonraker)

**Setup during installation:**
The `install.sh` script offers to configure Moonraker update manager.

**Manual setup:**
Add to your `moonraker.conf`:
```ini
[update_manager klipper-toolchanger-extended]
type: git_repo
path: ~/klipper-toolchanger-extended
origin: https://github.com/PrintStructor/klipper-toolchanger-extended.git
primary_branch: main
managed_services: klipper
install_script: install.sh
```

See [`moonraker.conf`](moonraker.conf) for detailed configuration.

**Update via Mainsail/Fluidd:**
1. Navigate to "Machine" tab
2. Check for updates
3. Click "Update" button
4. System automatically restarts Klipper

### Manual Updates

```bash
cd ~/klipper-toolchanger-extended
git pull
./install.sh
sudo systemctl restart klipper
```

### Rollback

If an update causes issues:
```bash
cd ~/klipper-toolchanger-extended
git log                  # Find previous version
git checkout v1.0.0      # Or specific commit
./install.sh
sudo systemctl restart klipper
```

### Release Channels

- **`main` branch** - Stable releases only (recommended)
- **`develop` branch** - Beta features and testing
- **`feature/*` branches** - Specific feature development

To switch to develop branch for beta testing:
```bash
cd ~/klipper-toolchanger-extended
git checkout develop
git pull
./install.sh
```

---

## 🤝 Contributing

Contributions are welcome! This project thrives on community input.

### How to Contribute

- **Report bugs** - Use [bug report template](https://github.com/PrintStructor/klipper-toolchanger-extended/issues/new?template=bug_report.md)
- **Suggest features** - Use [feature request template](https://github.com/PrintStructor/klipper-toolchanger-extended/issues/new?template=feature_request.md)
- **Improve docs** - Fix typos, add examples, clarify instructions
- **Submit code** - Fork, branch, code, test, pull request
- **Share configs** - Contribute working setups for different printers

**Read the full guide:** [CONTRIBUTING.md](CONTRIBUTING.md)

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

---

## 🙏 Credits

### Original Framework
**Viesturs Zarins** (viesturz)  
Original klipper-toolchanger project  
[github.com/viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)

### ATOM Toolhead
**Creator of the Reaper Toolhead**  
Exclusive design for this project  
[reapertoolhead.com](https://reapertoolhead.com)

### NUDGE Probe
**Zruncho** (zruncho3d)  
Automatic XY offset calibration probe  
[github.com/zruncho3d/nudge](https://github.com/zruncho3d/nudge)

### Extended Features
**PrintStructor**  
Safety features, error handling, production integration  
[github.com/PrintStructor](https://github.com/PrintStructor)

---

## 📄 License

This project is licensed under **GPL-3.0**, consistent with the original klipper-toolchanger project.

**You are free to:**
- Use for personal or commercial purposes
- Modify and adapt
- Distribute and share

**Under the conditions:**
- Maintain GPL-3.0 license
- Share modifications under same license
- Credit original authors

See [LICENSE](LICENSE) for full details.

---

## 🔗 Related Projects

### Integration Projects
- **[orcaslicer-tool-shutdown](https://github.com/PrintStructor/orcaslicer-tool-shutdown)** - Automatic hotend shutdown after last use
- **[Beacon](https://beacon3d.com/)** - Eddy current probe for Z calibration
- **[KNOMI](https://github.com/bigtreetech/KNOMI)** - Round display integration

### Community Resources
- **[VORON Design](https://vorondesign.com/)** - CoreXY printer designs
- **[Klipper Documentation](https://www.klipper3d.org/)** - Official Klipper docs
- **[r/VORONDesign](https://reddit.com/r/VORONDesign)** - Reddit community

---

## 📊 Project Stats

- **Version:** 1.0.0
- **License:** GPL-3.0
- **Python Modules:** 12
- **Example Configs:** Complete 6-tool VORON reference
- **Documentation Pages:** 10+
- **Production Status:** ✅ Tested and Stable

---

## 🎉 Acknowledgments

Special thanks to:
- The entire Klipper community
- VORON Design team for inspiration
- Early testers and contributors
- Everyone who provides feedback and bug reports

---

**Ready to get started?** See the [Installation](#installation) section above or jump straight to the [ATOM Example Configuration](examples/atom-tc-6tool/README.md)!

---

**Questions?** Check out [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions) or open an [issue](https://github.com/PrintStructor/klipper-toolchanger-extended/issues).
