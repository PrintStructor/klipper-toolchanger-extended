# Documentation Overview

Welcome to the klipper-toolchanger-extended documentation!

---

## 🚀 Getting Started

**New to toolchangers? Start here:**

- [**⚡ Quick Start Guide**](QUICKSTART.md) - Get up and running in under an hour
- [**🔧 Configuration Guide**](CONFIGURATION.md) - Complete parameter reference and best practices
- [**📐 Calibration Guide**](CALIBRATION.md) - Step-by-step calibration procedures

---

## 📖 Core Documentation

**Module reference and technical details:**

- [**Toolchanger Module**](toolchanger.md) - Main toolchanger configuration and G-code commands
- [**Tool Probe System**](tool_probe.md) - Tool probe endstop configuration
- [**Tools Calibrate**](tools_calibrate.md) - Automatic offset calibration with NUDGE probe
- [**Rounded Path**](rounded_path.md) - Smooth curved motion paths for tool changes
- [**Tool Paths**](tool_paths.md) - Path definition and execution system

---

## 🔧 Advanced Features

**Optional modules and enhancements:**

- [**Manual Rail**](manual_rail.md) - Flying gantry / liftbar support
- [**Bed Thermal Adjust**](bed_thermal_adjust.md) - Bed temperature compensation
- [**ATOM Reference**](atom-reference.md) - ATOM toolhead system details

---

## 🚨 Support & Troubleshooting

**Having issues? Find solutions here:**

- [**🚨 Troubleshooting Guide**](TROUBLESHOOTING.md) - Problem diagnosis and solutions
- [**❓ FAQ**](FAQ.md) - Frequently asked questions
- [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues) - Report bugs
- [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions) - Ask questions

---

## 💡 Examples & Reference Configs

**Production-tested configurations:**

- [**ATOM 6-Tool Setup**](../examples/atom-tc-6tool/README.md) - Complete 6-tool reference configuration
  - Hardware integration (Beacon, LEDs, KNOMI)
  - Safety features (Two-stage pickup, monitoring)
  - Per-tool input shaper
  - Complete calibration workflow
- [**OrcaSlicer Setup**](../examples/atom-tc-6tool/ORCASLICER_SETUP.md) - Slicer configuration guide
  - G-code templates
  - Post-processing script for auto-shutdown
  - Multi-material workflow

---

## 🏗️ Hardware

**Physical setup and integration:**

- [**Hardware Overview**](../hardware/README.md) - Supported hardware and requirements
- [**ATOM Toolhead**](../hardware/ATOM-toolhead/README.md) - ATOM-specific documentation and CAD files

---

## 🔍 Project Resources

**General project information:**

- [**Main README**](../README.md) - Project overview and features
- [**Installation Guide**](../README.md#installation) - Setup instructions
- [**CHANGELOG**](../CHANGELOG.md) - Version history and updates
- [**CONTRIBUTING**](../CONTRIBUTING.md) - How to contribute
- [**License**](../LICENSE) - GPL-3.0

---

## 📚 Documentation Index

### By Topic

| Topic | Document | Description |
|-------|----------|-------------|
| **Setup** | [Quick Start](QUICKSTART.md) | 5-step setup guide |
| **Config** | [Configuration](CONFIGURATION.md) | All parameters explained |
| **Calibration** | [Calibration](CALIBRATION.md) | XY/Z offset calibration |
| **Problems** | [Troubleshooting](TROUBLESHOOTING.md) | Fix common issues |
| **Questions** | [FAQ](FAQ.md) | Quick answers |
| **Reference** | [Toolchanger](toolchanger.md) | Module reference |
| **Probing** | [Tools Calibrate](tools_calibrate.md) | NUDGE probe setup |
| **Example** | [ATOM Setup](../examples/atom-tc-6tool/README.md) | Complete config |

### By User Level

**🟢 Beginner:**
1. [Quick Start](QUICKSTART.md)
2. [FAQ](FAQ.md)
3. [ATOM Example](../examples/atom-tc-6tool/README.md)

**🟡 Intermediate:**
1. [Configuration Guide](CONFIGURATION.md)
2. [Calibration Guide](CALIBRATION.md)
3. [Troubleshooting](TROUBLESHOOTING.md)

**🔴 Advanced:**
1. [Toolchanger Module](toolchanger.md)
2. [Rounded Path](rounded_path.md)
3. [Tool Paths](tool_paths.md)

---

## 📋 Configuration File Reference

### Minimum Required Files

```
printer.cfg
├── [include toolchanger.cfg]           # Core toolchanger
├── [include toolchanger_macros.cfg]    # Essential macros
└── [include T0.cfg, T1.cfg, ...]       # Tool definitions
```

### Complete Setup (ATOM Example)

```
printer.cfg
├── Core Toolchanger
│   ├── toolchanger.cfg
│   ├── toolchanger_macros.cfg
│   └── macros.cfg
├── Tools
│   ├── T0.cfg
│   ├── T1.cfg
│   ├── T2.cfg (etc.)
├── Calibration
│   └── calibrate_offsets.cfg
└── Hardware Integration
    ├── beacon.cfg
    ├── tc_led_effects.cfg
    └── knomi.cfg
```

---

## 🔧 Python Module Reference

All Python modules are located in `klipper/extras/`:

| Module | Purpose | Documentation |
|--------|---------|---------------|
| `toolchanger.py` | Main toolchanger logic | [toolchanger.md](toolchanger.md) |
| `tool.py` | Individual tool management | [toolchanger.md](toolchanger.md) |
| `tools_calibrate.py` | XY calibration | [tools_calibrate.md](tools_calibrate.md) |
| `tool_probe.py` | Per-tool probe | [tool_probe.md](tool_probe.md) |
| `tool_probe_endstop.py` | Probe routing | [tool_probe.md](tool_probe.md) |
| `rounded_path.py` | Smooth paths | [rounded_path.md](rounded_path.md) |
| `tc_beacon_capture.py` | Z-offset capture | N/A (utility) |
| `tc_config_helper.py` | Config helpers | N/A (utility) |
| `bed_thermal_adjust.py` | Thermal compensation | [bed_thermal_adjust.md](bed_thermal_adjust.md) |
| `manual_rail.py` | Manual rail control | [manual_rail.md](manual_rail.md) |
| `multi_fan.py` | Multi-fan controller | N/A (utility) |

---

## 🎓 Learning Path

### Beginner
1. Read the [Quick Start Guide](QUICKSTART.md)
2. Review the [ATOM example configuration](../examples/atom-tc-6tool/README.md)
3. Check the [FAQ](FAQ.md) for common questions
4. Follow the [calibration workflow](CALIBRATION.md)

### Intermediate
1. Deep dive into [Configuration Guide](CONFIGURATION.md)
2. Study [tool paths](tool_paths.md) for custom docks
3. Configure [per-tool probes](tool_probe.md) if applicable
4. Optimize [rounded paths](rounded_path.md) for your setup

### Advanced
1. Review [toolchanger module internals](toolchanger.md)
2. Understand [Python module source code](../klipper/extras/)
3. Explore [ATOM reference features](atom-reference.md)
4. Contribute improvements via [pull requests](../CONTRIBUTING.md)

---

## 🌐 External Resources

**Related projects and tools:**

- [Original klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) by viesturz
- [NUDGE Probe](https://github.com/zruncho3d/nudge) by Zruncho
- [Beacon Probe](https://github.com/beacon3d/beacon_klipper) by Beacon3D
- [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) by SoftFever
- [Klipper Documentation](https://www.klipper3d.org/)

---

## 🆘 Getting Help

### Documentation Issues
- **Typo or error in docs?** Submit a [pull request](../CONTRIBUTING.md)
- **Missing documentation?** Open an [issue](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)

### Technical Support
- **Bug reports:** Use [bug report template](https://github.com/PrintStructor/klipper-toolchanger-extended/issues/new?template=bug_report.md)
- **Feature requests:** Use [feature request template](https://github.com/PrintStructor/klipper-toolchanger-extended/issues/new?template=feature_request.md)
- **Questions:** Use [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)

### Community Resources
- **Reddit:** r/VORONDesign, r/klippers
- **Forums:** Klipper Discourse

---

## 📝 Documentation Standards

When contributing documentation:

1. **Clarity** - Use simple, clear language
2. **Examples** - Include working examples
3. **Testing** - Test all commands before documenting
4. **Formatting** - Follow Markdown best practices
5. **Links** - Keep internal links up to date

---

## 🔄 Recent Documentation Updates

**v1.0.0 (2025-11-18):**
- ✨ Added Quick Start Guide
- ✨ Added Configuration Guide
- ✨ Added Calibration Guide
- ✨ Added Troubleshooting Guide
- ✨ Added FAQ
- 📝 Updated tools_calibrate.md with ATOM references
- 🎨 Reorganized documentation structure
- 🔗 Improved navigation and cross-references

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**License:** GPL-3.0
