# Quick Start Guide

This guide walks you from a **fresh clone** of `klipper-toolchanger-extended`
to a **first safe, calibrated toolchange** on your printer.

It focuses on the reference setup:

- VORON 2.4 350 mm
- 6 × ATOM tools
- Beacon probe
- Tool‑presence sensing (recommended, but not strictly required)

If you run different hardware, you can still follow the same steps and adapt
positions and IDs to your machine.

---

## 1. Prerequisites

Before you start, make sure you have:

- ✅ A working Klipper install (v0.11+)
- ✅ Basic single‑tool printing working on your machine
- ✅ Homing and endstops configured correctly
- ✅ A Z‑probe configured (Beacon recommended, but others work too)
- ✅ Basic familiarity with:
  - `printer.cfg`
  - Using the Klipper console (Mainsail / Fluidd)
  - Running `SAVE_CONFIG`

**Strongly recommended:**

- Tool‑presence / dock sensors (microswitch, hall sensor, etc.)
- An emergency stop button within reach during first tests

**Required Klipper Extensions:**

Some features require additional Klipper extensions:

- ✅ **[gcode_shell_command](https://github.com/dw-0/kiauh)** - Required for KNOMI display and Beacon calibration automation

  **Installation via KIAUH:**
  ```bash
  cd ~/kiauh
  ./kiauh.sh
  # Select: 4) [Advanced] → 8) [G-Code Shell Command]
  ```

  > **Note:** If you don't use KNOMI (`knomi.cfg`) or automated Beacon calibration (`calibrate_offsets.cfg`), you can skip installing shell_command.

---

## 2. Install the Fork

SSH to your Klipper host and clone the repo:

```bash
cd ~
git clone https://github.com/PrintStructor/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended
```

Run the installation script:

```bash
./install.sh
```

What this script does:

- Symlinks the Python modules from this repo into your Klipper `extras/` folder
- Optionally sets up a Moonraker `update_manager` entry
- Restarts Klipper so the new modules are loaded

If anything fails here, fix it **before** moving on.

---

## 3. Include the Example Configuration

Open your main `printer.cfg` and add the following includes:

```ini
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/toolchanger_macros.cfg]
[include klipper-toolchanger-extended/examples/atom-tc-6tool/macros.cfg]
# ... add tool configs T0-T5 ...

# Example tool config includes:
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T0.cfg]
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T1.cfg]
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T2.cfg]
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T3.cfg]
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T4.cfg]
# [include klipper-toolchanger-extended/examples/atom-tc-6tool/T5.cfg]
```

Then **restart Klipper** from your web UI.

If there are syntax errors, fix them now (wrong paths, typos, etc.) before continuing.

---

## 4. Wire Up Your Hardware in Config

At this point, the example config is included – but it still contains
**placeholder values** for *your* hardware.

Go through the following **in order**:

### 4.1. MCU / Board IDs

In each `T*.cfg` and related files, update:

- `mcu` / `canbus_uuid` for each toolhead board
- Any `[extruder]`, `[heater_fan]`, `[fan]` sections to match your pins

If you are unsure, start from the configs that already work for your
single‑tool setup and merge them into the ATOM tool configs.

### 4.2. Beacon / Z‑Probe

Make sure your Z‑probe section (Beacon or other) is correct and working:

- Probe pin and communication
- Offsets (X, Y) relative to the nozzle
- Basic Z offset procedure already validated on a single‑tool setup

You **must** have a known‑good Z‑probe before running automated Z calibration.

### 4.3. Dock Positions (Coarse)

The ATOM example provides dock positions that work on the reference VORON build.

On your printer:

- Roughly position your docks where the reference expects them
- Adjust X/Y positions in `T0.cfg … T5.cfg` so:
  - The nozzle passes near the center of each dock
  - There is no risk of crashing into frame parts

You do **not** need perfect values yet – just "close enough" that the
NUDGE‑based calibration can safely refine them.

---

## 5. Sanity Checks (No Tools Yet)

Before attempting a real tool change:

1. Home all axes:

   ```gcode
   G28
   ```

2. Move manually to positions roughly above each dock to confirm:
   - No collisions with frame/wiring
   - Axes can reach needed positions

3. Keep speeds conservative at first:

   ```gcode
   SET_VELOCITY_LIMIT VELOCITY=100 ACCEL=1500
   ```

---

## 6. First Toolchange Test (Dry Run)

With **no filament loaded** and bed relatively cool:

1. Set the initial tool:

   ```gcode
   SET_INITIAL_TOOL TOOL=0
   ```

2. Pick up T0 using your configured macro (typically `T0` or a specific pickup macro):

   ```gcode
   T0
   ```

3. Drop T0 again (e.g. `T-1` or dedicated park/drop macro, depending on your setup).

4. Repeat for each tool (T1…T5), watching:
   - Motion path
   - Dock engagement
   - Any scraping / collisions

Do **not** continue until you are confident all tools can be picked and dropped
without mechanical issues.

---

## 7. XY Calibration

Once basic pickup and dropoff work, you have two calibration methods:

### Option A: kTAMV (Camera-based) – Recommended

If you have kTAMV installed ([kTAMV by TypQxQ](https://github.com/TypQxQ/kTAMV)):

```gcode
G28
SET_INITIAL_TOOL TOOL=0
KTAMV_CALIBRATE_ALL_TOOLS_XY   # Full batch calibration
```

This uses computer vision to automatically measure all XY offsets.

### Option B: NUDGE (Physical probe)

If you don't have kTAMV, use the manual nudge workflow:

```gcode
G28
SET_INITIAL_TOOL TOOL=0
NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
```

This guides you through aligning each tool visually over a reference mark.

---

When calibration completes, offsets are saved automatically via `SAVE_CONFIG`.

> 📌 Full details in: `CALIBRATION.md` → *XY Calibration* and *Batch Calibration*

---

## 8. Z Calibration

After XY is dialed in:

1. Home & heat the bed and tools to your usual print temperatures.

2. Make sure your reference tool T0 has a correct Z offset via your normal
   probe‑based procedure.

3. Run Z calibration:

### Option A: Batch Z Calibration (Recommended)

```gcode
G28
SET_INITIAL_TOOL TOOL=0
BEACON_CALIBRATE_ALL_TOOLS_Z   # Full matrix calibration
```

This uses each tool as reference and averages results for best accuracy.

### Option B: Single-Reference Calibration

```gcode
G28
SET_INITIAL_TOOL TOOL=0
MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
```

The macro will use your probe to measure each tool relative to T0.

---

Offsets are saved automatically via `SAVE_CONFIG`.

> 📌 Full details in: `CALIBRATION.md` → *Z Calibration* and *Batch Calibration*

---

## 9. First Real Test Print

Now you have:

- ✅ Safe, working pickup & dropoff
- ✅ XY offsets calibrated
- ✅ Z offsets calibrated

Pick a **small** multi‑tool test:

- 2–3 colors
- Simple shapes
- 5–20 minutes print time

Make sure your slicer calls your standard print‑start macro and uses
tool change commands (`T0`, `T1`, …) that match your config.

Watch this print in full. If everything looks good:

- Gradually increase complexity
- Increase speed/accel
- Start trusting the system with longer jobs

---

## 10. Where to Go Next

- Read **`WHY_THIS_FORK.md`** for background and design philosophy  
- Check **`FEATURE_COMPARISON.md`** to see how this fork differs from others  
- Study **`CALIBRATION.md`** for deeper understanding of XY/Z workflows  
- Explore **`examples/atom-tc-6tool/README.md`** for the full reference setup

Once you're comfortable, you can start:

- Using **per-tool Z babystepping** during prints (`SET_TOOL_Z_ADJUST`)
- Tuning per‑tool input shaper
- Integrating KNOMI / LED status
- Refining your slicer profiles for multi‑tool printing

> 💡 **Tip:** During prints, use `SET_TOOL_Z_ADJUST TOOL=n Z=±0.02` to fine-tune
> individual tool Z-offsets without stopping. Save with `SAVE_TOOL_Z_ADJUSTMENTS`
> after a successful print.
