# Klipper Toolchanger Extended

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-1.1.0-green.svg)](https://github.com/PrintStructor/klipper-toolchanger-extended/releases)
[![Klipper](https://img.shields.io/badge/Klipper-0.11+-orange.svg)](https://www.klipper3d.org/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-printstructor-yellow.svg)](https://buymeacoffee.com/printstructor)

<p align="center">
  <img src="docs/images/ATOM-TOOL_CHANGE_720.gif" alt="ATOM 6-head toolchanger in action" width="100%">
</p>

A Klipper toolchanger extension with safety checks, error recovery and a
complete, working configuration for a 6-tool VORON 2.4 with ATOM toolheads.

Based on [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger).

---

## What it adds

**Safety**
- Two-stage pickup: the tool is verified by its sensor before the pickup is completed.
- Tool presence is monitored during a print. A lost tool pauses the print and switches off its heater.
- No tool change runs while Klipper and the sensors disagree about the mounted tool
  (for example after a tool was removed by hand). Nothing moves; outside a print there is no pause either.
- Errors pause the print instead of stopping the printer, so it can be resumed.

**Calibration**
- XY offsets with a camera ([TAXY](https://github.com/PrintStructor/TAXY)) or the
  [NUDGE](https://github.com/zruncho3d/nudge) contact probe.
- NUDGE **ring calibration**: 12 measurements instead of 30, same result within a few microns.
- Z offsets with the Beacon contact probe, as a full matrix of all tools.
- Thermal expansion compensation of the nozzle, calibrated per tool.
- Per-tool Z babystepping during a print, and a global Z adjust for all tools.
- Any tool can be the reference tool, not only T0.

**Optional**
- Experimental closed-loop X/Y with TMC4671 servo drivers ([guide](docs/CLOSED_LOOP_UPGRADE.md)).
- [KNOMI](https://github.com/PrintStructor/knomi-toolchanger) displays per tool, LED status effects.

---

## Is this for me?

This is not plug-and-play. You need a working toolchanger: several complete
toolheads, docks, a detection sensor per tool and an automatic pickup mechanism.
Expect a day or two for the software setup and a few hours for the first calibration.

If your hardware is very different, the
[viesturz base project](https://github.com/viesturz/klipper-toolchanger) may be the
better starting point. For one hotend with several filaments, look at an MMU instead.

---

## Quick start

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended
./install.sh
```

The installer links the Python modules into Klipper, can add a Moonraker
update entry and can copy the example configuration into your config folder.

Then follow the guides in this order:

1. [Installation](docs/INSTALLATION.md): install, include the config, first tool change
2. [Configuration](docs/CONFIGURATION.md): the values you must adapt to your printer
3. [Calibration](docs/CALIBRATION.md): XY, Z and thermal compensation
4. [Troubleshooting](docs/TROUBLESHOOTING.md): when something goes wrong

---

## Repository layout

| Path | Content |
|---|---|
| `klipper/extras/` | Python modules, linked into Klipper by the installer |
| `examples/atom-tc-6tool/` | The author's complete printer configuration ([overview](examples/atom-tc-6tool/README.md)) |
| `docs/` | Guides |
| `hardware/` | ATOM toolhead hardware notes |
| `kTAMV/` | Legacy camera calibration (replaced by TAXY) |

### Python modules

| Module | Purpose |
|---|---|
| `toolchanger.py` | Core logic: tool changes, detection, safety checks, error handling |
| `tool.py` | Tool definition and detection pin |
| `tools_calibrate.py` | NUDGE probing for XY offsets |
| `tool_xy_calibration.py` | Saves camera-measured XY offsets |
| `tool_z_adjust.py` | Per-tool Z babystepping |
| `rounded_path.py` | Smooth paths for dock moves |
| `tc_beacon_capture.py` | Collects Beacon readings for Z calibration (via Moonraker) |
| `tc_config_helper.py`, `tc_save_config_value.py` | Helpers for writing calibration results |
| `beacon_temp_override.py` | Raises the Beacon contact temperature limit during thermal calibration only |
| `tmc4671_crash_detect.py` | Crash detection for the closed-loop option |

---

## Dependencies

**Required:** [Beacon](https://github.com/beacon3d/beacon_klipper) for Z calibration and bed mesh.

**Recommended:**
[TAXY](https://github.com/PrintStructor/TAXY) (camera XY calibration),
[Klipper LED Effect](https://github.com/julianschill/klipper-led_effect),
[Shake&Tune](https://github.com/Frix-x/klippain-shaketune),
[TMC Autotune](https://github.com/andrewmcgr/klipper_tmc_autotune).

**Optional:**
[NUDGE](https://github.com/zruncho3d/nudge) probe,
[gcode_shell_command](https://github.com/dw-0/kiauh) (only for KNOMI sleep/wake),
[TMC4671 driver](https://github.com/andrewmcgr/tmc-4671) (closed-loop option).

---

## Credits

- [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger): original toolchanger framework
- [NUDGE](https://github.com/zruncho3d/nudge) by Zruncho, [kTAMV](https://github.com/PrintStructor/kTAMV) by TypQxQ
- ATOM toolhead by Alex (APDMachine); shuttle based on ClickChanger/Stealthchanger
- Extensions, calibration workflows and configuration by PrintStructor

Bugs and ideas: please open an issue with your Klipper version, the relevant config
and the console output. See [CONTRIBUTING.md](CONTRIBUTING.md) for pull requests.

If this project saved you a print or two:
[buy me a coffee](https://buymeacoffee.com/printstructor).

## License

GPL-3.0, like Klipper. See [LICENSE](LICENSE).
