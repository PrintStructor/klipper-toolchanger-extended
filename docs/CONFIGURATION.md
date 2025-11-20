# Configuration Guide

This document explains the **structure** of the configuration files
shipped with `klipper-toolchanger-extended` and how to adapt them to
your own printer.

It is not a replacement for reading the comments in the example configs,
but it gives you the big picture and shows **where to change what**.

The reference layout is:

- `examples/atom-tc-6tool/toolchanger.cfg`
- `examples/atom-tc-6tool/toolchanger_macros.cfg`
- `examples/atom-tc-6tool/macros.cfg`
- `examples/atom-tc-6tool/T0.cfg` … `T5.cfg`

You normally include these from your `printer.cfg` and then override
individual values as needed.

---

## 1. File Overview

### 1.1. `toolchanger.cfg` – Core Toolchanger Settings

Defines the **core objects** that make the toolchanger work:

- The main toolchanger module
- Global options (number of tools, park positions, etc.)
- Optional helper components (safety, monitoring)

Think of this file as **“what a toolchanger is on this printer”**.

---

### 1.2. `toolchanger_macros.cfg` – Toolchange Logic & Calibration

Contains the **high-level macros** that:

- Perform pickup and dropoff
- Manage safe motion around docks
- Run calibration helpers:
  - `NUDGE_FIND_TOOL_OFFSETS`
  - `MEASURE_TOOL_Z_OFFSETS`
- Provide recovery workflows

Think of this as **“how we move and what we do when tools change”**.

---

### 1.3. `macros.cfg` – User-Facing Macros

Contains the **macros you normally call from G-code**:

- `T0` … `T5` (or similar) for tool selection
- Wrapper macros for:
  - `PRINT_START`
  - `PRINT_END`
  - Park / unload helpers
- Any integration macros for slicers

Think of this as **“what the user / slicer actually runs”**.

---

### 1.4. `T0.cfg` … `T5.cfg` – Per-Tool Configuration

Each file represents one physical tool:

- Board / MCU mapping (CAN UUID or USB ID)
- Extruder, heater, fan, sensor pins
- Tool-specific parameters
- Dock positions
- Optional per-tool input shaper and tuning values

Think of each `T*.cfg` as **“all hardware details for this one tool”**.

---

## 2. Core Toolchanger Settings (`toolchanger.cfg`)

Open `examples/atom-tc-6tool/toolchanger.cfg`.

You will typically find sections like:

- A core toolchanger object
- One or more helper / extension objects
- Global behavior flags and limits

### 2.1. Number of Tools

Look for something like:

```ini
[toolchanger]
tool_count: 6
```

Adjust `tool_count` if you use fewer or more tools:

- 2 tools → `tool_count: 2`
- 4 tools → `tool_count: 4`
- etc.

Make sure the number of `T*.cfg` files and tool macros matches this.

---

### 2.2. Global Positions & Speeds

Typical global options:

```ini
[toolchanger]
# Example values – adapt to your printer
safe_z: 20
travel_speed: 200
dock_speed: 80
```

- `safe_z`  
  → Height used when moving above docks and during error recovery

- `travel_speed`  
  → XY travel speed used for non-critical moves

- `dock_speed`  
  → Slower speed used when entering / leaving docks

Adjust these to your machine:

- Big/heavy gantry → more conservative speeds
- Light/rigid machine → higher values possible

Always start conservative and tune up later.

---

### 2.3. Parking Position

Many setups define a **park position**:

```ini
[toolchanger]
park_x: 175
park_y: 350
park_z: 20
```

This is used when:

- Parking during pauses
- Some error conditions
- Manual maintenance macros

Pick a location that:

- Is safe (no collision with frame / docks)
- Is easy to reach
- Leaves the bed accessible if you open the door

---

### 2.4. Safety & Monitoring Options

Depending on the version, you may see sections like:

```ini
[tool_safety]
heater_shutdown_on_tool_loss: true
safe_z_on_error: 20

[tool_monitor]
check_interval: 1.0
tool_presence_timeout: 2.0
```

Typical options:

- `heater_shutdown_on_tool_loss`  
  → Turn off heater if the active tool disappears

- `safe_z_on_error`  
  → Height to move to when an error occurs

- `check_interval`  
  → How often tool presence is checked (in seconds)

- `tool_presence_timeout`  
  → How long a discrepancy is tolerated before pausing

**Suggested starting values:**

- `check_interval: 1.0`  
- `tool_presence_timeout: 2.0–3.0`  
- `safe_z_on_error`: Same as your global `safe_z`

---

## 3. Per-Tool Configuration (`T0.cfg` … `T5.cfg`)

Each tool config defines everything needed for that tool to work:

- Toolhead MCU / board
- Motors, heater, fans
- Dock positions
- Sensors (tool presence, filament, etc.)
- Optional per-tool tuning

Open e.g. `T0.cfg` and you will typically see:

---

### 3.1. MCU / CAN IDs

```ini
[mcu tool0]
canbus_uuid: xxxxxxxxxxxxxxxxxxxxxxxx
```

or:

```ini
[mcu tool0]
serial: /dev/serial/by-id/usb-...
```

Set this to match **your actual hardware**. The easiest way:

1. Look at your working single-tool config
2. Copy the `mcu` section (CAN UUID or serial)
3. Paste & adapt it in `T0.cfg`, `T1.cfg`, etc.

Each physical board **must** have a unique section and ID.

---

### 3.2. Extruder & Heater

Example:

```ini
[extruder tool0]
step_pin: tool0:PB0
dir_pin:  tool0:PB1
enable_pin: !tool0:PB2
heater_pin: tool0:PB3
sensor_type: PT1000
sensor_pin: tool0:PA0
...
```

Replace:

- `step_pin`
- `dir_pin`
- `enable_pin`
- `heater_pin`
- `sensor_pin`
- Any other pins

…with the correct pins for your board.

If you already have a known-good extruder config:

- Copy it in
- Adjust the `extruder` section name (e.g. `extruder tool0`)
- Update references in macros if necessary

---

### 3.3. Fans & Cooling

Example:

```ini
[fan_generic tool0_part_fan]
pin: tool0:PA1

[heater_fan tool0_hotend_fan]
pin: tool0:PA2
```

Map these to your actual fan pins.

If you use a central CPAP blower instead of per-tool part fans, the
example config may:

- Map that blower in only one place
- Use macros to control it depending on the active tool

Adjust as needed for your wiring.

---

### 3.4. Tool & Dock Positions

Usually there is a section that ties a tool to a dock:

```ini
[tool tool0]
dock_id: 0
tool_number: 0
park_x: 300
park_y: 350
dock_x: 320
dock_y: 350
dock_z: 5
```

Key fields:

- `tool_number`  
  → Must match the logical tool index (T0 → `tool_number: 0`)

- `dock_id`  
  → Used internally to match docks and tools

- `dock_x`, `dock_y`, `dock_z`  
  → Where the printer moves to pick up / drop off the tool

- `park_x`, `park_y`  
  → Where the tool is parked during some operations

You can start with the ATOM example values and then:

- Adjust them to your dock positions
- Refine them via `NUDGE_FIND_TOOL_OFFSETS`

---

### 3.5. Tool Presence / Dock Sensors

If you use a sensor to detect whether a tool is present:

```ini
[tool tool0]
tool_sensor_pin: tool0:PB4
tool_sensor_inverted: false
```

Or similar.

Check:

- Pin name and port
- Whether logic is inverted (`true` vs `false`)
- That the sensor changes state when you attach / detach a tool

You can watch the sensor in:

- Mainsail / Fluidd → `Console` → `QUERY_BUTTON` / `QUERY_ENDSTOP`
- Or via the web UI’s “Endstop” panel (if mapped)

---

### 3.6. Per-Tool Input Shaper (Optional)

If you tune input shaper per tool:

```ini
[shaper_calibrate tool0]
shaper_type: mzv
shaper_freq_x: 50
shaper_freq_y: 45
```

Or more commonly:

```ini
[input_shaper]
shaper_type_x: mzv
shaper_freq_x: 50
shaper_type_y: mzv
shaper_freq_y: 45
```

Where the active tool’s profile is selected via macros.

How exactly this is wired depends on your version – check comments in
`toolchanger_macros.cfg` for details.

---

## 4. Macros & Workflow (`toolchanger_macros.cfg`, `macros.cfg`)

### 4.1. Tool Selection (`T0` … `T5`)

Typically, user-facing tool macros look like:

```ini
[gcode_macro T0]
gcode:
  SET_TOOL TOOL=0

[gcode_macro T1]
gcode:
  SET_TOOL TOOL=1
```

These call into the core toolchanger logic:

- Check if a tool is already mounted
- Drop it if needed
- Move to the correct dock
- Perform pickup with two-stage verification
- Update internal state

If you change the number of tools, ensure:

- You have one macro per logical tool
- `TOOL=` indices match your `tool_number` fields

---

### 4.2. Print Start / End

Look in `macros.cfg` for:

- `PRINT_START`
- `PRINT_END`
- `PAUSE`
- `RESUME`
- `CANCEL_PRINT`

These often:

- Call into toolchanger-specific macros
- Ensure a tool is mounted before printing
- Park or drop tools on pause / cancel

Integrate them with your slicer by:

- Setting your slicer’s start/end G-code to call `PRINT_START` / `PRINT_END`
- Letting the slicer use `T0` … `Tn` for tool changes

---

### 4.3. Recovery Macros

`toolchanger_macros.cfg` usually contains macros for:

- Recovering after a failed pickup / dropoff
- Re-picking a tool after manual adjustment
- Re-syncing internal state if you intervened manually

Examples might include:

- `TC_RECOVER`
- `TC_REPICK_TOOL`
- `TC_REDOCK_TOOL`

(Names can differ – check the comments in the file.)

You normally don’t call these from slicer G-code; they are meant for
manual use via console when something goes wrong.

---

### 4.4. Calibration Macros

Described in detail in `CALIBRATION.md`, but configuration-wise:

- `NUDGE_FIND_TOOL_OFFSETS`  
  → Uses motion / nudge controls to compute XY offsets

- `MEASURE_TOOL_Z_OFFSETS`  
  → Uses your probe to compute relative Z offsets

They rely on:

- A correct reference tool set via `SET_INITIAL_TOOL`
- A working probe configuration
- Valid dock positions that won’t crash into hardware

---

## 5. Editing Strategy

Because the example configs are meant as a **reference**, a good
editing strategy is:

1. **Include** the example files as-is in `printer.cfg`.
2. Create a **separate override file**, e.g.:

   ```ini
   [include my_toolchanger_overrides.cfg]
   ```

3. In `my_toolchanger_overrides.cfg`, redefine only what differs:

   ```ini
   [toolchanger]
   safe_z: 25
   travel_speed: 180

   [tool tool0]
   dock_x: 320
   dock_y: 348
   ```

4. Keep a copy of the original `examples/` files intact so you can
   always check defaults and comments.

This makes it much easier to:

- Pull updates from the upstream repo
- See what you changed vs the defaults
- Debug configuration issues

---

## 6. Checklist After Configuration

Once you’ve adjusted the config, run this checklist:

- [ ] Klipper starts without errors
- [ ] All MCUs / boards connect correctly
- [ ] Homing works (`G28`)
- [ ] Each tool can be picked up and dropped off without collision
- [ ] Tool presence sensors (if used) report correctly
- [ ] `SET_INITIAL_TOOL` works (no errors)
- [ ] `T0` … `Tn` macros select tools as expected
- [ ] XY calibration (`NUDGE_FIND_TOOL_OFFSETS`) runs successfully
- [ ] Z calibration (`MEASURE_TOOL_Z_OFFSETS`) runs successfully
- [ ] Multi-tool test print completes without crashes

If something fails, check:

- The relevant section in this document
- The comments in the example config files
- `TROUBLESHOOTING.md` (if present)
- The Klipper log (`klippy.log`) for stack traces and error messages

Once all of the above work reliably, your configuration should be
ready for real multi-tool production prints.
