# Documentation – klipper-toolchanger-extended

This folder is the **documentation hub** for the `klipper-toolchanger-extended` repository.

The goal of these docs is to turn the raw Klipper modules and configs into a **practical, repeatable setup guide** for multi-tool / toolchanger printers.

---

## What This Repository Provides

`klipper-toolchanger-extended` builds on top of Viesturs Zarins’ original [`klipper-toolchanger`](https://github.com/viesturz/klipper-toolchanger) and adds:

- A **reference multi-tool configuration** (`atom`)
- Extended macros for safer and more robust toolchanging
- A place for **real-world examples** and workflows
- A structure to document how everything fits together

Where the original project focuses on the **core Klipper extensions**, this fork focuses on the **full stack** around them.

---

## The `atom` Reference Configuration

Throughout the docs you will see references to a configuration called **`atom`**:

- `atom` is the name of the **reference printer setup** used by the author
- It is based on a toolhead design by **APDesign & Machine (APDM)**  
  – see https://github.com/APDMachine and https://reapertoolhead.com

On a typical Klipper host, this configuration lives under:

```text
printer_data/config/atom/
```

It contains:

- Core toolchanger config (`toolchanger.cfg`)
- Toolchanger macros (`toolchanger_macros.cfg`)
- Calibration macros (`calibrate_offsets.cfg`)
- Per-tool config (`T0.cfg`, `T1.cfg`, …)
- Optional integrations (Beacon, LEDs, KNOMI, etc.)

You can treat `atom` as a **working, opinionated example** and adapt it to your own printer.

---

## Suggested Reading Order

As the docs grow, a good reading flow will be:

1. **Overview & Concepts**
   - What the toolchanger modules do
   - How tools, offsets and detection are modelled

2. **Core Setup**
   - Installing the Python modules (extras)
   - Wiring and basic config of tools
   - First successful tool change

3. **Calibration**
   - XY calibration (e.g. NUDGE)
   - Z calibration (e.g. Beacon or similar probe)
   - Saving offsets and validating them

4. **Runtime & Safety**
   - Tool presence monitoring
   - Error handling & pause/resume flows
   - Safe startup & shutdown sequences

5. **Advanced Topics**
   - Per-tool tuning (input shaper, pressure advance, etc.)
   - Integrating with slicers (OrcaSlicer, PrusaSlicer, …)
   - Multi-material / multi-profile setups

---

## How to Navigate This Folder

Planned structure (may evolve over time):

```text
docs/
├── overview.md          # High-level explanation of the stack
├── installation.md      # Step-by-step install guide
├── configuration.md     # How to wire configs together
├── atom-reference.md    # Deep dive into the atom config
├── calibration.md       # XY + Z calibration flows
├── runtime.md           # Monitoring, errors, recovery
└── faq.md               # Common problems & questions
```

At the moment, not all of these files may exist yet – but the goal is to fill them with **practical, battle-tested knowledge** from daily multi-tool usage.

---

## Upstream Documentation

For details on the core modules shipped by the original project, refer to:

- `toolchanger.md`
- `tool_probe.md`
- `tools_calibrate.md`
- `rounded_path.md`

You’ll find them in Viesturs’ repository:  
https://github.com/viesturz/klipper-toolchanger

Think of those docs as the **API reference** for the Klipper modules, and this folder as the **integration & real-world usage guide**.

---

## Contributing to the Docs

If you:

- Run a different toolchanger geometry
- Use other probes or detection hardware
- Have better macros, safer sequences or clearer explanations

…feel free to open a PR and propose additions or corrections to the docs.

Good documentation is just as important as good code – especially in the world of multi-tool Klipper setups. 🙂
