# Calibration

Every tool sits slightly differently on the shuttle. Calibration measures how far
each nozzle is from the **reference tool** in X, Y and Z, so all tools print onto
the same spot.

Order for a new printer:

1. [XY offsets](#xy-offsets): NUDGE probe
2. [Z offsets](#z-offsets): Beacon contact probe
3. [Thermal compensation](#thermal-compensation): once per tool
4. [Check with a test print](#checking-the-result), fine-tune with
   [babystepping](#z-babystepping-during-a-print)

All macros below are in `atom/tool_calibration.cfg`, `atom/nudge_ring.cfg` and
`atom/beacon_diagnostics.cfg`.

## Before you calibrate

- All tools change reliably ([Installation](INSTALLATION.md#4-first-tool-change)).
- Nozzles are clean. For contact probing, unload the filament: a drop of plastic
  on the tip goes straight into the result.
- The reference tool is T0 unless you choose otherwise. It always has offset 0;
  all other offsets are relative to it. `SET_INITIAL_TOOL TOOL=<n>` changes it.

All calibration macros home and heat by themselves and save the result with
`SAVE_CONFIG` at the end, which restarts Klipper. Offsets end up in the
`[tool T<n>]` sections at the bottom of `printer.cfg`.

---

## XY offsets

| Method | Command | Measurements | When |
|---|---|---|---|
| NUDGE ring | `NUDGE_CALIBRATE_RING_XY` | 12 | Default with NUDGE |
| NUDGE full | `NUDGE_CALIBRATE_ALL_TOOLS_XY` | 30 | Occasional cross-check |
| NUDGE single reference | `NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0` | 5 | Quick check |
| NUDGE one tool | `NUDGE_FIND_TOOL_OFFSET` | 1 | Current tool only |

The NUDGE is a small pin that the nozzle touches from four sides. From the
contact points it finds the nozzle centre.

**Ring calibration (recommended).** Only neighbouring tools are measured, each pair
in both directions: T0↔T1, T1↔T2 … T5↔T0. A least-squares adjustment then
computes one consistent position per tool and writes all offsets, so any tool can
serve as reference.

```gcode
NUDGE_CALIBRATE_RING_XY            # optional: MAX_CLOSURE=0.05
```

Why both directions: every single measurement carries a small constant bias
(about +0.004 mm in X and Y on the author's printer). It cancels only when a pair
is measured both ways.

The macro checks the **ring closure**: going once around the ring has to end
where it started. If the gap exceeds `MAX_CLOSURE` (default 0.05 mm), nothing is
saved. Then run `FIRMWARE_RESTART`, check the probe and the nozzles, and repeat.

On the author's printer, ring and full calibration agreed to 0.005 mm on average
and 0.006 mm at most, with a ring closure under 0.01 mm. That is far below what
shows up in a print, so the full run is only needed as an occasional cross-check.

**Full calibration.** Every tool is the reference once and measures all others
(6 × 5 = 30 measurements). Takes about twice as long as the ring.

```gcode
NUDGE_CALIBRATE_ALL_TOOLS_XY       # optional: SKIP=3 to leave out tool 3
```

**Good to know**

- During NUDGE probing the part fan runs at 25 % and the bed fans at 100 %. This
  keeps filament residue on the hot nozzle from sticking to the probe pin and
  dragging it along, which caused failed measurements.
- Each measured offset is written to `variables.cfg` immediately
  (`nudge_xy_<reference>_<tool>`). After a disconnect,
  `NUDGE_RESTORE_OFFSETS SAVE=1` restores them.
- Probing quality is set in `[tools_calibrate]`: `samples: 3` with
  `samples_discard: 1` probes 5 times, drops the highest and lowest value and
  checks the tolerance on the remaining 3. A single outlier no longer forces a
  full retry.

---

## Z offsets

The Beacon probe measures by contact: each nozzle touches the bed, and the height
difference to the reference tool becomes its Z offset. Measured at 150 °C;
the thermal compensation adds the expansion at print temperature.

```gcode
BEACON_CALIBRATE_ALL_TOOLS_Z       # full matrix, 30 measurements (recommended)
BEACON_CALIBRATE_Z INITIAL_TOOL=0  # single reference, 5 measurements
BEACON_BATCH_ABORT                 # stop a running batch
```

`BEACON_CALIBRATE_ALL_TOOLS_Z` accepts `PROBE_TEMP` (default 150) and the probing
position `X_POS`/`Y_POS` (default bed centre).

---

## Thermal compensation

A nozzle gets longer as it heats up, roughly 0.0005 mm per °C. Between the
calibration temperature (150 °C) and 250 °C that is about 0.05 mm, enough to ruin
a first layer. The compensation measures this per tool and corrects it on every
tool change.

Calibrate once per tool, with the **filament unloaded**:

```gcode
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=0      # optional: TEMP_LOW=150 TEMP_HIGH=250
BEACON_CALIBRATE_NOZZLE_TEMP_OFFSET INITIAL_TOOL=1
# ... up to T5
```

The macro measures at both temperatures (3 samples each) and stores the
coefficient as `nozzle_expansion_coefficient_t<n>` in `variables.cfg`.
Normal values are 0.0004 to 0.0008 mm/°C. During the calibration it raises
Beacon's contact temperature limit temporarily and restores it afterwards.

Applied automatically: after every tool change and in `PRINT_START`
(`APPLY_NOZZLE_TEMP_OFFSET`). By hand:

```gcode
SHOW_NOZZLE_TEMP_OFFSET            # coefficients and current correction of all tools
APPLY_NOZZLE_TEMP_OFFSET TOOL=2
CLEAR_NOZZLE_TEMP_OFFSET
```

Recalibrate after a nozzle or hotend change.

---

## Z babystepping during a print

Fine adjustments while printing, kept in memory until you save them:

```gcode
SET_TOOL_Z_ADJUST Z=0.02           # current tool 0.02 mm higher
SET_TOOL_Z_ADJUST TOOL=3 Z=-0.01   # a specific tool
SET_TOOL_Z_ADJUST TOOL=3 RESET=1   # back to the calibrated value
GLOBAL_Z_ADJUST Z=-0.01            # all tools at once
SHOW_TOOL_Z_ADJUSTMENTS
SAVE_TOOL_Z_ADJUSTMENTS            # make them permanent (SAVE_CONFIG, restarts Klipper)
```

The babystep buttons in Mainsail/Fluidd also act on the current tool only.
Unsaved adjustments are lost on the next restart.

How the Z offset of a tool is put together:

```
Z = calibrated offset + thermal compensation + babystep of the tool + global adjust
```

---

## Checking the result

- **XY:** print a multi-tool calibration pattern (for example, lines or crosses
  from every tool on top of each other) and compare the positions.
- **Z:** print a single-layer pattern with every tool; all tools should look the same.

## When to recalibrate

| Change | Recalibrate |
|---|---|
| Dock moved or reprinted, toolhead rebuilt | XY of this tool (or ring) |
| Nozzle or hotend changed | Z and thermal compensation of this tool, check XY |
| Probe, bed or build plate changed | Z of all tools |
| Colours misaligned in prints | XY |
| First layer differs between tools | Z |

## If the results look wrong

- Offsets of several millimetres are always an error: wrong reference tool, a loose
  tool or a probe problem. Do not print with them.
- Restore the previous values from a `printer-<date>.cfg` backup (written by
  `SAVE_CONFIG`) or with `NUDGE_RESTORE_OFFSETS`.
- More in [Troubleshooting](TROUBLESHOOTING.md#calibration).
