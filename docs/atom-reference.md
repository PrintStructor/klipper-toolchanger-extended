## NUDGE + Beacon: Calibration workflow in `atom`

The `atom` reference configuration uses **two separate sensors** for tool alignment:

- **NUDGE** (by zruncho3d) for *relative XY tool offsets* between tools.
- **Beacon** for *Z offsets* and *bed surface* calibration in Klipper.

The key design idea is that **every tool is calibrated as a reference tool once**.  
This is what makes the setup more flexible than many classic “all tools relative to T0 only” approaches.

---

### 1. XY tool alignment with NUDGE (per-tool reference workflow)

NUDGE is a 3-axis contact probe that can be nudged in **Z, X and Y**, allowing Klipper to measure the relative offset between any number of tools.

In the `atom` setup the XY workflow looks like this:

1. Make sure the printer is homed and all tools are mechanically in a good state.
2. Heat **all tools** to a moderate temperature (e.g. 180 °C) so that nozzle contact is repeatable.
3. For each tool you want to calibrate, run:

   ```gcode
   NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
   NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=1
   NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=2
   ...
   ```

   – one call per tool.

   For each call:

   - the given `INITIAL_TOOL` is treated as the **temporary reference tool**,
   - the macro runs a fully automatic sequence with NUDGE:
     - the tool taps the probe in Z, then X and Y,
     - Klipper measures the XY deltas relative to this reference,
   - the resulting XY offsets are stored **at the bottom of your `printer.cfg`**  
     (that’s where `SAVE_CONFIG` writes the updated values).

4. After each `INITIAL_TOOL` calibration round, you run:

   ```gcode
   SAVE_CONFIG
   ```

   once, so that the updated XY offsets are written back into `printer.cfg`.

After this procedure every tool has its **own consistent XY entry** in `printer.cfg`, and all tools share a common coordinate system.  
Because each tool was treated as a reference at least once, the system can be re-used and extended more easily (e.g. when adding or replacing tools).

---

### 2. Z offsets & bed surface with Beacon (per-tool, bed heated)

Beacon is used as the **Z reference** for all tools. It combines a high-resolution inductive sensor with an optional contact workflow to build a Z model of the bed and the nozzle-to-bed distance.

In the `atom` configuration the Z workflow is intentionally separated from the XY workflow and is always done with a **heated bed** (and typically heated nozzles) to match real printing conditions.

The typical sequence is:

1. Heat the bed to your usual printing temperature.
2. Heat the tools to a suitable calibration temperature.
3. For each tool, run:

   ```gcode
   MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
   MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=1
   MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=2
   ...
   ```

   – again, one call per tool.

   For each call:

   - the `INITIAL_TOOL` is used as the active tool during the sequence,
   - the macro parks the tool above a defined probe point,
   - Beacon is used in **contact mode** to touch off the bed with the current nozzle,
   - the Z difference to the internally stored reference is measured,
   - a per-tool Z offset (`t0_z_offset`, `t1_z_offset`, …) is also written **to the bottom of your `printer.cfg`**.

4. After a full round of `MEASURE_TOOL_Z_OFFSETS` calls, run:

   ```gcode
   SAVE_CONFIG
   ```

   so that all updated Z offsets are persisted in `printer.cfg`.

---

### 3. Normal print workflow

Once the above XY + Z procedures have been completed:

- Homing and bed mesh use Beacon as the **global Z reference**.
- The toolchanger macros automatically apply:
  - the **per-tool XY offsets** stored in `printer.cfg`,
  - and the **per-tool Z offsets** measured with Beacon.
- You can re-run:
  - NUDGE-based XY calibration after mechanical changes (tool swap, dock adjustment),
  - Beacon-based Z calibration whenever nozzles or build plates change,

without having to rebuild the entire setup from scratch.

The result is a repeatable calibration chain that keeps all tools aligned in XY and Z, while still allowing you to treat each tool as a proper first-class reference when needed.
