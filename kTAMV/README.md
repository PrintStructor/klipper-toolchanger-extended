# kTAMV Detection Improvements

Enhanced nozzle detection for [kTAMV](https://github.com/TypQxQ/kTAMV) with better reliability across varying lighting conditions.

## Improvements

| Feature | Description |
|---------|-------------|
| **CLAHE Preprocessing** | Contrast Limited Adaptive Histogram Equalization for better detection in varying lighting |
| **HoughCircles Fallback** | When blob detection fails, HoughCircles is used as backup |
| **Multi-Blob Handling** | When multiple blobs are detected, the most centered one is selected instead of failing |
| **Morphological Cleanup** | Opening/closing operations to remove noise and reflections |
| **Dynamic Resolution** | Works with any camera resolution (not hardcoded to 640x480) |

## Detection Cascade

The improved detection tries 9 algorithm combinations plus HoughCircles fallback:

1. `standard + YUV` (original)
2. `standard + triangle` (original)
3. `standard + CLAHE` (new)
4. `relaxed + YUV` (original)
5. `relaxed + triangle` (original)
6. `relaxed + CLAHE` (new)
7. `relaxed + CLAHE + morphology` (new)
8. `superRelaxed + median` (original)
9. `superRelaxed + CLAHE + morphology` (new)
10. `HoughCircles` (new, fallback)

## Installation

### Automatic (via install.sh)

The improved detection is installed automatically when you run:

```bash
cd ~/klipper-toolchanger-extended
./install.sh
```

### Manual

Copy the improved detection manager to your kTAMV installation:

```bash
cp ~/klipper-toolchanger-extended/kTAMV/server/ktamv_server_dm.py ~/kTAMV/server/
```

Then restart the kTAMV server:

```bash
pkill -f ktamv_server.py
nohup ~/ktamv-env/bin/python ~/kTAMV/server/ktamv_server.py --port 8085 > ~/ktamv.log 2>&1 &
```

## Tuning HoughCircles Parameters

If detection still has issues, you can tune the HoughCircles parameters in `ktamv_server_dm.py`:

```python
self.hough_dp = 1.2          # Resolution ratio (1.0 = same as input)
self.hough_minDist = 50      # Minimum distance between detected circles
self.hough_param1 = 50       # Canny edge detection threshold
self.hough_param2 = 30       # Accumulator threshold (lower = more circles)
self.hough_minRadius = 10    # Minimum nozzle radius in pixels
self.hough_maxRadius = 50    # Maximum nozzle radius in pixels
```

## Debug Information

The algorithm used is logged in the kTAMV server output:
- `algo 1-3`: Standard detector
- `algo 4-7`: Relaxed detector
- `algo 8-9`: Super relaxed detector
- `algo 100`: HoughCircles fallback

## Credits

- Original kTAMV by [TypQxQ](https://github.com/TypQxQ/kTAMV)
- Detection improvements by PrintStructor
