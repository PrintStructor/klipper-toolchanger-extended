# About This Fork

## What This Is

An extension of [viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger) adding safety features, guided calibration, and a complete 6-tool VORON configuration.

---

## Feature Comparison

| Feature | viesturz | TypQxQ | This Fork |
|---------|----------|--------|-----------|
| **Core toolchanger logic** | ✅ | ✅ | ✅ |
| **Two-stage pickup verification** | ❌ | ❌ | ✅ |
| **Tool presence monitoring** | ❌ | ❌ | ✅ |
| **Heater shutoff on tool loss** | ❌ | ❌ | ✅ |
| **TAXY AI calibration** | ❌ | ❌ | ✅ |
| **NUDGE probe calibration** | ❌ | ❌ | ✅ |
| **Batch calibration (full matrix)** | ❌ | ❌ | ✅ |
| **Per-tool Z babystepping** | ❌ | ❌ | ✅ |
| **Complete example configs** | ⚠️ Minimal | ⚠️ Basic | ✅ Full |
| **LED/KNOMI integration** | ❌ | ❌ | ✅ |
| **Virtual tools** | ❌ | ✅ | ❌ |
| **MMU-style systems** | ⚠️ | ✅ | ❌ |

---

## Which Project to Choose?

### This fork if:
- Building a 6-tool VORON with ATOM-style toolheads
- Want complete, working configuration to adapt
- Value safety features and guided calibration

### viesturz base if:
- Custom hardware that doesn't match ATOM design
- Want maximum flexibility
- Prefer building from scratch

### TypQxQ if:
- Need virtual tool support
- Building MMU-style systems

---

## Key Features

**Safety:**
- Two-stage pickup with verification
- Tool presence monitoring during prints
- Pause-based error recovery (not emergency stops)
- Automatic heater shutoff on tool loss

**Calibration (v1.1.0+):**
- TAXY AI-based XY calibration (primary, ~5µm precision)
- kTAMV OpenCV-based XY calibration (legacy/fallback)
- NUDGE physical probe (backup)
- Batch calibration for full offset matrix
- Per-tool Z babystepping during prints

**Configuration:**
- Complete 6-tool VORON 2.4 + ATOM setup
- LED status integration
- KNOMI display support
- Per-tool input shaper

---

## Hardware Reference

Designed for:
- VORON 2.4 CoreXY (350mm)
- 6× ATOM toolheads (~236g each)
- Beacon probe (Z calibration)
- CPAP shuttle cooling
- CAN bus toolhead boards

**Different hardware requires substantial modifications.**

---

## Time Estimates

| Task | Time |
|------|------|
| Software setup | 3-5 hours |
| Initial calibration (6 tools) | 30-60 min |
| Recalibration (after changes) | 20-30 min |

---

## Credits

- **[viesturz/klipper-toolchanger](https://github.com/viesturz/klipper-toolchanger)** – Core framework
- **[TAXY](https://github.com/PrintStructor/TAXY)** – AI-based XY calibration (primary)
- **[kTAMV](https://github.com/PrintStructor/kTAMV)** by TypQxQ – OpenCV calibration (legacy, GPL-3.0)
- **[NUDGE](https://github.com/zruncho3d/nudge)** by Zruncho – Physical probe calibration
- **ATOM Toolhead** by Alex/APDMachine

---

**Version:** 1.1.0
**Last Updated:** 2026-01-10
**License:** GPL-3.0
