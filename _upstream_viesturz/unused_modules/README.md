# Cleanup Archive

## Inhalt
Dieser Ordner enthält ungenutzte Dateien, die am 2025-11-19 aus dem aktiven Projekt entfernt wurden.

### Python-Module (5)
Diese Module wurden nicht in der ATOM TC Konfiguration verwendet:
- `bed_thermal_adjust.py` - Thermische Bett-Kompensation (Viesturz Feature)
- `manual_rail.py` - Manuelle Rail-Steuerung (Viesturz Feature)
- `multi_fan.py` - Multi-Fan-Management (Viesturz Feature)
- `tool_probe.py` - Per-Tool Z-Endstop (ersetzt durch Beacon)
- `tool_probe_endstop.py` - Probe-basiertes Endstop (ungenutzt)

### Dokumentation (3)
Dokumentation zu den ungenutzten Modulen:
- `bed_thermal_adjust.md` - Leer
- `manual_rail.md` - Manual Rail Dokumentation
- `tool_probe.md` - Tool Probe Dokumentation

## Wiederherstellung
Falls eine Datei doch benötigt wird:
```bash
# Einzelne Datei wiederherstellen
cp _cleanup_archive/klipper_extras/[filename].py klipper/extras/
cp _cleanup_archive/docs/[filename].md docs/

# FIRMWARE_RESTART in Klipper durchführen
```

## Löschen
Wenn du sicher bist, dass diese Dateien nicht mehr benötigt werden:
```bash
rm -rf _cleanup_archive/
```

---
**Archiviert:** 2025-11-19
**Grund:** Ungenutzte Module aus Viesturz Fork
**Analyse:** Siehe SCRIPT_USAGE_ANALYSIS.md und DOCS_CLEANUP_ANALYSIS.md
