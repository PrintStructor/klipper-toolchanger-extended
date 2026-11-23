# Installation

From a working single-tool Klipper printer to the first tool change.

## Before you start

- Klipper 0.11 or newer runs, homing works, and the printer prints with one tool.
- A Beacon probe is set up and tested on one tool.
- Every tool has a working detection sensor (microswitch or similar).
- An emergency stop is within reach for the first tests.

## 1. Install

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended
./install.sh
```

The installer:

- links the Python modules from `klipper/extras/` into `~/klipper/klippy/extras/`
- optionally adds an `[update_manager klipper-toolchanger-extended]` entry to
  `moonraker.conf`, so updates show up in Mainsail/Fluidd
- optionally copies the example configuration to
  `~/printer_data/config/ATOM-toolchanger-examples/`
- restarts Klipper

## 2. Include the configuration

The example in `examples/atom-tc-6tool/` is the author's complete printer
configuration. Use it as a template, not as a drop-in file: pins, CAN UUIDs and
dock positions must match your printer (see [Configuration](CONFIGURATION.md)).

The usual layout keeps the toolchanger files in an `atom/` folder next to
`printer.cfg`:

```ini
[include atom/toolchanger.cfg]          # core toolchanger settings and change logic
[include atom/toolchanger_macros.cfg]   # TC_INIT, PARK_TOOLHEAD, PICKUP_TOOL, ...
[include atom/beacon.cfg]
[include atom/T0.cfg]
[include atom/T1.cfg]
[include atom/T2.cfg]
[include atom/T3.cfg]
[include atom/T4.cfg]
[include atom/T5.cfg]
[include atom/tool_calibration.cfg]     # NUDGE and Beacon calibration
[include atom/nudge_ring.cfg]           # NUDGE ring calibration (optional)
[include atom/beacon_diagnostics.cfg]   # thermal compensation, probe tests
[include macros.cfg]                    # PRINT_START, PAUSE/RESUME, filament
```

If the installer copied the examples, the same files are in
`ATOM-toolchanger-examples/`; adjust the include paths or move them into your own
layout. `variables.cfg` stores calibration results and must exist
(`[save_variables]` in `printer.cfg`).

Restart Klipper and fix any config errors before you go on.

## 3. Checks without tools

With the shuttle empty:

```gcode
G28
DEBUG_TOOL_DETECTION
```

All tools must report `detect_state: 0` and `Detected Tool: None`.
Now put one tool on the shuttle by hand and run `DEBUG_TOOL_DETECTION` again:
exactly this tool must show `detect_state: 1`. Repeat for every tool.
If a sensor reports the wrong state, fix it now (see
[Troubleshooting](TROUBLESHOOTING.md#tool-detection)).

## 4. First tool change

First determine the park position of every dock and reduce the speeds
considerably, as described in
[Configuration](CONFIGURATION.md#dock-positions-and-speed-do-this-first).
Keep a hand near the emergency stop, then:

```gcode
G28
INITIALIZE_TOOLCHANGER
T0
T1
PARK_TOOLHEAD
```

Watch every approach to the dock. If a tool hits the dock, correct
`params_park_x/y/z` of that tool in `T<n>.cfg`. Once all tools change reliably,
`TOOLCHANGE_DEMO` runs 20 random changes as an endurance test.

## 5. Calibrate

Next step: [Calibration](CALIBRATION.md).

---

## Updating

With the Moonraker entry, update from Mainsail/Fluidd (Machine → Update Manager).
Without it:

```bash
cd ~/klipper-toolchanger-extended
git pull
sudo systemctl restart klipper
```

The Python modules are linked, so a pull updates them directly. Your config files
are never overwritten. To take over improved macros, compare first:

```bash
diff ~/printer_data/config/atom/tool_calibration.cfg \
     ~/klipper-toolchanger-extended/examples/atom-tc-6tool/atom/tool_calibration.cfg
```

Never copy the example `printer.cfg` or `variables.cfg` over your own: they
contain the author's calibration values. Make a backup before larger changes:

```bash
cp -r ~/printer_data/config ~/printer_data/config.backup.$(date +%Y%m%d)
```
