## NUDGE + Beacon: Calibration workflow in `atom`

The `atom` reference configuration uses **two separate sensors** for tool alignment:

- **NUDGE** (by zruncho3d) for *relative XY tool offsets* between all tools.
- **Beacon** for *Z offset* and *bed surface* calibration in Klipper.

This keeps the roles clearly separated:

- NUDGE answers:  
  > “Where are the other nozzles in X/Y relative to my reference tool?”
- Beacon answers:  
  > “Where is the bed surface in Z for this tool on this build plate?”

### 1. XY tool alignment with NUDGE

NUDGE is a 3-axis contact probe that can be nudged in **Z, X and Y**, allowing Klipper to measure the relative offset between any number of tools.

In the `atom` setup:

1. A **reference tool** (usually `T0`) is chosen.
2. All tools are jogged to the NUDGE probe in a safe position.
3. The macro

   ```gcode
   NUDGE_FIND_TOOL_OFFSETS INITIAL_TOOL=0
   ```

   runs a fully automatic sequence:
   - each tool taps the probe in Z, then X and Y,
   - Klipper calculates the ΔX/ΔY between the active tool and `T0`,
   - the resulting offsets are written into the per-tool config (e.g. `T1.cfg`, `T2.cfg`, …).

4. After the run you either:
   - confirm and persist the values via `SAVE_CONFIG`, or  
   - copy the reported offsets into your tool config manually.

Once this is done, all tools share a common XY coordinate system and can be used for multi-color / multi-material prints without visible misalignment.

### 2. Z offset & bed surface with Beacon

Beacon is used as the **Z reference** for all tools. It combines a high-resolution inductive sensor with an optional contact workflow to build a Z model of the bed and the nozzle-to-bed distance.

In the `atom` configuration the typical flow is:

1. **Beacon model & global Z offset for the reference tool**  
   - Follow the Beacon docs to install and calibrate the probe (`BEACON_CALIBRATE` or `BEACON_AUTO_CALIBRATE`).  
   - The result is a Beacon model plus a reliable Z offset for the reference tool (e.g. `T0`).

2. **Per-tool Z offsets using Beacon contact mode**

   After XY alignment via NUDGE, a macro like:

   ```gcode
   MEASURE_TOOL_Z_OFFSETS INITIAL_TOOL=0
   ```

   will:

   - park each tool over the same probe point,
   - use Beacon in **contact mode** to touch off the bed with each nozzle,
   - measure the Z difference between the active tool and the reference tool,
   - write per-tool Z offsets (e.g. `t1_z_offset`, `t2_z_offset`, …) into the config.

   The reference tool (`INITIAL_TOOL`) defines Z = 0; all other tools are adjusted relative to it.

3. **Normal print workflow**

   Once NUDGE + Beacon calibration is complete:

   - Homing and bed mesh use Beacon as the Z reference.
   - The toolchanger macros automatically apply the stored XY and Z offsets when switching tools.
   - You can optionally re-run Beacon’s contact auto-calibration periodically (or before critical prints) without touching the NUDGE XY offsets.

### 3. Summary

- **NUDGE**: one-time or occasional **XY** alignment between tools – micron-level nozzle registration.  
- **Beacon**: repeatable **Z** calibration and bed mesh, shared across all tools.  
- The `atom` macros (`NUDGE_FIND_TOOL_OFFSETS`, `MEASURE_TOOL_Z_OFFSETS`, etc.) wrap both systems into a repeatable calibration chain that can be re-run whenever tools, nozzles or build plates are changed.
