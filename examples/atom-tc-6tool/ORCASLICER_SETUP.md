# OrcaSlicer Multi-Tool Setup Guide

**Author:** PrintStructor  
**Version:** 2.5  
**For:** VORON 6-Tool Toolchanger

---

## Overview

This guide covers OrcaSlicer configuration for the VORON 6-tool toolchanger, including:
- Machine G-code templates
- Post-processing script for automatic tool shutdown
- Tool temperature management
- Multi-material printing workflow

---

## Machine G-Code Templates

### Machine Start G-Code

```gcode
PRINT_START BED_TEMP=[first_layer_bed_temperature] TOOL_TEMP={first_layer_temperature[initial_tool]} INITIAL_TOOL=[initial_tool]
SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]
```

**What it does:**
- Calls custom `PRINT_START` macro with parameters
- Sets bed and tool temperatures from slicer
- Specifies which tool starts the print
- Tracks total layer count for display

### Machine End G-Code

```gcode
PRINT_END
```

**What it does:**
- Calls custom `PRINT_END` macro
- Retracts filament, parks toolhead
- Turns off heaters and fans
- Performs cleanup

### Before Layer Change G-Code

```gcode
G92 E0
```

**What it does:**
- Resets extruder position to zero
- Prevents E-position overflow on long prints

### Layer Change G-Code

```gcode
SET_PRINT_STATS_INFO CURRENT_LAYER={layer_num + 1}
```

**What it does:**
- Updates current layer number for display
- Enables accurate progress tracking

### Change Filament G-Code

```gcode
M104 S{temperature[next_extruder]} T[next_extruder] ; set new tool temperature so it can start heating while changing
```

**What it does:**
- Pre-heats next tool during tool change
- Reduces waiting time between tools
- Inserted automatically by OrcaSlicer before tool changes

### Pause G-Code

```gcode
PAUSE
```

**What it does:**
- Calls custom `PAUSE` macro
- Parks toolhead safely
- Maintains temperatures
- Allows manual intervention

---

## Post-Processing Script: Auto Tool Shutdown

### Purpose

By default, OrcaSlicer keeps unused tools at a standby temperature (100°C) after their last use. This wastes energy and generates unnecessary heat in the chamber.

This post-processing script automatically inserts shutdown commands (`M104 S0`) after the last usage of each tool, completely turning off unused hotends.

### Benefits

- **Energy Savings:** Reduces power consumption by ~50W per unused tool
- **Thermal Management:** Less chamber heat buildup
- **Component Longevity:** Reduces unnecessary hotend wear
- **Automated:** No manual G-code editing required

### How It Works

1. **Scans G-code** for tool usage patterns and extrusion moves
2. **Identifies** last usage of each tool
3. **Locates** OrcaSlicer's standby command (`M104 S100 T{tool}`)
4. **Inserts** shutdown command (`M104 S0 T{tool}`) immediately after standby
5. **Generates** detailed report in G-code header

### Installation

#### 1. Save the Script

Save the following Python script as:
```
/home/pi/orcaslicer_tool_shutdown.py
```

Make it executable:
```bash
chmod +x /home/pi/orcaslicer_tool_shutdown.py
```

#### 2. Configure OrcaSlicer

**In OrcaSlicer:**
1. Go to: **Printer Settings** → **Machine G-code** tab
2. Find: **Post-processing scripts** field
3. Enter:
   ```
   /usr/bin/python3 "/home/pi/orcaslicer_tool_shutdown.py"
   ```

#### 3. Test

Slice a multi-tool print and check the G-code:
```bash
# Look for AUTO-SHUTDOWN comments
grep "AUTO-SHUTDOWN" your_print.gcode
```

---

## Python Script: orcaslicer_tool_shutdown.py

```python
#!/usr/bin/env python3
"""
OrcaSlicer Post-Processing Script: Automatisches Tool-Shutdown nach letzter Verwendung
Version: 2.5
Autor: Multi-Tool Klipper Setup

CHANGELOG v2.5:
- FIX: Toolchange-Zählung korrigiert (nur echte Wechsel zählen)
- FIX: Zeile 131: Prüfung ob previous_tool != new_tool

CHANGELOG v2.4:
- VEREINFACHT: Sucht rückwärts nach letztem "M104 S100 T{tool}" (Standby)
- FIX: Fügt M104 S0 direkt danach ein (überschreibt Standby)
- ENTFERNT: Komplexe CP TOOLCHANGE Suche (nicht mehr nötig)
- ERGEBNIS: ~100 Zeilen weniger Code, robuster und einfacher

CHANGELOG v2.3:
- FIX: Sucht nach CP TOOLCHANGE START Marker für robuste Einfügeposition
- FIX: Korrekte M104 Syntax: "M104 S0 T{tool}" (wie Orca)

Dieses Script analysiert den von OrcaSlicer generierten GCode und fügt automatisch
Shutdown-Befehle (M104 S0) direkt nach Orca's Standby-Befehlen ein.
"""

import sys
import re
import os
from collections import defaultdict
from datetime import datetime
import argparse

class ToolShutdownProcessor:
    def __init__(self, gcode_file, dry_run=False):
        self.gcode_file = gcode_file
        self.lines = []
        self.tool_usage = defaultdict(list)
        self.tool_changes = defaultdict(int)
        self.current_tool = 0
        self.total_tools = set()
        self.shutdown_inserted = set()
        self.dry_run = dry_run
        
        # Extruder-Tracking
        self.e_mode = 'ABS'
        self.e_pos = 0.0
        
        # Regex-Pattern
        self.re_e = re.compile(r'(?<!;)\bE([-+]?\d*\.?\d+)')
        self.re_t = re.compile(r'(?<!;)\bT(\d+)\b')
        self.re_g92_e = re.compile(r'^\s*G92\s+.*E([-+]?\d*\.?\d+)', re.IGNORECASE)
        
        # Konfiguration
        self.config = {
            'shutdown_heater': True,
            'shutdown_fan': False,
            'add_comments': True,
            'create_backup': True,
            'generate_report': True,
        }
        
    def load_gcode(self):
        """Lädt die GCode-Datei"""
        try:
            with open(self.gcode_file, 'r', encoding='utf-8') as f:
                self.lines = f.readlines()
            print(f"✓ Geladen: {len(self.lines)} Zeilen aus {self.gcode_file}")
            if self.dry_run:
                print("⚠ DRY-RUN Modus: Es werden keine Änderungen gespeichert")
            return True
        except Exception as e:
            print(f"✗ Fehler beim Laden der Datei: {e}")
            return False
    
    def analyze_tool_usage(self):
        """Analysiert Tool-Verwendung mit M82/M83 Support"""
        previous_tool = None
        in_start_gcode = True
        
        for line_num, raw_line in enumerate(self.lines):
            line = raw_line.strip()
            
            if ';LAYER:' in line or ';layer' in line.lower():
                in_start_gcode = False
            
            if line.startswith('M82'):
                self.e_mode = 'ABS'
                continue
            elif line.startswith('M83'):
                self.e_mode = 'REL'
                continue
            
            g92_match = self.re_g92_e.match(line)
            if g92_match:
                self.e_pos = float(g92_match.group(1))
                continue
            
            t_match = self.re_t.search(line)
            if t_match:
                new_tool = int(t_match.group(1))
                # FIX v2.5: Nur zählen wenn ECHTER Wechsel (previous_tool != new_tool)
                if not in_start_gcode and previous_tool is not None and previous_tool != new_tool:
                    self.tool_changes[new_tool] += 1
                self.current_tool = new_tool
                previous_tool = new_tool
                self.total_tools.add(new_tool)
                continue
            
            if line and line[0] == 'G' and line[:2] in ('G0', 'G1'):
                e_match = self.re_e.search(line)
                if not e_match:
                    continue
                
                e_value = float(e_match.group(1))
                is_extrusion = False
                
                if self.e_mode == 'ABS':
                    if e_value > self.e_pos + 1e-6:
                        is_extrusion = True
                    self.e_pos = e_value
                else:
                    if e_value > 1e-6:
                        is_extrusion = True
                
                if is_extrusion:
                    self.tool_usage[self.current_tool].append(line_num)
                    self.total_tools.add(self.current_tool)
        
        print(f"✓ Analyse abgeschlossen:")
        for tool in sorted(self.total_tools):
            usage_count = len(self.tool_usage[tool])
            change_count = self.tool_changes[tool]
            if usage_count > 0:
                first_line = min(self.tool_usage[tool])
                last_line = max(self.tool_usage[tool])
                print(f"  T{tool}: {usage_count} Extrusionen, {change_count} Toolwechsel, Zeile {first_line}-{last_line}")
    
    def find_last_standby_command(self, tool_num):
        """
        NEU v2.4: Einfache Rückwärts-Suche nach letztem Standby-Befehl.
        
        Sucht nach: "M104 S100 T{tool_num}"
        S100 = Orca's Standby-Temperatur (eindeutig, keine Drucktemperatur)
        
        Returns: Index NACH dem Standby-Befehl, oder None
        """
        # Durchsuche von hinten nach vorne
        for idx in range(len(self.lines) - 1, -1, -1):
            line = self.lines[idx].strip()
            
            # Suche EXAKT nach "M104 S100 T{tool_num}"
            if f'M104 S100 T{tool_num}' in line:
                print(f"  ✓ Gefunden: Letzter Standby für T{tool_num} bei Zeile {idx}")
                return idx + 1  # Füge direkt danach ein
        
        # Kein Standby gefunden - Tool wird vermutlich bis Ende verwendet
        return None
    
    def find_safe_insertion_point(self, last_usage_line, tool):
        """
        v2.4: Stark vereinfachte Einfügelogik
        """
        # Suche nach letztem Standby-Befehl für dieses Tool
        insert_after_standby = self.find_last_standby_command(tool)
        
        if insert_after_standby:
            # Perfekt! Füge nach Standby ein
            return insert_after_standby
        
        # Kein Standby gefunden - Tool bleibt bis Ende aktiv
        # In diesem Fall KEINEN Shutdown einfügen
        print(f"  ℹ T{tool}: Kein Standby gefunden - bleibt aktiv bis Ende")
        return None
    
    def generate_shutdown_commands(self, tool_num):
        """
        Generiert Shutdown-Befehle
        
        v2.4: Korrekte Syntax wie Orca: "M104 S0 T{tool}"
        """
        commands = []
        
        if self.config['add_comments']:
            commands.append(f"; ========================================\n")
            commands.append(f"; AUTO-SHUTDOWN: Tool T{tool_num}\n")
            commands.append(f"; Überschreibt Orca Standby (100°C → 0°C)\n")
            commands.append(f"; ========================================\n")
        
        if self.config['shutdown_heater']:
            # Standard M104 - S kommt VOR T (wie bei Orca!)
            commands.append(f"M104 S0 T{tool_num}          ; Hotend T{tool_num} komplett abschalten\n")
        
        if self.config['shutdown_fan']:
            commands.append(f"M106 P{tool_num} S0          ; Part-Cooling-Fan T{tool_num} abschalten\n")
        
        if self.config['add_comments']:
            commands.append(f"; Energieeinsparung: Tool T{tool_num} vollständig deaktiviert\n")
            commands.append("\n")
        
        return commands
    
    def insert_shutdown_commands(self):
        """Fügt Shutdown-Befehle ein (von hinten nach vorne)"""
        last_usage = {}
        for tool in self.total_tools:
            if self.tool_usage[tool]:
                last_usage[tool] = max(self.tool_usage[tool])
        
        tools_by_last_use = sorted(last_usage.items(), key=lambda x: x[1], reverse=True)
        output_lines = self.lines.copy()
        
        for tool, last_line in tools_by_last_use:
            insert_at = self.find_safe_insertion_point(last_line, tool)
            
            if insert_at is None:
                continue
            
            shutdown_cmds = self.generate_shutdown_commands(tool)
            
            for cmd in reversed(shutdown_cmds):
                output_lines.insert(insert_at, cmd)
            
            self.shutdown_inserted.add(tool)
            print(f"✓ Shutdown für T{tool} eingefügt bei Zeile {insert_at}")
        
        return output_lines
    
    def generate_report(self):
        """Generiert Report für GCode-Header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_changes = sum(self.tool_changes.values())
        total_extrusions = sum(len(usage) for usage in self.tool_usage.values())
        
        report = []
        report.append("; ╔════════════════════════════════════════════════════════════╗\n")
        report.append("; ║  AUTOMATISCHER TOOL-SHUTDOWN REPORT                        ║\n")
        report.append("; ╚════════════════════════════════════════════════════════════╝\n")
        report.append(f"; Verarbeitet am: {timestamp}\n")
        report.append(f"; Script: orcaslicer_tool_shutdown.py v2.5\n")
        report.append(f"; Modus: {'DRY-RUN' if self.dry_run else 'PRODUKTIV'}\n")
        report.append(";\n")
        report.append("; Gesamt-Statistik:\n")
        report.append("; ──────────────────────────────────────────────────────────\n")
        report.append(f";   • Tools: {len(self.total_tools)}\n")
        report.append(f";   • Toolwechsel: {total_changes}\n")
        report.append(f";   • Extrusionen: {total_extrusions}\n")
        report.append(f";   • Auto-Shutdowns: {len(self.shutdown_inserted)}\n")
        
        if total_changes > 0:
            est_time = total_changes * 20
            report.append(f";   • Toolwechsel-Zeit: ~{est_time//60}m {est_time%60}s\n")
        
        report.append(";\n")
        report.append("; Tool-Verwendung:\n")
        report.append("; ──────────────────────────────────────────────────────────\n")
        
        for tool in sorted(self.total_tools):
            if self.tool_usage[tool]:
                usage = len(self.tool_usage[tool])
                changes = self.tool_changes[tool]
                first = min(self.tool_usage[tool])
                last = max(self.tool_usage[tool])
                
                report.append(f";   Tool T{tool}:\n")
                report.append(f";     • Wechsel: {changes}x\n")
                report.append(f";     • Extrusionen: {usage}\n")
                report.append(f";     • Zeilen: {first} bis {last}\n")
                
                if changes > 0:
                    avg = usage / changes
                    report.append(f";     • Ø Extrusionen/Aktivierung: {avg:.1f}\n")
                
                status = "✓ Auto-Shutdown" if tool in self.shutdown_inserted else "○ Aktiv bis Ende"
                report.append(f";     • Status: {status}\n")
                report.append(";\n")
        
        report.append("; ══════════════════════════════════════════════════════════\n")
        report.append("; v2.5: Korrigierte Toolwechsel-Zählung (nur echte Wechsel)\n")
        report.append("; v2.4: Vereinfachte Rückwärts-Suche nach M104 S100 T{tool}\n")
        report.append("; Syntax: M104 S0 T{tool} (wie Orca Standby-Format)\n")
        report.append("; ══════════════════════════════════════════════════════════\n")
        report.append("\n")
        
        return report
    
    def insert_report(self, output_lines):
        """Fügt Report ein"""
        report = self.generate_report()
        
        insert_at = 0
        for idx, line in enumerate(output_lines):
            if ';LAYER:0' in line or 'thumbnail end' in line.lower():
                insert_at = idx if ';LAYER:0' in line else idx + 1
                break
        
        for line in reversed(report):
            output_lines.insert(insert_at, line)
        
        return output_lines
    
    def save_output(self, output_lines):
        """Speichert Output"""
        if self.dry_run:
            print("\n" + "="*60)
            print("DRY-RUN: Folgende Änderungen würden vorgenommen:")
            print("="*60)
            for tool in sorted(self.shutdown_inserted):
                print(f"  • T{tool}: Shutdown würde eingefügt")
            print(f"\n  {len(output_lines) - len(self.lines)} Zeilen würden hinzugefügt")
            print("="*60)
            return True
        
        if self.config['create_backup']:
            backup = self.gcode_file + '.bak'
            try:
                with open(backup, 'w', encoding='utf-8') as f:
                    f.writelines(self.lines)
                print(f"✓ Backup: {backup}")
            except Exception as e:
                print(f"⚠ Backup-Fehler: {e}")
        
        try:
            with open(self.gcode_file, 'w', encoding='utf-8') as f:
                f.writelines(output_lines)
            print(f"✓ Gespeichert: {self.gcode_file}")
            return True
        except Exception as e:
            print(f"✗ Speicher-Fehler: {e}")
            return False
    
    def process(self):
        """Hauptprozess"""
        print("=" * 60)
        print("OrcaSlicer Tool-Shutdown v2.5 (korrigiert)")
        print("=" * 60)
        
        if not self.load_gcode():
            return False
        
        print("\nAnalysiere Tool-Verwendung...")
        self.analyze_tool_usage()
        
        if not self.total_tools:
            print("\n⚠ Keine Tools gefunden")
            return False
        
        print("\nFüge Shutdown-Befehle ein...")
        output_lines = self.insert_shutdown_commands()
        
        if self.config['generate_report']:
            print("\nGeneriere Report...")
            output_lines = self.insert_report(output_lines)
        
        print("\nSpeichere..." if not self.dry_run else "\nDry-Run...")
        success = self.save_output(output_lines)
        
        print("\n" + "=" * 60)
        if success:
            print("✓ ERFOLGREICH" if not self.dry_run else "✓ DRY-RUN OK")
            print(f"  • Original: {len(self.lines)} Zeilen")
            print(f"  • Neu: {len(output_lines)} Zeilen")
            print(f"  • Shutdowns: {len(self.shutdown_inserted)}")
        else:
            print("✗ FEHLER")
        print("=" * 60)
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description='OrcaSlicer Tool-Shutdown v2.5',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python3 orcaslicer_tool_shutdown.py print.gcode
  python3 orcaslicer_tool_shutdown.py --dry-run print.gcode

OrcaSlicer Integration:
  Printer Settings → Machine G-code → Post-processing scripts:
  /usr/bin/python3 "/pfad/zum/orcaslicer_tool_shutdown.py"
        """
    )
    
    parser.add_argument('gcode_file', nargs='?', help='GCode-Datei')
    parser.add_argument('--dry-run', action='store_true', help='Test-Modus')
    parser.add_argument('--version', action='version', version='v2.5')
    
    args = parser.parse_args()
    
    if not args.gcode_file:
        parser.print_help()
        sys.exit(1)
    
    if not os.path.exists(args.gcode_file):
        print(f"✗ Datei nicht gefunden: {args.gcode_file}")
        sys.exit(1)
    
    processor = ToolShutdownProcessor(args.gcode_file, dry_run=args.dry_run)
    success = processor.process()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

---

## Script Features

### Automatic Analysis
- Detects tool usage patterns throughout G-code
- Tracks extrusion moves per tool
- Counts tool changes accurately (v2.5 fix)
- Identifies last usage of each tool

### Smart Insertion
- Searches backward for OrcaSlicer's standby command (`M104 S100 T{tool}`)
- Inserts shutdown (`M104 S0 T{tool}`) immediately after
- Preserves original G-code structure
- Only affects tools that have a standby command

### Report Generation
- Detailed statistics in G-code header
- Tool usage summary (changes, extrusions, line ranges)
- Auto-shutdown status per tool
- Estimated tool change time

### Safety Features
- Automatic backup (`.bak` file)
- Dry-run mode for testing (`--dry-run`)
- Preserves comments and formatting
- Error handling with helpful messages

---

## Usage Examples

### Test Mode (Dry Run)
```bash
# Test without modifying file
python3 /home/pi/orcaslicer_tool_shutdown.py --dry-run /path/to/print.gcode
```

### Manual Execution
```bash
# Process a single file
python3 /home/pi/orcaslicer_tool_shutdown.py /path/to/print.gcode

# Check result
grep "AUTO-SHUTDOWN" /path/to/print.gcode
```

### Automatic (via OrcaSlicer)
Just slice normally - script runs automatically after slicing completes.

---

## Expected Behavior

### Before (OrcaSlicer Default)
```gcode
; Tool T1 finishes printing
G1 X100 Y100 E50.0    ; Last extrusion
...
M104 S100 T1          ; Standby at 100°C
...
; Print continues with other tools
; T1 stays at 100°C unnecessarily
```

### After (With Script)
```gcode
; Tool T1 finishes printing
G1 X100 Y100 E50.0    ; Last extrusion
...
M104 S100 T1          ; Standby at 100°C
; ========================================
; AUTO-SHUTDOWN: Tool T1
; Überschreibt Orca Standby (100°C → 0°C)
; ========================================
M104 S0 T1            ; Hotend T1 komplett abschalten
; Energieeinsparung: Tool T1 vollständig deaktiviert
...
; Print continues with other tools
; T1 is now completely off
```

---

## Troubleshooting

### Script Not Running
**Check:**
1. Script path correct in OrcaSlicer
2. Script has execute permissions: `chmod +x orcaslicer_tool_shutdown.py`
3. Python3 installed: `which python3`

### No Shutdowns Inserted
**Possible causes:**
1. Tool used until end of print (no standby command)
2. Single-tool print (no multi-tool detection)
3. OrcaSlicer not generating standby commands

**Check with dry-run:**
```bash
python3 /home/pi/orcaslicer_tool_shutdown.py --dry-run print.gcode
```

### Backup Files Accumulating
**Clean up:**
```bash
# Remove backup files older than 7 days
find ~/OrcaSlicer/ -name "*.gcode.bak" -mtime +7 -delete
```

---

## Advanced Configuration

### Disable Features (Edit Script)

**Disable Comments:**
```python
self.config = {
    'shutdown_heater': True,
    'shutdown_fan': False,
    'add_comments': False,      # ← Change to False
    'create_backup': True,
    'generate_report': True,
}
```

**Disable Backup:**
```python
self.config = {
    'shutdown_heater': True,
    'shutdown_fan': False,
    'add_comments': True,
    'create_backup': False,     # ← Change to False
    'generate_report': True,
}
```

**Enable Fan Shutdown:**
```python
self.config = {
    'shutdown_heater': True,
    'shutdown_fan': True,       # ← Change to True
    'add_comments': True,
    'create_backup': True,
    'generate_report': True,
}
```

---

## Best Practices

### Temperature Settings
- **Printing Temp:** 200-260°C (material dependent)
- **Standby Temp:** 100°C (OrcaSlicer default, overridden by script)
- **Off Temp:** 0°C (script sets this for unused tools)

### Tool Change Behavior
- Pre-heat next tool during change: ✓ (via "Change filament G-code")
- Keep unused tools at standby: ✗ (script shuts down)
- Resume to printing temp on tool select: ✓ (automatic)

### Multi-Material Projects
1. Assign different colors/materials to tools
2. Configure per-tool temperature profiles
3. Let script manage energy efficiency automatically

---

## Verification

After slicing, check your G-code:

```bash
# Count auto-shutdowns
grep -c "AUTO-SHUTDOWN" print.gcode

# View report
head -n 50 print.gcode | grep "^;"

# Check specific tool
grep "T1" print.gcode | grep "M104"
```

Expected output:
```
M104 S100 T1          ; Standby
M104 S0 T1            ; Auto-shutdown (script added)
```

---

## Performance Impact

- **Slicing Time:** +0.1-0.5 seconds per print
- **File Size:** +100-500 bytes (comments + commands)
- **Print Quality:** No impact (changes only post-print temperatures)
- **Energy Savings:** ~50W per unused tool × remaining print time

---

## Related Documentation

- **Configuration Guide:** `README.md` (in this directory)
- **Main Project:** `/home/pi/klipper-toolchanger/README.md`
- **OrcaSlicer Docs:** https://github.com/SoftFever/OrcaSlicer

---

**Version:** 2.5  
**Last Updated:** 2025-11-16  
**Author:** PrintStructor
