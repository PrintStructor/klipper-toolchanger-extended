# Hardware Files

This directory contains CAD files, STL files, and documentation for the physical hardware components of the Klipper Toolchanger Extended system.

---

## Directory Structure

```
hardware/
├── ATOM-toolhead/           # ATOM toolhead system files
│   ├── STL/                 # Print-ready STL files
│   ├── CAD/                 # Source CAD files (STEP, F3D, etc.)
│   └── README.md            # ATOM-specific documentation
└── README.md                # This file
```

---

## ATOM Toolhead System

The **ATOM toolhead** is an exclusive design created by the developer of the **Reaper Toolhead**, specifically engineered for this toolchanger project.

### Key Features:
- **Simple 4-point dock path** - Reliable and easy to tune
- **Compact design** - Optimized for multi-tool setups
- **Proven reliability** - Production-tested configuration
- **Tool detection integration** - Built-in sensor mounting
- **CAN bus ready** - Designed for BTT EBB36/42 boards

---

## Adding Your Files

### CAD Files
Place source CAD files in the appropriate subdirectory:
- STEP files: `ATOM-toolhead/CAD/*.step`
- Fusion 360: `ATOM-toolhead/CAD/*.f3d`
- Other formats: `ATOM-toolhead/CAD/`

### STL Files
Place print-ready STL files in:
- `ATOM-toolhead/STL/*.stl`

### Documentation
Update the `ATOM-toolhead/README.md` with:
- Print settings
- Assembly instructions
- BOM (Bill of Materials)
- Wiring diagrams

---

## Notes

- All hardware designs are licensed under the same GPL-3.0 license as the software
- When sharing modifications, please maintain attribution to original designers
- For questions about the ATOM design, contact PrintStructor

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18  
**License:** GPL-3.0
