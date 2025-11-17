# Klipper Toolchanger – Extended Fork

**Author:** PrintStructor  
**Original project:** https://github.com/viesturz/klipper-toolchanger

> Complete Klipper config, macros and tooling for multi-tool / toolchanger 3D printers, based on Viesturs Zarins’ original klipper-toolchanger project.

---

## Overview

This repository is an **enhanced fork** of Viesturs’s excellent `klipper-toolchanger` project. It keeps the original Python modules and core concepts, but adds a more complete, production-oriented setup:

- Extended macros and safety logic for **reliable multi-tool printing**
- A full reference printer configuration (`atom`)
- Better separation of core code vs. user-specific config
- A structured place for documentation and examples

If you’re building or tuning a **Klipper-based toolchanger** (IDEX, gantry toolchanger, docked tools, etc.), this repo is meant to be a **practical starting point**.

---

## Base Project (Viesturs)

The original `klipper-toolchanger` by Viesturs Zarins provides the core framework for Klipper-based toolchangers, including:

- Toolchanger object and tool management support
- Per-tool Z probe support (`tool_probe`)
- Rounded path module for smooth non-print moves
- Tools calibrate module for contact-based XYZ calibration

🔗 Original repo: https://github.com/viesturz/klipper-toolchanger

This fork keeps that foundation and builds additional config and workflows on top of it.

---

## Key Enhancements in This Fork

### 1. Two-Stage Pickup & Safer Tool Handling

- Stage 1: Safe approach and partial insertion with detection checks  
- Stage 2: Full insertion only if the tool is confirmed present  
- Reduces the risk of crashes from mis-detection or mechanical misalignment

### 2. Non-Fatal Error Handling

- Toolchanger errors are handled via **pause and recovery**, not instant firmware shutdown
- Allows you to:
  - Fix mechanical issues (tool not seated, obstruction, etc.)
  - Resume printing with restored position and temperatures

### 3. Tool Detection State Management

- Clear detection states: `PRESENT`, `ABSENT`, `UNAVAILABLE`
- Continuous monitoring during printing
- Automatic pause if the active tool is lost/drops mid-print

### 4. XY-Offset Matrix Support

- Stores relative **XY offsets per tool**
- Supports multi-tool setups (up to 6 tools in the reference config)
- Offsets are applied automatically during tool changes

### 5. Recovery System

- `RESUME` brings the printer back into a known-good state:
  - Restores last print position
  - Restores previous heater state
  - Continues the print from where it stopped

### 6. Per-Tool Configuration & Advanced Macros

- Individual parameters per tool (offsets, detection pins, parking coordinates, etc.)
- Separation between:
  - Core toolchanger logic (Python modules)
  - User macros and printer-specific config
- Ready to be extended with your own:
  - Purge/wipe macros  
  - Standby/active temperature strategies  
  - Per-tool tuning (pressure advance, input shaper, etc.)

---

## Repository Structure

```text
klipper-toolchanger-extended/
├── klipper/          # Python modules for Klipper (extras)
├── usermods/         # User-level macros and config snippets
├── examples/         # Example configs and usage snippets
├── docs/             # Documentation entry point
├── install.sh        # Helper script to install extras into Klipper
└── README.md         # This file
```

On your Klipper host (e.g. Raspberry Pi), the **printer configuration** usually lives under:

```text
/opt/printer_data/config/   or   ~/printer_data/config/
```

This repository refers to a reference configuration folder named:

```text
printer_data/config/atom/
```

`atom` is the name of the reference printer configuration and is based on a toolhead originally designed by **APDesign & Machine (APDM)**.  
APDM GitHub: https://github.com/APDMachine

---

## Requirements

- **Firmware:** Klipper v0.11.0 or newer
- **Host:** Linux SBC (e.g. Raspberry Pi) or equivalent
- **Printer:** Multi-tool / toolchanger setup
- **Tool detection:** Endstop / hall / inductive or similar sensors are strongly recommended
- **Slicer:** Any Klipper-compatible slicer (OrcaSlicer, PrusaSlicer, etc.)

---

## Installation

> ⚠️ This fork assumes you already have a working Klipper installation.

### 1. Clone the Repository

SSH into your printer / Klipper host:

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd ~/klipper-toolchanger-extended
```

### 2. Install the Klipper Extras

Recommended way – via the included script:

```bash
./install.sh
```

The script will symlink the Python modules into your Klipper `extras` directory.

Manual alternative:

```bash
ln -sf ~/klipper-toolchanger-extended/klipper/extras/*.py ~/klipper/klippy/extras/
```

### 3. Include the configuration in Klipper

In your `printer.cfg`:

```ini
# Core toolchanger sections are provided by viesturz/klipper-toolchanger
# and extended by this repo.

[include usermods/toolchanger_macros.cfg]
# Optional: further includes, depending on how you structure your config:
# [include usermods/toolchanger_calibration.cfg]
# [include usermods/tool_leds.cfg]
```

If you use the **ATOM reference configuration** as a base, you can include its files directly, e.g.:

```ini
[include atom/toolchanger.cfg]
[include atom/toolchanger_macros.cfg]
[include atom/calibrate_offsets.cfg]
[include atom/T0.cfg]
[include atom/T1.cfg]
[include atom/T2.cfg]
[include atom/T3.cfg]
[include atom/T4.cfg]
[include atom/T5.cfg]
```

> Note: adjust the paths to match your actual `printer_data/config` layout on the host.

### 4. Restart Klipper

```bash
sudo systemctl restart klipper
```

---

## Reference Configuration: `atom`

The `atom` reference configuration (on your host typically under `printer_data/config/atom/`) demonstrates a complete multi-tool setup with:

- Up to **6 tools** (`T0`–`T5`)
- Per-tool offsets
- Tool detection pins
- Separate XY and Z calibration (e.g. NUDGE + Beacon)
- Optional LED and KNOMI integration

Typical files:

- `toolchanger.cfg` – core toolchanger configuration  
- `toolchanger_macros.cfg` – central macros (pickup/dropoff, init, etc.)  
- `calibrate_offsets.cfg` – calibration macros for XY/Z  
- `T0.cfg` … `T5.cfg` – individual tool definitions  
- `beacon.cfg` – Z calibration with Beacon (or similar probe)  
- `tc_led_effects.cfg` – LED status visualization  
- `knomi.cfg` – KNOMI display integration

---

## Quick Start (G-Code / Macros)

### 1. Define a tool

```ini
[tool T0]
tool_number: 0
extruder: extruder
detection_pin: ^et0:PB9
params_park_x: 25.3
params_park_y: 3.0
params_park_z: 325.0
```

### 2. Set initial tool

```gcode
SET_INITIAL_TOOL TOOL=0
```

### 3. Switch tools

```gcode
T1 ; Switch to Tool 1
```

### 4. Calibrate XY offsets (e.g. with NUDGE probe (by zruncho3d) or similar)
  → https://github.com/zruncho3d/nudge

```gcode
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
```

### 5. Calibrate Z offsets (e.g. with Beacon)

```gcode
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
SAVE_CONFIG
```

---

## Error Handling & Monitoring

### Tool Presence Monitoring

Example of how a monitoring timer can be started (simplified):

```ini
# Typically started in PRINT_START or an init macro:
UPDATE_DELAYED_GCODE ID=TOOL_PRESENCE_MONITOR DURATION=2.0
```

If the active tool is lost (sensor reports ABSENT):

- The tool heater is turned off (safety)
- The print is paused
- LEDs can show an error state (if configured)
- You can fix the mechanical issue and resume

### Recovery with `RESUME`

After fixing the issue (re-seating the tool, clearing the obstruction):

```gcode
RESUME
```

The extended toolchanger stack will restore position and temperatures (assuming your macros are wired accordingly) and continue the print.

---

## Docs & Further Reading

- `docs/` – entry point for this repo’s documentation (work in progress)
- Upstream documentation from Viesturs:
  - `toolchanger.md`
  - `tool_probe.md`
  - `tools_calibrate.md`
  - `rounded_path.md`

You can find them in the original project:  
https://github.com/viesturz/klipper-toolchanger

Think of those docs as the **API reference** for the Klipper modules, and this repo as a **concrete, tested reference configuration** for a modern multi-tool setup.

---

## Credits

- **Core toolchanger code:**  
  Viesturs Zarins – https://github.com/viesturz/klipper-toolchanger

- **Toolhead design inspiration (ATOM):**  
  APDesign & Machine (APDM) – https://github.com/APDMachine / https://reapertoolhead.com

- **NUDGE – automatic nozzle alignment probe:**  
  Zruncho / zruncho3d – https://github.com/zruncho3d/nudge  
  Used as the reference hardware for automatic XY tool offset calibration.

- **Extended config & macros:**  
  PrintStructor – https://github.com/PrintStructor

---

## License

This project – like the original – is licensed under **GPL-3.0**.

In short:

- You may use, modify and redistribute the code
- If you publish modified versions, they must also be under GPL-3.0
- See the `LICENSE` file in this repository for full details
