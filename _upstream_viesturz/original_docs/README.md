# Viesturz Reference Documentation

This directory contains the original API reference documentation from [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger).

## What's Here

These documents describe the **base framework** that klipper-toolchanger-extended builds upon:

- **toolchanger.md** - Core toolchanger module API reference
  - Configuration parameters for `[toolchanger]` and `[tool]`
  - Available G-code commands
  - Status reference

- **tool_paths.md** - Example pickup/dropoff paths
  - TapChanger, StealthChanger, ClickChanger examples
  - Generic reference (not ATOM TC specific)

- **rounded_path.md** - Rounded path module documentation
  - Smooth curved motion paths
  - Configuration and G-code reference

## Why Is This Here?

These are kept as reference documentation for users who want to:
- Understand the underlying Viesturz framework
- Dive deeper into configuration parameters
- Adapt this fork to different hardware

## For ATOM TC Users

**Most users should refer to the main documentation instead:**
- [QUICKSTART.md](../QUICKSTART.md) - Getting started guide
- [CONFIGURATION.md](../CONFIGURATION.md) - ATOM TC configuration guide
- [CALIBRATION.md](../CALIBRATION.md) - Calibration procedures

The Viesturz reference docs are useful for **advanced users** who want to understand the framework internals or implement custom toolchanger designs.

## Credits

Original documentation by [Viesturs Zarins (viesturz)](https://github.com/viesturz).

This fork maintains compatibility with the Viesturz framework while adding safety features and complete ATOM TC configuration.

---

**Note:** Some links and images in these documents may not work as they reference the original viesturz repository structure.
