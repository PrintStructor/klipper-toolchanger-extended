# Upgrade Guide

This guide explains how to upgrade from a previous version of klipper-toolchanger-extended.

## Upgrading from v1.0.x to v1.1.0

### What's New in v1.1.0

- **Batch Calibration**: One-click XY and Z calibration with 30 measurements
  - `KTAMV_CALIBRATE_ALL_TOOLS_XY` - Full matrix XY calibration
  - `BEACON_CALIBRATE_ALL_TOOLS_Z` - Full matrix Z calibration
- **Per-Tool Z Babystepping**: Live Z adjustments during printing
  - `SET_TOOL_Z_ADJUST` - Adjust individual tool Z offset
  - `GLOBAL_Z_ADJUST` - Adjust all tools equally
- **Emergency Abort**: Stop batch calibration mid-process
  - `KTAMV_BATCH_ABORT` / `BEACON_BATCH_ABORT`

### Upgrade Steps

#### 1. Backup Your Configuration

```bash
cp -r ~/printer_data/config/atom ~/printer_data/config/atom.backup.$(date +%Y%m%d)
```

#### 2. Update the Repository

```bash
cd ~/klipper-toolchanger-extended
git pull origin main
```

#### 3. Copy Updated Macro Files

**Important**: Only copy the macro files, NOT `printer.cfg` (which contains your hardware calibration).

```bash
# Copy macro files
cp examples/atom-tc-6tool/atom/tool_calibration.cfg ~/printer_data/config/atom/
cp examples/atom-tc-6tool/atom/toolchanger.cfg ~/printer_data/config/atom/
```

#### 4. Check for Custom Modifications

If you made custom changes to the macro files, compare before overwriting:

```bash
# Show differences
diff ~/printer_data/config/atom/tool_calibration.cfg examples/atom-tc-6tool/atom/tool_calibration.cfg

# Or use a visual diff tool
meld ~/printer_data/config/atom/tool_calibration.cfg examples/atom-tc-6tool/atom/tool_calibration.cfg
```

#### 5. Restart Klipper

In Mainsail/Fluidd console:
```
FIRMWARE_RESTART
```

### Verify the Upgrade

After restart, check that new commands are available:

```
# Should show the macro description
KTAMV_CALIBRATE_ALL_TOOLS_XY
BEACON_CALIBRATE_ALL_TOOLS_Z
SET_TOOL_Z_ADJUST
```

### Files Changed in v1.1.0

| File | Changes |
|------|---------|
| `tool_calibration.cfg` | Added batch calibration macros, per-tool babystepping |
| `toolchanger.cfg` | Minor improvements to tool change logic |

### Rollback (if needed)

If something goes wrong, restore your backup:

```bash
rm -rf ~/printer_data/config/atom
mv ~/printer_data/config/atom.backup.YYYYMMDD ~/printer_data/config/atom
```

Then restart Klipper: `FIRMWARE_RESTART`

---

## General Upgrade Tips

1. **Always backup first** - Your `printer.cfg` contains calibrated offsets that took time to set up
2. **Read the CHANGELOG** - Check what changed between versions
3. **Don't overwrite printer.cfg** - This file contains your hardware-specific settings
4. **Test after upgrade** - Run a quick calibration check before printing
