# Audit log

## What was checked

- Every formula and number stated in the chat and in the lesson file was recomputed from scratch (about 20 items).
- The page's per-shot numbers were recomputed with a separate numpy implementation: agreement to 1e-12.
- The page's JavaScript fit and the tracker's SciPy fit agree to 1e-7 on all three shots (`tests/fit_reference.py`).
- Synthetic flights with known truth are recovered exactly (no noise) and within the stated range (with noise, drag and a bolt nearer the camera than the yardstick).
- Tracker on synthetic videos with a known speed: within 0.4% when the yardstick is in the bolt's plane; the true speed is inside the reported range when it is not.
- Detection threshold from 25 to 80: speed changes by less than 0.3%.
- No dropped or duplicated frames in the slow-motion exports.
- Full page click-through in jsdom (`tests/smoke_jsdom.js`) and, during development, in headless Chromium at phone and iPad sizes.

## Problems found and fixed

| Problem | Effect | Fix |
|---|---|---|
| Lesson answer said 27.8 km/h | Wrong rounding (should be 27.7) | Corrected |
| Early reading of the gravity mismatch as a frame-rate error | Wrong explanation; the cause is the scale (parallax) | Corrected once 240 fps was confirmed |
| Assumed the bolt was the 13-hole gray beam | Only the drawn length in the replay | Noted |
| Tracker cropped odd-sized regions misaligned (ffmpeg chroma rounding) | Garbage on odd region sizes | Convert to gray before cropping |
| A clipped frame at the doorway was included | Biased fits | Outlier rejection and a stop at the yardstick's end |
| Optimiser stuck when a parameter sat on its bound | Shot 2 fit about 2% off | Active-set handling |
| Fit let the scale shrink (bolt behind the wall) | Shot 2 speed 11.1 instead of 10.8 | Scale bounded to >= 1 |
| Midpoint of two scales used as the headline | Arbitrary | Replaced by the full-flight fit |
| Detector only found flat bolts (bounding-box aspect) | Missed the 30 degree shot | Shape-based (PCA) detection |
| Simulator chart stretched the height and was not labelled | A 16 degree launch looked like 41 degrees on an iPad | True scale by default; stretch is labelled; angle printed on the Results chart |
| Single-number landing prediction (7.39 m) with drag taken as 0 from one short track | Real landing 5.194 m | Prediction now flagged as a best case; drag can be calibrated from a real landing |

## What cannot be verified

- The scale at the bolt's own distance (parallax): about 0 to 12%. This dominates the uncertainty.
- The 240 fps figure (taken from the camera setting).
- Rolling-shutter timing (estimated under 1%, not measured).
- The yardstick's tick marks are too blurred in the compressed video to check the scale independently, so it rests on the end positions (about 1%).
