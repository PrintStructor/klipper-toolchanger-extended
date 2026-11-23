# ATOM TC-6 example configuration

The complete configuration of the author's printer, in daily use:

- VORON 2.4, 350 mm, with 6 ATOM toolheads on CAN toolhead boards
- ATOM: created together with Alex from APDMachine, developed further by PrintStructor;
  runs on the Fysetc CNC shuttle for Stealthchanger
- Beacon RevH (Z offsets, bed mesh), NUDGE probe (XY offsets)
- CPAP part cooling on the shuttle, bed fans, per-tool filament sensors, LED effects
- Optional: closed-loop X/Y with TMC4671 (Ouroboros board)

Use it as a template. Pins, CAN UUIDs, dock positions and all calibration values
belong to this printer and must be replaced with yours
([Configuration](../../docs/CONFIGURATION.md#must-change)).

## Files

```
atom-tc-6tool/
├── printer.cfg                  main config, includes, saved offsets at the bottom
├── macros.cfg                   PRINT_START/END, PAUSE/RESUME, filament load/unload
├── variables.cfg                calibration data (written by macros)
├── bedfans.cfg                  bed fan control
├── helix_macros.cfg             HelixScreen display macros (author-specific)
├── mainsail.cfg, crowsnest.conf web UI and camera
├── mainsail/toolchanger-panel.html  live toolchanger status panel for Mainsail
├── ouroboros_xy.cfg             closed-loop X/Y sections (experimental)
├── printer_closedloop_xy.cfg    printer.cfg variant for closed-loop X/Y
└── atom/
    ├── toolchanger.cfg          [toolchanger] and the tool change sequence
    ├── toolchanger_macros.cfg   TC_INIT, PARK_TOOLHEAD, PICKUP_TOOL, ...
    ├── T0.cfg … T5.cfg          one file per tool
    ├── tool_calibration.cfg     NUDGE probe, NUDGE/Beacon calibration, Z adjust
    ├── nudge_ring.cfg           NUDGE ring calibration (12 measurements)
    ├── beacon.cfg               Beacon probe
    ├── beacon_diagnostics.cfg   thermal compensation, probe tests
    ├── clean_nozzle.cfg         nozzle wipe
    ├── ouroboros_shaper_macros.cfg  input shaper measurement for closed-loop X/Y
    ├── tc_led_effects.cfg       LED status
    └── knomi.cfg                KNOMI displays (optional)
```

## Toolchanger panel for Mainsail

`mainsail/toolchanger-panel.html` shows live what `DEBUG_TOOL_DETECTION` prints:
the tool Klipper expects next to the tool the sensors report (red on mismatch),
every tool's dock/shuttle state, hotend and toolhead board temperatures and Z offsets.
Board temperatures turn yellow at 70 °C and red at 85 °C; change with
`?board_warn=…&board_bad=…` in the URL.

1. Copy it into the Mainsail folder:
   `cp mainsail/toolchanger-panel.html ~/mainsail/`
2. Keep it across Mainsail updates: add to `[update_manager mainsail]` in
   `moonraker.conf`: `persistent_files: toolchanger-panel.html`
3. In Mainsail: Settings → Webcams → add a webcam, service **HTML/iFrame**,
   URL `/toolchanger-panel.html`, aspect ratio e.g. `5:2`.

## Most used commands

| Command | Purpose |
|---|---|
| `T0` … `T5` | Change tool |
| `PARK_TOOLHEAD` | Dock the current tool and leave the shuttle empty |
| `INITIALIZE_TOOLCHANGER` | Take over the tool state from the sensors |
| `DEBUG_TOOL_DETECTION` | Show Klipper's state and the sensors side by side |
| `NUDGE_CALIBRATE_RING_XY` | XY calibration with the NUDGE probe |
| `BEACON_CALIBRATE_ALL_TOOLS_Z` | Z calibration of all tools |
| `SET_TOOL_Z_ADJUST Z=0.01` | Babystep the current tool |
| `LOAD_FILAMENT T=2` / `UNLOAD_FILAMENT T=2` | Filament handling per tool |

Guides: [Installation](../../docs/INSTALLATION.md) ·
[Configuration](../../docs/CONFIGURATION.md) ·
[Calibration](../../docs/CALIBRATION.md) ·
[Troubleshooting](../../docs/TROUBLESHOOTING.md)
