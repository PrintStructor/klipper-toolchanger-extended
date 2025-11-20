# Upstream Viesturz Archive

This directory contains archived material from the original [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) repository.

**⚠️ Status:** This content is **not actively maintained** and is preserved only as reference material.

---

## 📁 Directory Structure

### `unused_modules/`
Python modules and documentation from the original Viesturz repository that are **not used** in the ATOM TC configuration:

- `bed_thermal_adjust.py` - Bed thermal expansion compensation
- `manual_rail.py` - Manual rail alignment helpers  
- `tool_probe.py` - Tool-mounted probe system
- `tool_probe_endstop.py` - Probe as virtual endstop
- `multi_fan.py` - Multiple fan control

These modules were part of the original framework but are not required for the ATOM TC setup with BEACON probe and shuttle-mounted CPAP cooling.

### `original_docs/`
Original documentation from the Viesturz repository:

- `toolchanger.md` - Core toolchanger module documentation
- `rounded_path.md` - Smooth path motion system
- `tool_paths.md` - Tool path configuration

These documents describe the base framework that this fork extends. Current documentation is in the main `/docs` directory.

---

## 🔍 Why Is This Here?

This archive exists for:

1. **Reference** - Understanding the original framework
2. **Completeness** - Preserving upstream context
3. **Future Development** - Potential reuse of unused modules

**For current documentation, see:**
- [Main README](../README.md)
- [Documentation Overview](../docs/README.md)
- [ATOM TC Example](../examples/atom-tc-6tool/README.md)

---

## 📌 Attribution

All content in this archive is from:
- **Project:** [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)
- **Author:** Viesturs Zarins
- **License:** GPL-3.0

This fork extends the original framework with additional safety features and a complete ATOM TC configuration.

---

## ⚠️ Important Notes

- **Not Updated:** This archive reflects the state at fork time
- **Not Supported:** No support provided for these archived modules
- **Use At Own Risk:** These components are not tested with ATOM TC
- **Check Upstream:** For latest versions, see the original repository

---

**Last Updated:** 2025-11-20  
**Archive Created:** v1.0.0 release preparation
