# Documentation Overview

Welcome to the klipper-toolchanger-extended documentation!

---

## 🚀 Getting Started

**New to toolchangers? Start here:**

- [**⚡ Quick Start Guide**](QUICKSTART.md) - Installation and setup
- [**🔧 Configuration Guide**](CONFIGURATION.md) - Complete parameter reference  
- [**📐 Calibration Guide**](CALIBRATION.md) - XY/Z offset calibration procedures

---

## 📖 Core Documentation

### User Guides

- [**Why This Fork**](WHY_THIS_FORK.md) - What this fork provides vs other solutions
- [**Feature Comparison**](FEATURE_COMPARISON.md) - Technical comparison with other projects
- [**Safety Features in Action**](SUCCESS_STORIES.md) - How safety features work in practice
- [**Troubleshooting**](TROUBLESHOOTING.md) - Common problems and solutions
- [**FAQ**](FAQ.md) - Frequently asked questions

### Technical Reference

- [**Tools Calibrate**](tools_calibrate.md) - NUDGE probe XY offset calibration API
- [**ATOM Reference**](atom-reference.md) - NUDGE + Beacon calibration workflow details
- [**Viesturz Reference**](../_upstream_viesturz/original_docs/README.md) - Original framework documentation

---

## 💡 Examples & Configuration

**Complete working configurations:**

- [**ATOM 6-Tool Setup**](../examples/atom-tc-6tool/README.md) - Complete 6-tool VORON reference
  - Hardware integration (Beacon, LEDs, KNOMI)
  - Safety features configuration
  - Calibration workflow
  
- [**OrcaSlicer Setup**](../examples/atom-tc-6tool/ORCASLICER_SETUP.md) - Slicer configuration
  - G-code templates
  - Post-processing scripts
  - Multi-material workflow

---

## 🏗️ Hardware

**Physical setup information:**

- Hardware documentation is planned for future release
- Current focus: ATOM toolhead system for VORON 2.4
- Check [ATOM Example README](../examples/atom-tc-6tool/README.md) for hardware specifications

---

## 🔍 Project Resources

**General information:**

- [**Main README**](../README.md) - Project overview and features
- [**CHANGELOG**](../CHANGELOG.md) - Version history
- [**CONTRIBUTING**](../CONTRIBUTING.md) - How to contribute
- [**License**](../LICENSE) - GPL-3.0

---

## 📚 Documentation Index by User Level

### 🟢 Beginner

**Start here if you're new to toolchangers:**

1. [Quick Start Guide](QUICKSTART.md) - Installation basics
2. [FAQ](FAQ.md) - Common questions answered
3. [ATOM Example](../examples/atom-tc-6tool/README.md) - Working configuration
4. [Why This Fork](WHY_THIS_FORK.md) - Understanding what this provides

### 🟡 Intermediate

**For users setting up and calibrating:**

1. [Configuration Guide](CONFIGURATION.md) - All parameters explained
2. [Calibration Guide](CALIBRATION.md) - XY/Z calibration procedures
3. [Troubleshooting](TROUBLESHOOTING.md) - Fixing common issues
4. [OrcaSlicer Setup](../examples/atom-tc-6tool/ORCASLICER_SETUP.md) - Slicer integration

### 🔴 Advanced

**For users customizing and developing:**

1. [Tools Calibrate](tools_calibrate.md) - Calibration module API
2. [ATOM Reference](atom-reference.md) - Detailed calibration workflow
3. [Viesturz Reference](../_upstream_viesturz/original_docs/README.md) - Base framework internals
4. [Python Source Code](../klipper/extras/) - Module implementation

---

## 📋 Quick Reference

### Documentation by Topic

| Topic | Document | Level |
|-------|----------|-------|
| **Installation** | [Quick Start](QUICKSTART.md) | Beginner |
| **Configuration** | [Configuration Guide](CONFIGURATION.md) | Intermediate |
| **Calibration** | [Calibration Guide](CALIBRATION.md) | Intermediate |
| **Problems** | [Troubleshooting](TROUBLESHOOTING.md) | All |
| **Questions** | [FAQ](FAQ.md) | All |
| **Examples** | [ATOM Setup](../examples/atom-tc-6tool/README.md) | All |
| **Comparison** | [Feature Comparison](FEATURE_COMPARISON.md) | Beginner |
| **Technical** | [Tools Calibrate](tools_calibrate.md) | Advanced |

---

## 🔧 Python Modules

Core Klipper extensions included in this fork:

**Main modules:**
- `toolchanger.py` - Core toolchanger logic with two-stage pickup
- `tool.py` - Individual tool management
- `tools_calibrate.py` - NUDGE probe XY calibration
- `rounded_path.py` - Smooth curved motion paths

**Helper modules:**
- `tc_config_helper.py` - Configuration save helpers
- `tc_beacon_capture.py` - Beacon Z-offset capture
- `tc_save_config_value.py` - Auto-save integration
- `tc_save_beacon_contact.sh` - Shell script for Beacon

**For detailed API documentation, see [Viesturz Reference](../_upstream_viesturz/original_docs/toolchanger.md).**

---

## 🌐 External Resources

**Related projects:**

- [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) - Original framework
- [zruncho3d/nudge](https://github.com/zruncho3d/nudge) - NUDGE probe for XY calibration
- [beacon3d/beacon_klipper](https://github.com/beacon3d/beacon_klipper) - Beacon probe
- [Klipper Documentation](https://www.klipper3d.org/) - Official Klipper docs

---

## 🆘 Getting Help

### Documentation Issues

Found an error or missing information?
- Submit a [pull request](../CONTRIBUTING.md) to fix it
- Open an [issue](https://github.com/PrintStructor/klipper-toolchanger-extended/issues) to report it

### Technical Support

Need help with your setup?
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) first
- Review [FAQ](FAQ.md) for common questions
- Open a [GitHub Discussion](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)
- Report bugs via [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)

---

## 📝 Documentation Standards

When contributing documentation, please:

1. **Use clear language** - Avoid jargon when possible
2. **Provide examples** - Show working code/config examples
3. **Test instructions** - Verify all commands work as documented
4. **Keep links current** - Only link to existing files
5. **Follow conventions** - Match existing documentation style

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

## 🔄 Recent Updates

**v1.0.0 (2025-11-20):**
- ✨ Comprehensive user documentation added
- 📝 Technical reference guides created
- 🎨 Reorganized into beginner/intermediate/advanced sections
- 🔗 Fixed broken links and removed references to non-existent files
- 📚 Added Viesturz reference documentation archive

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**License:** GPL-3.0
