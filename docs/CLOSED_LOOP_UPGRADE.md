# Closed-Loop Stepper Upgrade Guide (TMC4671 + Ouroboros)

> **Status: EXPERIMENTAL** — This guide documents the integration of closed-loop
> servo control for X/Y axes using the TMC4671 driver IC on the Ouroboros board.
> The TMC4671 Klipper driver by Andrew McGrath is currently in beta.

## Overview

This upgrade replaces the standard open-loop TMC2209 stepper drivers on X/Y with
closed-loop FOC (Field Oriented Control) servo operation using:

- **Driver Board:** Ouroboros by Isik's Tech (dual TMC4671 + TMC6100)
- **Motors:** LDO-42STH48-2504-E1000 with integrated 1000-line optical encoders
- **Klipper Driver:** [andrewmcgr/tmc-4671](https://github.com/andrewmcgr/tmc-4671)

The TMC4671 handles all servo control in hardware. Klipper treats it as a
conventional stepper driver — sending step/dir signals that the TMC4671 translates
into position angle targets internally.

## What Changes

| Aspect | Before (TMC2209) | After (TMC4671/Ouroboros) |
|---|---|---|
| Control mode | Open-loop | Closed-loop FOC servo |
| Driver IC | TMC2209 (UART) | TMC4671 + TMC6100 (SPI) |
| Board | Octopus Pro onboard | Ouroboros (separate MCU) |
| Motors | Moons MS17HD6P420I-04 | LDO-42STH48-2504-E1000 |
| Encoder | None | 1000-line optical (6-wire) |
| Microsteps | 32 (physical) | 2 (virtual — servo in hardware) |
| Steps/rev | 200 | 4096 (virtual) |
| Sensorless homing | Yes (StallGuard) | No (not functional yet) |
| autotune_tmc | Yes | No (use TMC_TUNE_PID instead) |
| Brake resistors | Not needed | **MANDATORY** |

## What Does NOT Change

- **Z-axis:** Remains on TMC5160 drivers (Octopus Pro) — no changes needed
- **Toolchanger logic:** All docking paths, macros, and tool configs remain identical
- **Z-current boost macros:** Still reference `tmc5160 stepper_z` — unchanged
- **CAN toolheads:** EBB36/42 boards and extruder configs are not affected
- **Beacon probe:** Z-homing and QGL configuration stays the same

## Hardware Requirements

1. **Ouroboros board** (Isik's Tech) — dual-channel TMC4671 + TMC6100
2. **LDO-42STH48-2504-E1000 motors** (×2) — with integrated 1000-line encoders
3. **Brake resistors** (×2) — mount where they can safely reach 95°C
4. **Physical endstop for X-axis** — sensorless homing is not functional
5. **SPI wiring** — SCK, MOSI, MISO, CS lines (must be hardware SPI, 3.3V only)
6. **STEP/DIR/ENABLE wiring** — from Ouroboros MCU to TMC4671 (3.3V, NOT 5V tolerant)
7. **Encoder cables** — 6-wire from LDO motors to Ouroboros encoder ports

### Encoder Wiring (LDO 2504-E1000)

The LDO motors use a 6-wire differential encoder. Connect as follows:

| Encoder Wire | Ouroboros Port |
|---|---|
| A+ | A |
| B+ | B |
| A- | GND |
| B- | GND |
| Common | GND |
| 5V | 5V |
| Z (if present) | Z (optional, will be used if connected) |

### Brake Resistors

Brake resistors are **mandatory** for the TMC4671. They absorb energy when the
motor decelerates. Normal operating temperatures reach ~95°C. Mount them on
metal surfaces away from plastic parts and wiring.

## Installation Steps

### Step 1: Install the TMC4671 Klipper Driver

```bash
wget -O - https://raw.githubusercontent.com/andrewmcgr/tmc-4671/main/install.sh | bash
```

Add to `moonraker.conf` for automatic updates:

```ini
[update_manager tmc-4671]
type: git_repo
channel: dev
path: ~/tmc-4671
origin: https://github.com/andrewmcgr/tmc-4671.git
managed_services: klipper
primary_branch: main
install_script: install.sh
```

### Step 2: Flash Klipper on the Ouroboros MCU

The Ouroboros board has its own STM32 controller that must run Klipper firmware.
Configure `make menuconfig` for your specific Ouroboros board revision and flash
via USB or DFU. Consult the Ouroboros documentation from Isik's Tech for the
exact menuconfig settings.

### Step 3: Wire the Hardware

1. Connect motors to the Ouroboros output phases (ensure current sense channels match)
2. Connect encoder cables (6-wire differential — see wiring table above)
3. Connect SPI bus (SCK, MOSI, MISO) and individual CS pins
4. Connect STEP, DIR, and ENABLE signals
5. Install and wire brake resistors
6. Add a physical endstop for X-axis if not already present

> **IMPORTANT:** All TMC4671 signals are 3.3V only — they are NOT 5V tolerant!

### Step 4: Update Klipper Configuration

In your `printer.cfg`, replace the X/Y stepper and TMC2209 sections with an
include for the Ouroboros config:

```ini
# Replace these sections in printer.cfg:
#   [stepper_x] + [tmc2209 stepper_x] + [autotune_tmc stepper_x]
#   [stepper_y] + [tmc2209 stepper_y] + [autotune_tmc stepper_y]
# With:
[include atom/ouroboros_xy.cfg]
```

Copy `ouroboros_xy.cfg` to your `atom/` config directory and edit ALL values
marked with `⚠️ VERIFY` to match your specific wiring and board.

### Step 5: Tune the PID Loops

Follow this exact sequence after first startup:

**Current/Torque PID (autotune):**
```
SET_STEPPER_ENABLE STEPPER=stepper_x
TMC_TUNE_PID STEPPER=stepper_x
SET_STEPPER_ENABLE STEPPER=stepper_y
TMC_TUNE_PID STEPPER=stepper_y
```

Copy the output values to both `foc_pid_flux` and `foc_pid_torque` settings.
Use **identical values** on both X and Y for CoreXY.

**Velocity/Position PID (autotune):**
```
TMC_TUNE_MOTION_PID LAMBDA_V=80 LAMBDA_P=180 HOLDING_CURRENT=2.5 HOLDING_TORQUE=0.055 STEPPER=stepper_x
TMC_TUNE_MOTION_PID LAMBDA_V=80 LAMBDA_P=180 HOLDING_CURRENT=2.5 HOLDING_TORQUE=0.055 STEPPER=stepper_y
SAVE_CONFIG
```

Lambda_v can range from ~45 upward, Lambda_p should be at least 2× Lambda_v.
If motors make noise at rest after tuning, increase Lambda values. The minimum
value that stays quiet is likely optimal.

**Biquad filters (manual):**

Start with `biquad_torque_frequency: 1600` and `biquad_flux_frequency: 800`.
Adjust based on motor behavior:
- Hissing while moving → torque frequency too high
- Noise while stationary → frequency too low
- Rounding corners at speed → flux frequency too low

## Toolchanger-Specific Considerations

### Homing Changes

Since sensorless homing is not functional with the TMC4671, you need a physical
endstop on the X-axis. The Y-axis already uses a physical endstop in the
standard configuration. Update your homing macros if they rely on StallGuard
behavior (e.g., `homing_retract_dist` should be > 0 for physical endstops).

### Tool Change Speed

Start with reduced `params_fast_speed` and `params_path_speed` in `toolchanger.cfg`
until the closed-loop system is fully tuned. The servo control needs time to
settle, especially during the rapid direction changes of docking paths.

### Z-Current Boost Macros

The macros `_TOOLCHANGER_TOOL_BEFORE_CHANGE` and `_TOOLCHANGER_TOOL_AFTER_CHANGE`
in `toolchanger.cfg` boost Z-stepper current during tool changes. These reference
`tmc5160 stepper_z` and remain **unchanged** — the Z-axis is not affected by
this upgrade.

### Input Shaper

Per-tool input shaper configuration in `T0.cfg` through `T5.cfg` continues to
work normally. However, the resonance characteristics will change with the new
motors and closed-loop control. Re-run input shaper calibration with ADXL345
after the upgrade is complete and PID is tuned.

## Crash Detection (Experimental)

One of the biggest advantages of closed-loop control is that the TMC4671 always
knows the real motor position via encoder feedback. This project includes an
experimental crash detection module that leverages this:

The module periodically reads the position tracking error from the TMC4671
(difference between `PID_POSITION_TARGET` and `PID_POSITION_ACTUAL`). During
normal operation, this error is near zero — the servo keeps up perfectly. When
the motor hits an obstruction (nozzle crash, belt skip, physical blockage), the
error grows rapidly because the motor can't reach the commanded position.

When the error exceeds a configurable threshold for multiple consecutive reads,
the module triggers a print pause — the same mechanism used by the toolchanger's
tool-loss detection.

### How it works

The TMC4671's closed-loop control corrects small disturbances automatically.
If you briefly hold the print head, the motor pushes back and catches up once
released. No lost steps, no layer shift. The crash detection only triggers when
the error is large and persistent — indicating a real crash, not a momentary
disturbance.

### Configuration

```ini
[tmc4671_crash_detect]
stepper_x: stepper_x
stepper_y: stepper_y
position_error_threshold: 200   # Tune for your machine
check_interval: 0.1             # Check every 100ms
consecutive_errors: 3           # 3 reads over threshold = crash
enabled_during_print: True      # Auto-enable when printing
pause_on_error: True            # Pause print on detection
```

### Tuning the threshold

Start with a high threshold (500+) and print normally. Use
`TMC4671_CRASH_DETECT_STATUS` during fast moves to see your baseline position
error. Set the threshold to 2-3× the maximum error seen during normal operation.
Fast accelerations cause momentary errors that are not crashes — the threshold
must be above those peaks.

### GCode commands

- `TMC4671_CRASH_DETECT_ENABLE` — start monitoring
- `TMC4671_CRASH_DETECT_DISABLE` — stop monitoring
- `TMC4671_CRASH_DETECT_STATUS` — show current position errors per axis

## Known Limitations

- **Sensorless homing:** Not functional with TMC4671 driver (as of March 2026)
- **Beta driver:** The TMC4671 Klipper driver is lightly tested
- **Digital Hall encoders:** Work but give poor results — use optical encoders
- **No autotune_tmc:** The Klipper TMC autotune plugin does not support TMC4671

## References

- [TMC4671 Klipper Driver (Andrew McGrath)](https://github.com/andrewmcgr/tmc-4671)
- [TMC4671 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC4671-LA_datasheet_rev2.08.pdf)
- [Ouroboros Board (Isik's Tech)](https://www.isiks.tech/)
- [LDO Motor Specifications](https://www.ldomotors.com/)
