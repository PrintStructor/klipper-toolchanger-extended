# kTAMV Enhanced Detection

Verbesserte Nozzle-Erkennung für [kTAMV](https://github.com/TypQxQ/kTAMV) mit besserer Zuverlässigkeit und korrektem Seitenverhältnis.

## Verbesserungen

| Feature | Beschreibung |
|---------|-------------|
| **16:9 Seitenverhältnis** | Korrekte Darstellung (keine ovalen Kreise mehr) |
| **Auto-Skalierung** | Detection-Parameter passen sich automatisch an die Auflösung an |
| **CLAHE Preprocessing** | Bessere Erkennung bei unterschiedlichen Lichtverhältnissen |
| **HoughCircles Fallback** | Wenn Blob-Detection fehlschlägt, wird HoughCircles als Backup verwendet |
| **Multi-Blob Handling** | Bei mehreren Erkennungen wird der zentrierteste Blob gewählt |
| **Morphologische Operationen** | Rauschen und Reflektionen werden besser gefiltert |
| **1280x720 Auflösung** | Höhere Auflösung für präzisere Erkennung |

## Detection Cascade

Die verbesserte Erkennung probiert 9 Algorithmus-Kombinationen + HoughCircles Fallback:

1. `standard + YUV` (original)
2. `standard + triangle` (original)
3. `standard + CLAHE` (neu)
4. `relaxed + YUV` (original)
5. `relaxed + triangle` (original)
6. `relaxed + CLAHE` (neu)
7. `relaxed + CLAHE + morphology` (neu)
8. `superRelaxed + median` (original)
9. `superRelaxed + CLAHE + morphology` (neu)
10. `HoughCircles` (neu, Fallback)

## Installation

### Automatisch (via install.sh)

```bash
cd ~/klipper-toolchanger-extended
./install.sh
```

Bei der Installation wirst du gefragt:
```
[kTAMV] Install improved nozzle detection? (CLAHE, HoughCircles fallback) [y/N]
```

### Manuell

1. **Backup erstellen:**
```bash
cp ~/kTAMV/server/ktamv_server_dm.py ~/kTAMV/server/ktamv_server_dm.py.backup
cp ~/kTAMV/server/ktamv_server_io.py ~/kTAMV/server/ktamv_server_io.py.backup
cp ~/kTAMV/server/ktamv_server.py ~/kTAMV/server/ktamv_server.py.backup
```

2. **Verbesserte Dateien kopieren:**
```bash
cp ~/klipper-toolchanger-extended/kTAMV/server/*.py ~/kTAMV/server/
```

3. **kTAMV Server neu starten:**
```bash
pkill -f ktamv_server.py
sleep 2
nohup ~/ktamv-env/bin/python ~/kTAMV/server/ktamv_server.py --port 8085 > ~/ktamv.log 2>&1 &
```

4. **Prüfen ob es läuft:**
```bash
curl http://localhost:8085/
```

Sollte zeigen: `Frame width: 1280, Frame height: 720`

## Kamera-Konfiguration

Die verbesserte Version verwendet **1280x720 (16:9)**. Stelle sicher, dass deine kTAMV-Kamera diese Auflösung unterstützt.

In `crowsnest.conf` für deine kTAMV-Kamera:
```ini
resolution: 1280x720
```

## Auto-Skalierung der Parameter

Die Detection-Parameter skalieren automatisch mit der Auflösung:

| Auflösung | minArea | maxArea | HoughCircles Radius |
|-----------|---------|---------|---------------------|
| 640x480 (original) | 400-600 | 900-15000 | 10-50px |
| 1280x720 (16:9) | 1600-2400 | 3600-60000 | 20-100px |
| 1920x1080 (Full HD) | 3600-5400 | 8100-135000 | 30-150px |

## Troubleshooting

### Kreise werden nicht erkannt

1. Prüfe die Beleuchtung - gleichmäßiges Licht ohne Reflektionen
2. Überprüfe den Fokus der Kamera
3. Schau im Log nach welcher Algorithmus verwendet wird:
   - `algo 1-3`: Standard Detector
   - `algo 4-7`: Relaxed Detector
   - `algo 8-9`: Super Relaxed Detector
   - `algo 100`: HoughCircles Fallback

### Bild ist verzerrt

Stelle sicher, dass Kamera-Auflösung und kTAMV-Auflösung das gleiche Seitenverhältnis haben (16:9).

### Server startet nicht

```bash
# Log prüfen
cat ~/ktamv.log

# Manuell starten zum Debuggen
~/ktamv-env/bin/python ~/kTAMV/server/ktamv_server.py --port 8085
```

## Zurück zur Original-Version

```bash
cp ~/kTAMV/server/ktamv_server_dm.py.backup ~/kTAMV/server/ktamv_server_dm.py
cp ~/kTAMV/server/ktamv_server_io.py.backup ~/kTAMV/server/ktamv_server_io.py
cp ~/kTAMV/server/ktamv_server.py.backup ~/kTAMV/server/ktamv_server.py
pkill -f ktamv_server.py && nohup ~/ktamv-env/bin/python ~/kTAMV/server/ktamv_server.py --port 8085 > ~/ktamv.log 2>&1 &
```

## Credits

- Original kTAMV von [TypQxQ](https://github.com/TypQxQ/kTAMV)
- Detection-Verbesserungen von PrintStructor
