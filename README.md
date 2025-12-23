# Klipper Toolchanger Extended

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-1.0.1-green.svg)](https://github.com/PrintStructor/klipper-toolchanger-extended/releases)
[![Klipper](https://img.shields.io/badge/Klipper-0.11+-orange.svg)](https://www.klipper3d.org/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-printstructor-yellow.svg)](https://buymeacoffee.com/printstructor)

---

<p align="center">
  <img src="docs/images/ATOM-TOOL_CHANGE_720.gif" alt="ATOM 6-Head Toolchanger in Action" width="100%">
</p>

---

**Version:** 1.0.1 | **Author:** PrintStructor | **License:** GPL-3.0
**Based on:** [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)
> Latest stable: **v1.0.1** – tool loss & error recovery bugfixes

> Klipper toolchanger extension with additional safety features, error recovery, and a complete working configuration for 6-tool VORON printers with ATOM toolheads.

---

## What This Is

This is an extension of [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) that adds:

**Safety Features:**
- Two-stage pickup with verification between stages
- Continuous tool presence monitoring during prints
- Pause-based error handling for recoverable issues
- Automatic heater shutoff on tool loss

**Complete Configuration:**
- 6-tool VORON 2.4 setup with ATOM toolheads
- All macros and safety checks pre-configured
- Documented hardware specifications
- LED status integration

**Calibration Workflows:**
- NUDGE probe for XY offset measurement
- Beacon contact probe for Z offset calibration
- Automated measurement workflows
- Configuration saved via SAVE_CONFIG

**Flexibility:**
- Any tool can be used as the initial reference tool (not limited to T0)
- Per-tool input shaper profiles
- CPAP shuttle cooling integration
- Optional KNOMI display support

---

## For Beginners

**What is a toolchanger?**  
A multi-tool 3D printer that can automatically switch between different hotends during a print, allowing for multi-color or multi-material printing with true independent toolheads.

**Do I need this?**  
Only if you're building a physical multi-tool system with:

- Multiple complete hotends on separate carriages
- Dock stations for parking/picking each tool
- Tool detection sensors
- An automatic tool changing mechanism

**Alternatives:**

- **Single toolhead:** Standard 3D printer - one extruder, one hotend
- **MMU systems:** Multiple filaments feeding into one hotend (ERCF, Tradrack, etc.)
- **Standard toolchangers:** Use viesturz/klipper-toolchanger base or TypQxQ implementations

**Prerequisites:**

- Experience with Klipper configuration
- Understanding of G-code and printer mechanics
- Mechanical assembly skills
- Time for calibration and tuning

**Required Klipper Extensions:**

This project uses additional Klipper extensions that must be installed separately:

- **[gcode_shell_command](https://github.com/dw-0/kiauh)** - Required for:
  - KNOMI display integration (sleep/wake commands)
  - Beacon calibration automation (capture/save functions)

  **Installation via KIAUH:**
  ```bash
  cd ~/kiauh
  ./kiauh.sh
  # Select: 4) [Advanced] → 8) [G-Code Shell Command]
  ```

  If you don't use KNOMI or automated Beacon calibration, you can skip the shell_command configs.

---

## Technical Differences from Base Project

**viesturz/klipper-toolchanger provides:**

- Core toolchanger logic and state management
- Flexible tool/dock abstraction
- Basic pickup/dropoff framework
- Foundation for custom implementations

**This fork adds:**

- Verification step between pickup stages (approach → verify → commit)
- Background tool presence checking during prints
- Pause-based error recovery instead of immediate stops
- Complete example configuration for specific hardware
- Documented calibration workflows
- Hardware-specific documentation (ATOM toolheads, CPAP cooling)

---

## Key Features

### Two-Stage Pickup Process

Standard pickup happens in one motion. This fork adds verification:

1. **Approach and pre-engage** – Move to dock, partially engage tool  
2. **Verify tool detection** – Check sensor confirms tool presence  
3. **Complete engagement** – Finish pickup only if verification passes  
4. **Abort if failed** – Maintain current tool if verification fails  

This catches misalignments and sensor issues before committing to moves.

### Tool Presence Monitoring

During printing, the system continuously checks that the active tool is still attached. If tool loss is detected:

- Pause the print immediately
- Shut off the lost tool's heater
- Move to safe Z height
- Wait for user intervention

This prevents crashes, dragging hotends across prints, and potential fire hazards.

### Error Recovery

Instead of emergency stops, the system uses pause-based recovery:

- Print state is preserved
- Tool states remain known
- User can fix issues manually
- Resume after correcting the problem

Common recoverable scenarios:

- Tool not properly seated in dock
- Tool detection sensor glitch
- Tool dropped mid-print
- Dock position slightly off

### Reference Tool Flexibility

Unlike systems that require T0 as the reference tool, this implementation allows any tool to be the initial reference. All other tools are calibrated relative to whichever tool you choose.

This is useful when:

- T0 is not ideal for calibration
- You want to use a specific tool as your "master"
- Your tool layout makes another tool more convenient

---

## Hardware Reference: ATOM + VORON 2.4

This configuration is designed for:

**Printer:**

- VORON 2.4 350mm (or similar CoreXY)
- MGN12 linear rails on X-axis
- Carbon fiber or aluminum X-extrusion

**Toolheads:**

- 6× ATOM toolheads (custom design by Alex/APDMachine)
- ~236 g per complete tool (with extruder, hotend, sensor)
- Tool detection sensors on each tool
- Individual heater cartridges and thermistors

**Shuttle:**

- ~52 g lightweight shuttle assembly
- CPAP blower mounted centrally on shuttle
- Beacon probe mounted on shuttle
- Pin-and-bushing pickup mechanism (ClickChanger/Stealthchanger style)

**Probing:**

- Beacon RevH probe for Z-offset calibration and bed meshing
- NUDGE probe for XY-offset calibration
- Touch-based contact for precise Z measurements

**Wiring:**

- Umbilical wiring (no cable chains)
- CAN bus for toolhead communication
- Per-tool CAN boards (e.g., EBB36/42)

**Optional:**

- LED strips for tool/dock status
- Per-tool filament sensors

---

## Optional Hardware Integration

### 🖥️ KNOMI Display Support

Real-time visual feedback and status display via BTT KNOMI:

**Repository:** [PrintStructor/knomi-toolchanger](https://github.com/PrintStructor/knomi-toolchanger)

<p align="center">
  <img src="https://github.com/PrintStructor/knomi-toolchanger/raw/master/docs/images/KNOMI-6-TC_720.gif" alt="KNOMI Toolchanger Display" width="600">
</p>

**Features:**
- Live tool status indication
- Temperature monitoring for all extruders
- Print progress visualization
- Error state alerts
- Animated tool change sequences

The KNOMI integration provides an intuitive visual interface for monitoring your multi-tool setup, making it easier to track which tools are active, their temperatures, and overall system status at a glance.

---

## Important Notes

**This is not plug-and-play:**

- Requires mechanical toolchanger hardware (not included)
- Needs careful dock alignment and sensor installation
- Configuration must be adapted to your specific hardware
- All dock positions, offsets, and speeds need tuning
- Calibration is mandatory before first use

**Expected setup time:**

- **Hardware build:** Several weeks (if building toolchanger from scratch)
- **Software setup:** 1–2 days (copying configs, adjusting values)
- **Initial calibration:** 2–3 hours (XY + Z offsets for all 6 tools)
- **Fine-tuning:** Ongoing as you learn your system

**Common issues to expect:**

- Dock position adjustments needed after thermal cycling
- Sensor sensitivity requires tuning
- Movement speeds need optimization for your hardware
- Occasional recalibration after maintenance or crashes
- Z-offset drift over time (normal, recalibrate periodically)

**Safety considerations:**

- Tool changes can fail – always monitor first prints
- Mechanical alignment is critical
- Sensors are not foolproof – verify correct operation
- Keep workspace clear of obstructions
- Hot toolheads present burn risk during changes

---

## What's Included

### Python Modules (Klipper Extensions)

Located in `klipper/extras/`:

- **`toolchanger.py`** – Core toolchanger logic (from viesturz base)
- **`tool.py`** – Tool state management and operations
- **`rounded_path.py`** – Smooth movement paths for toolchanges
- **`tools_calibrate.py`** – XY/Z offset calibration workflows
- **`tc_config_helper.py`** – Configuration parsing and validation
- **`tc_beacon_capture.py`** – Beacon probe integration for Z calibration
- **`tc_save_config_value.py`** – SAVE_CONFIG integration for storing offsets
- **`tc_save_beacon_contact.sh`** – Shell script for Beacon Z measurements

### Klipper Configs & Macros

In `examples/atom-tc-6tool/`:

- **`toolchanger.cfg`** – Core toolchanger configuration (tools, docks, offsets)
- **`toolchanger_macros.cfg`** – All macros for pickup, dropoff, recovery, calibration
- **`macros.cfg`** – High-level user macros (PRINT_START, etc.)
- **`T0.cfg` … `T5.cfg`** – Individual tool configurations (6 tools)
- **`beacon.cfg`** – Beacon probe configuration
- **`printer.cfg`** – Main printer config (example/reference)

---

## Quick Start

### Requirements

- **Klipper:** v0.11.0 or newer  
- **Python:** 3.7+ (included with Klipper)  
- **Hardware:** Multi-tool/toolchanger 3D printer with docks and sensors  
- **Host:** Raspberry Pi or similar Linux SBC running Klipper

### External Dependencies

This project works with several external Klipper plugins:

**Required:**

- **[Beacon 3D](https://github.com/beacon3d/beacon_klipper)** – For Z-offset calibration and bed meshing

**Recommended:**

- **[Shake&Tune](https://github.com/Frix-x/klippain-shaketune)** – For input shaper tuning  
- **[TMC Autotune](https://github.com/andrewmcgr/klipper_tmc_autotune)** – For automatic TMC driver tuning  
- **[Klipper LED Effect](https://github.com/julianschill/klipper-led_effect)** – For LED status effects

Install these according to their respective documentation before proceeding.

### Installation

**1. Clone the repository:**

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended
```

**2. Run the installation script:**

```bash
./install.sh
```

The script will:

- symlink the Python modules into your Klipper `klippy/extras` directory
- optionally add a Moonraker `update_manager` entry for this repository
- **optionally copy example configs into your Klipper config directory**  
  (`printer_data/config/ATOM-toolchanger-examples/`), so you can edit them
  directly from Mainsail/Fluidd
- restart the Klipper service

### Make the config files usable

If you answered **`y`** when the installer asked to copy example configs, you
already have a full set of configuration files under:

```text
printer_data/config/ATOM-toolchanger-examples/
 ├─ macros.cfg
 ├─ mainsail.cfg
 ├─ printer_example.cfg
 ├─ shell_command.cfg
 ├─ variables.cfg
 └─ atom/
     ├─ T0.cfg … T5.cfg
     ├─ toolchanger.cfg
     ├─ toolchanger_macros.cfg
     ├─ beacon.cfg
     ├─ calibrate_offsets.cfg
     ├─ knomi.cfg
     └─ tc_led_effects.cfg
```

You can open and edit these directly in Mainsail/Fluidd under:

> **Machine → Config Files → ATOM-toolchanger-examples**

There are two common ways to use them:

#### Option A – keep everything in `ATOM-toolchanger-examples` (easy start)

Keep the files where they are and include them from your `printer.cfg`:

```ini
[include ATOM-toolchanger-examples/atom/toolchanger.cfg]
[include ATOM-toolchanger-examples/atom/toolchanger_macros.cfg]
[include ATOM-toolchanger-examples/atom/beacon.cfg]

[include ATOM-toolchanger-examples/atom/T0.cfg]
[include ATOM-toolchanger-examples/atom/T1.cfg]
[include ATOM-toolchanger-examples/atom/T2.cfg]
[include ATOM-toolchanger-examples/atom/T3.cfg]
[include ATOM-toolchanger-examples/atom/T4.cfg]
[include ATOM-toolchanger-examples/atom/T5.cfg]
```

Use `macros.cfg`, `mainsail.cfg`, `shell_command.cfg` and `variables.cfg` as
templates and copy pieces into your existing config layout as needed.

#### Option B – move the files into your own layout (advanced users)

If you already have a custom config structure, you can:

1. Move/rename the files from `ATOM-toolchanger-examples/` to your preferred
   directories (for example into your own `atom/` folder)
2. Update your `[include ...]` lines in `printer.cfg` to match the new paths

#### If you skipped the example copy in the installer

If you answered **`n`** when the installer asked about copying example configs,
you can still use the original manual options:

```bash
# Symlink
ln -s ~/klipper-toolchanger-extended/examples/atom-tc-6tool ~/printer_data/config/atom

# or copy
cp -r ~/klipper-toolchanger-extended/examples/atom-tc-6tool ~/printer_data/config/atom
```

and then include:

```ini
[include atom/toolchanger.cfg]
[include atom/toolchanger_macros.cfg]
[include atom/beacon.cfg]
[include atom/T0.cfg]
[include atom/T1.cfg]
[include atom/T2.cfg]
[include atom/T3.cfg]
[include atom/T4.cfg]
[include atom/T5.cfg]
```

### First calibration steps

After wiring, config adaptation and safety checks, the basic sequence is:

```gcode
G28                                    # Home all axes
SET_INITIAL_TOOL TOOL=0                # Set T0 as reference tool (or any tool)
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0 # Calibrate XY offsets
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0  # Calibrate Z offsets
```

For detailed setup and calibration workflows, see:

- [QUICKSTART.md](docs/QUICKSTART.md) – Quick installation guide  
- [CONFIGURATION.md](docs/CONFIGURATION.md) – All config options explained  
- [CALIBRATION.md](docs/CALIBRATION.md) – Detailed calibration workflows  
- [ATOM Example Config](examples/atom-tc-6tool/README.md) – Hardware-specific setup

---

## Where to start

Depending on what you want to do, you don’t have to read everything in this repo.

### 1. I want to use the ATOM 6-tool configuration

Start here:

1. **README.md**
   - Read: *What This Is*, *For Beginners*, *Quick Start*
2. **docs/QUICKSTART.md**
   - Clone the repo, run `./install.sh`, make sure Klipper + Moonraker are set up
3. **examples/atom-tc-6tool/README.md**
   - Understand the example config layout and which values you MUST change
4. **docs/CALIBRATION.md**
   - Run XY and Z calibration for all tools
5. **docs/TROUBLESHOOTING.md**
   - Use this when something behaves differently than expected

### 2. I’m evaluating if this project is right for me

1. **README.md** – overall scope and hardware assumptions  
2. **docs/WHY_THIS_FORK.md** – what this fork adds on top of the base project  
3. **docs/FEATURE_COMPARISON.md** – differences vs. other popular solutions

### 3. I want to customize or extend the system

1. **README.md → What’s Included** – Python modules and config overview  
2. **docs/CONFIGURATION.md** – all configuration options explained  
3. `klipper/extras/*.py` – source code of the extended toolchanger modules  
4. **CONTRIBUTING.md** – how to propose changes or add new hardware profiles

---

## Documentation

**Getting Started:**

- [QUICKSTART.md](docs/QUICKSTART.md) – Installation and basic setup  
- [WHY_THIS_FORK.md](docs/WHY_THIS_FORK.md) – What this fork provides  
- [FEATURE_COMPARISON.md](docs/FEATURE_COMPARISON.md) – Comparison with other solutions

**Configuration:**

- [CONFIGURATION.md](docs/CONFIGURATION.md) – All configuration options  
- [CALIBRATION.md](docs/CALIBRATION.md) – XY and Z offset calibration  
- [ATOM Example Config](examples/atom-tc-6tool/README.md) – Complete 6-tool setup

**Reference:**

- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) – Common issues and solutions  
- [CHANGELOG.md](CHANGELOG.md) – Version history  
- [CONTRIBUTING.md](CONTRIBUTING.md) – How to contribute

**Hardware:**

- [Hardware Overview](hardware/README.md) – ATOM toolhead specifications (coming soon)

---

## Who Should Use This Fork?

**Use this fork if:**

- You're building a 6-tool VORON with ATOM-style toolheads
- You want a complete working configuration as a starting point
- You value documented safety features and error recovery
- You prefer examples over building from scratch

**Use viesturz/klipper-toolchanger base if:**

- You have completely custom hardware
- You want maximum flexibility to implement your own logic
- You prefer minimal frameworks over complete examples

**Use TypQxQ implementations if:**

- You need virtual tool support (one physical tool, multiple logical tools)
- You're building MMU-style systems
- You want a different architectural approach

All of these projects have merit – this fork simply provides one specific
approach with safety features and a complete reference implementation.

---

## Credits & Acknowledgments

This project builds on work by many contributors in the Klipper toolchanger community:

**Core Framework:**

- [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) – Original implementation and core logic

**Hardware Design:**

- **ATOM Toolhead:** Custom-designed by Alex at APDMachine (creator of the Reaper Toolhead)  
- **Shuttle Mechanism:** Based on ClickChanger/Stealthchanger pin-and-bushing principles  
- **Dock Design:** Inspired by modular dock concepts, redesigned for this application

**This Fork:**

- Additional safety features, monitoring, and complete configuration by PrintStructor

This project is licensed under **GPL-3.0** (same as Klipper).  
See [LICENSE](LICENSE) for full terms.

---

## Contributing

Contributions are welcome! This is an open-source project.

**Ways to contribute:**

- Report bugs or issues you encounter
- Share your hardware variant configurations
- Improve documentation or add examples
- Submit code improvements via pull requests

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

---

## Support & Community

**Found a bug?**  
Open an issue on GitHub with:

- Your hardware setup
- Klipper version
- Configuration files
- Error messages or logs
- Steps to reproduce

**Have questions?**

- Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) first
- Review existing GitHub issues
- Ask in VORON or Klipper community channels

**Want to share your build?**

- Post in community forums
- Tag this project if sharing publicly
- Consider contributing your config as an example

**Want to support development?**

If this project helped you get your toolchanger running (or saved a print from total disaster 🙃), you can support further development here:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?logo=buymeacoffee&logoColor=000&style=flat-square)](https://buymeacoffee.com/printstructor)

---

## Roadmap

Planned improvements:

- Additional hardware profile examples (different toolhead designs)
- More calibration and setup documentation
- Video tutorials for common procedures
- Extended recovery scenarios
- Additional display/LED integrations

Contributions toward these goals are welcome!

---

## License

This project is licensed under **GNU General Public License v3.0** (GPL-3.0),
the same license as Klipper.

**What this means:**

- You can use, modify, and distribute this software
- Any modifications must also be GPL-3.0 licensed
- No warranty is provided (use at your own risk)

See [LICENSE](LICENSE) for complete terms.

---

**Last updated:** 2025-11-20  
**Version:** 1.0.0  
**Maintained by:** PrintStructor
