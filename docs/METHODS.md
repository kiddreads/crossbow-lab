# Methods

All formulas used by the page and the tracker.

## From video to numbers

1. **Frame rate.** The clips are iPhone slow motion recorded at 240 fps and exported at 30 fps, so playback is 8 times slower. Time between frames is `dt = 1 / 240 s = 4.167 ms`.
2. **Tracking.** The bolt is the thin dark blob that differs from a median background. Its centre (centroid) is recorded each frame, as pixel (x, y). Blobs touching the frame edge, narrower than usual, or past the end of the yardstick are dropped, and outliers are rejected by iterative sigma clipping.
3. **Scale.** `scale = yardstick pixels / 914.4 mm` (36 in).
4. **Fits (in pixels, n = frame number):**
   - `x = a0 + a1 n` (straight line)
   - `y = c0 + c1 n + c2 n^2` (parabola, y points down)
5. **Speeds.**
   - Horizontal: `vx = |a1| / scale x fps / 1000` m/s
   - Vertical at the start of the track: `vy = -c1 / scale x fps / 1000` m/s
   - Speed: `v = sqrt(vx^2 + vy^2)`; angle: `atan2(vy, vx)` (independent of the scale).
6. **Peak.** `n* = -c1 / (2 c2)`, height gained `= (y(0) - y(n*)) / scale`. If `n*` lies beyond the tracked frames it is a prediction.

## Checking the scale with gravity

Gravity bends the path by `a = 2 c2` pixels per frame squared, so
`g_measured = a x fps^2 / (scale x 1000)` m/s^2. Setting this equal to 9.81 gives a scale at the bolt's own distance from the camera: `scale_g = 2 c2 fps^2 / (9810)`.
This is sensitive on short tracks (it moved by about 15% with sub-pixel changes in the last frames of shot 2), so it is shown as a cross-check, not the headline.

## The best fit (headline number)

Fit one complete flight to every tracked frame at once:

- Equations: gravity plus quadratic drag, `a = -k |v| v` (k in 1/m, so speed falls by about `k x 100` percent per metre). Integrated with RK4.
- Parameters: launch speed, launch angle, drag k, and scale factor `rho` (true px/mm = `rho` x yardstick px/mm).
- `rho` is bounded to `>= 1` (the bolt is in front of the wall, so it can only look bigger) with a Gaussian prior of width 0.12 around 1. For a shot where the yardstick was in the bolt's plane the bounds are 0.85 to 1.15 with width 0.02.
- Position offsets are removed analytically; noise levels are 2 px (x) and at least 0.8 px (y).
- Solved with Levenberg-Marquardt (page) or SciPy `least_squares` (tracker); the two agree to better than 1e-6 on all shots.
- Uncertainty comes from the Jacobian, scaled by chi-squared if it exceeds 1. The headline is the quadratic-fit speed at the fitted scale.

## Simulator

Gravity plus the same quadratic drag, RK4 with a 0.5 ms step, flight ends at the floor. "Match the drag to a real landing" solves for the k that gives a measured landing distance (bisection), minus the gap between the crossbow and where tracking starts.

## Table-drop check (no camera)

Fall time `t = sqrt(2h / g)`, speed `v = d / t` for a level shot off a table of height h that lands at distance d.
