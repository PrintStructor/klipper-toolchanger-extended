# ATOM Toolhead System

**Designer:** Creator of the Reaper Toolhead  
**Project:** Exclusive design for Klipper Toolchanger Extended  
**Version:** 1.0.0

---

## Overview

The ATOM toolhead is a custom-designed toolchanging system specifically created for this project. It features a simple, reliable 4-point docking mechanism that has been production-tested on a 6-tool VORON setup.

---

## Features

- **Simple 4-Point Dock Path** - Easy to calibrate and maintain
- **Reliable Tool Detection** - Integrated sensor mounting
- **CAN Bus Integration** - Designed for BTT EBB36/42 boards
- **Compact Design** - Space-efficient for multi-tool arrays
- **Proven Performance** - Tested in production environment

---

## Files

### STL/
Place your print-ready STL files here. Organize by component:
- Toolhead body
- Dock components
- Mounting brackets
- Cable management parts

### CAD/
Place your source CAD files here:
- STEP files for maximum compatibility
- Native CAD formats (F3D, SLDPRT, etc.)
- Assembly files

---

## Recommended Print Settings

*To be added - customize based on your specific design requirements*

**Example:**
- Material: ABS or ASA
- Layer Height: 0.2mm
- Wall Count: 4
- Infill: 40%
- Supports: As needed

---

## Assembly Instructions

*To be added - include step-by-step assembly guide*

1. Print all required parts
2. Install heat inserts
3. Mount CAN board
4. Wire sensors
5. Install on toolchanger
6. Calibrate offsets

---

## Bill of Materials (BOM)

*To be added - list all hardware components needed*

**Example:**
- BTT EBB36/42 CAN board
- M3 heat inserts
- M3 screws (various lengths)
- Filament sensor switch
- Wire harness
- Fans (hotend + part cooling)

---

## Wiring

*To be added - wiring diagrams and pin assignments*

### CAN Bus
- CAN_H: Connect to CAN bus high
- CAN_L: Connect to CAN bus low
- 24V/GND: Power supply

### Sensors
- Tool detection pin: [specify pin]
- Filament sensor: [specify pin]

---

## Dock Configuration

The ATOM dock uses a simple 4-point path:

```python
params_atom_dock_path: [
    {'y':9, 'z':1},              # Approach position
    {'y':8, 'z':0.5, 'f':0.5},   # Verification point
    {'y':0, 'z':0.5},            # Engage position
    {'y':0, 'z':-10}             # Final park position
]
```

The `'f':0.5` parameter marks the verification point where tool presence is checked.

---

## Tuning Guide

### Dock Position Calibration

1. Move toolhead manually to each dock position
2. Record X, Y, Z coordinates
3. Update in corresponding TX.cfg:
   ```ini
   params_park_x: [X coordinate]
   params_park_y: [Y coordinate]
   params_park_z: [Z coordinate]
   ```

### Path Speed Adjustment

Start slow for testing:
```ini
params_path_speed: 300  # 5 mm/s for initial testing
```

Increase once reliable:
```ini
params_path_speed: 3000  # 50 mm/s for production
```

### Tool Detection

Test detection sensor:
```gcode
QUERY_ENDSTOPS
QUERY_FILAMENT_SENSOR SENSOR=T0_filament_sensor
```

---

## Compatibility

**Tested With:**
- VORON 2.4 (350mm build)
- BTT EBB36 v1.2
- BTT EBB42 v1.2
- Beacon RevH probe
- NUDGE probe

**Compatible With:**
- Most CoreXY printers
- CAN bus control boards
- Various extruder types

---

## Credits

**Design:** Creator of the Reaper Toolhead  
**Integration & Testing:** PrintStructor  
**Project:** [Klipper Toolchanger Extended](https://github.com/PrintStructor/klipper-toolchanger-extended)

---

## License

This hardware design is licensed under GPL-3.0, consistent with the software project.

**You are free to:**
- Use the design for personal or commercial purposes
- Modify and adapt the design
- Share the design with others

**Under the conditions:**
- Maintain attribution to original designer
- Share modifications under the same license
- Document any changes made

---

## Support & Discussion

- **Issues:** [GitHub Issues](https://github.com/PrintStructor/klipper-toolchanger-extended/issues)
- **Discussions:** [GitHub Discussions](https://github.com/PrintStructor/klipper-toolchanger-extended/discussions)

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**Status:** Files to be added by maintainer
