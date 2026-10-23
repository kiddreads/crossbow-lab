# Crossbow Lab

Measure the speed, angle and path of a Lego Technic crossbow bolt from slow-motion video, then explore the maths in an interactive page.

Everything here was built from three 240 fps iPhone clips of a bolt flying past a 36 inch yardstick taped to a wall.

## What is in this repo

| Folder | What it holds |
|---|---|
| `web/crossbow-lab.html` | The interactive lab. Open it in any browser. All three shots are built in, no server needed. |
| `web/crossbow-lab.claude-artifact.html` | The same page as published on claude.ai, where shots are stored in a shared database. |
| `tracker/bolt_track.py` | Command-line tracker: finds the bolt in a video, tracks it, and reports speed, angle and drag. |
| `tracker/synth_video.py` | Makes test videos with a known true speed, to check the tracker. |
| `data/shots/` | The tracked points for each shot (pixel positions per frame, yardstick position, frame rate). |
| `data/tracker-output/` | The tracker's plots and CSVs for each shot. |
| `lesson/` | A printable maths lesson built from the experiment. |
| `tests/` | Unit tests, a cross-check between the two fit implementations, and a page smoke test. |
| `docs/` | `METHODS.md` (every formula) and `AUDIT.md` (what was checked and what was found wrong). |

## Results so far

| | Speed | Angle at start of track | Air drag k (per metre) | Real landing |
|---|---|---|---|---|
| Shot 1 | 10.2 m/s (9.5 to 11.0) | 4.4° | 0.061 ± 0.020 | not measured |
| Shot 2 | 10.8 m/s (9.9 to 11.1) | 16.3° | about 0 from the video | 5.194 m |
| Shot 3 | 11.0 m/s (9.6 to 11.2) | 30.0° | about 0 from the video | not measured yet |

The range in brackets is the honest uncertainty. See "Limits" below.

## Quick start

Open `web/crossbow-lab.html` in a browser. Tabs: Replay, Results, Math, Simulate, Data.

### Track a new clip

```
pip install -r requirements.txt        # also needs ffmpeg on your PATH
python3 tracker/bolt_track.py clip.mov --ruler-px 694 1630 --ruler-mm 914.4 --fps 240
```

- `--ruler-px X1 X2` is the pixel x of the yardstick's two ends in the video frame.
- `--fps` is the **recording** rate (240 for iPhone slo-mo), not the playback rate (30).
- Add `--in-plane` only if the yardstick was held in the bolt's own flight path.
- If the bolt leaves the default search area, pass `--region X Y W H`.

It prints the speed three ways (yardstick scale, gravity-calibrated, best fit with air drag) and writes a plot, a CSV and a `.pts.json` file you can load into the page.

### Run the tests

```
npm install
npm test
```

## Limits (read these)

- **Scale:** the bolt flies in front of the wall, so it looks bigger than the yardstick. The yardstick scale therefore reads the speed too high by an unknown 0 to about 12%. The best fit allows for this but can't remove it. Holding the yardstick in the bolt's path cuts the uncertainty to about 2%.
- **Short tracks:** the camera sees only the first metre or so (about 60 to 80 ms). Air drag measured there does not predict a 5 to 8 m flight. Calibrate drag from a real landing (Simulate tab, "Match the drag to a real landing").
- **Frame rate** is taken as 240 fps from the camera setting.
- **Angles on charts:** the Results and Simulate charts can stretch the height. Read angles from the printed numbers, not from a protractor on the screen.
- Raw videos are not in the repo (too large). `.gitignore` excludes them.

## Uploading to GitHub

```
cd crossbow-lab
git init && git add . && git commit -m "Crossbow Lab"
git branch -M main
git remote add origin https://github.com/<you>/crossbow-lab.git
git push -u origin main
```

To host the page, turn on GitHub Pages for the `web/` folder. No licence file is included: add the one you want.
