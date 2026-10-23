#!/usr/bin/env python3
"""
bolt_track.py - find a fast dark bolt in a video, track it, and report
speed, velocity, launch angle and trajectory.

Needs: ffmpeg/ffprobe on PATH, plus numpy, scipy, matplotlib (pip install them).

Example (36" yardstick spans x=694 to x=1630 px, recorded at 240 fps):
    python3 bolt_track.py IMG_4037_1.mov --ruler-px 694 1630 --ruler-mm 914.4 --fps 240

How it works
  1. Builds a background image (median of sampled frames).
  2. Streams every frame, looks for a long, thin, dark blob (the bolt).
  3. Keeps the longest consecutive run of detections (the shot).
  4. Converts pixels to metres with the ruler, frames to seconds with --fps.
  5. Fits x(t) linearly and y(t) as a parabola, then prints the results.
  6. Uses gravity (9.81 m/s^2) and your known frame rate to check the scale at the bolt's
     own distance from the camera, and reports both speeds plus a best estimate.

Note: iPhone slo-mo exports play back at 30 fps but were recorded at 240 fps.
--fps is the RECORDING rate (240), not the playback rate.
"""
import argparse
import csv
import subprocess
import sys

import numpy as np
from scipy import ndimage as ndi

G = 9.81


def probe(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,nb_frames",
        "-of", "csv=p=0", path]).decode().strip().split(",")
    w, h = int(out[0]), int(out[1])
    num, den = out[2].split("/")
    return w, h, float(num) / float(den)


def read_gray(path, crop, vf_extra="", n_frames=None):
    """Yield grayscale frames cropped to (x, y, w, h)."""
    x, y, w, h = crop
    # convert to gray FIRST: cropping yuv420p silently rounds sizes to even numbers
    vf = f"format=gray,crop={w}:{h}:{x}:{y}{vf_extra}"
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", vf,
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=w * h * 4)
    size = w * h
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w)
    p.stdout.close()
    p.wait()


def build_background(path, crop, samples=60):
    x, y, w, h = crop
    vf = f"select='not(mod(n\\,{samples}))'"
    frames = []
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf",
           f"{vf},format=gray,crop={w}:{h}:{x}:{y}", "-vsync", "0",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = w * h
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        frames.append(np.frombuffer(buf, np.uint8).reshape(h, w))
    p.wait()
    if len(frames) < 5:
        sys.exit("Could not sample enough frames for the background.")
    return np.median(np.stack(frames), axis=0).astype(np.int16)


def detect(frame, bg, thresh, min_px, aspect):
    """Find the bolt: a thin, dark, elongated blob, at ANY angle (judged by its shape, not its bounding box)."""
    d = bg - frame.astype(np.int16)           # positive where darker than bg
    m = d > thresh
    if m.sum() < min_px:
        return None
    lab, n = ndi.label(m)
    best = None
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        ys, xs = sl
        if max(xs.stop - xs.start, ys.stop - ys.start) < 30:
            continue
        yy, xx = np.nonzero(lab[sl] == k)
        area = len(xx)
        if area < min_px:
            continue
        pts = np.c_[xx - xx.mean(), yy - yy.mean()]
        w_, _ = np.linalg.eigh(np.cov(pts.T))
        major = 4 * np.sqrt(max(w_[1], 1e-9))
        minor = 4 * np.sqrt(max(w_[0], 1e-9))
        if major < 40 or major > 300 or minor > 26 or major / max(minor, 1.0) < 5:
            continue
        cand = dict(cx=xx.mean() + xs.start, cy=yy.mean() + ys.start,
                    x0=xs.start, x1=xs.stop, y0=ys.start, y1=ys.stop, w=major, area=area)
        if best is None or area > best["area"]:
            best = cand
    return best


def longest_run(dets, min_step, max_step):
    """dets: dict frame->detection. Return longest run with steady x steps."""
    best, cur = [], []
    for f in sorted(dets):
        d = dets[f]
        if cur and f == cur[-1][0] + 1 and \
                min_step <= abs(d["cx"] - cur[-1][1]["cx"]) <= max_step:
            cur.append((f, d))
        else:
            cur = [(f, d)]
        if len(cur) > len(best):
            best = list(cur)
    return best



def traj(v0, th, k, nmax, fps):
    """Flight with gravity and quadratic air drag (a = -k |v| v), RK4. Returns x, height in metres per frame."""
    sub = 8
    dt = 1.0 / fps / sub
    x = h = 0.0
    vx, vy = v0 * np.cos(th), v0 * np.sin(th)
    X, H = [0.0], [0.0]
    def acc(ux, uy):
        sp = np.hypot(ux, uy)
        return -k * sp * ux, -G - k * sp * uy
    for _ in range(nmax):
        for _ in range(sub):
            a1 = acc(vx, vy); v2 = (vx + a1[0] * dt / 2, vy + a1[1] * dt / 2)
            a2 = acc(*v2);    v3 = (vx + a2[0] * dt / 2, vy + a2[1] * dt / 2)
            a3 = acc(*v3);    v4 = (vx + a3[0] * dt, vy + a3[1] * dt)
            a4 = acc(*v4)
            x += dt / 6 * (vx + 2 * v2[0] + 2 * v3[0] + v4[0])
            h += dt / 6 * (vy + 2 * v2[1] + 2 * v3[1] + v4[1])
            vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0])
            vy += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1])
        X.append(x); H.append(h)
    return np.array(X), np.array(H)


def full_fit(n, x, y, fps, sr, in_plane):
    """Fit launch speed, angle, air drag k and a scale factor rho (true px/mm = rho * yardstick px/mm)
    to every tracked frame at once. The yardstick scale is trusted to about 12% (2% if in the bolt's path).
    Same method as the Crossbow Lab page."""
    from scipy.optimize import least_squares
    n = np.round(n - n[0]).astype(int)
    cx, cy = np.polyfit(n, x, 1), np.polyfit(n, y, 2)
    rxs = np.sqrt(((x - np.polyval(cx, n)) ** 2).sum() / max(1, len(n) - 2))
    rys = np.sqrt(((y - np.polyval(cy, n)) ** 2).sum() / max(1, len(n) - 3))
    sx, sy, sp = max(2.0, rxs), max(0.8, 3 * rys), (0.02 if in_plane else 0.12)
    dr = 1 if cx[0] >= 0 else -1

    def res(p):
        X_, H_ = traj(p[0], np.radians(p[1]), p[2], int(n.max()), fps)
        sc = p[3] * sr * 1000
        xm, ym = dr * sc * X_[n], -sc * H_[n]
        return np.r_[((xm - xm.mean()) - (x - x.mean())) / sx, ((ym - ym.mean()) - (y - y.mean())) / sy, (p[3] - 1) / sp]

    v0 = np.hypot(abs(cx[0]), -cy[1]) * fps / 1000 / sr
    th0 = np.degrees(np.arctan2(-cy[1], abs(cx[0])))
    # the bolt flies in front of the wall, so it can only look bigger than the yardstick (rho >= 1)
    rlo, rhi = (0.85, 1.15) if in_plane else (1.0, 1.5)
    r = least_squares(res, [v0, th0, 0.02, max(rlo, 1.0)], bounds=([0.5, -30, 0, rlo], [60, 85, 0.5, rhi]),
                      x_scale=[1, 1, 0.05, 0.1], xtol=1e-12, ftol=1e-12)
    dof = max(1, len(r.fun) - 2 - 4)
    chi2 = float((r.fun ** 2).sum() / dof)
    se = np.sqrt(np.abs(np.diag(np.linalg.pinv(r.jac.T @ r.jac))) * max(1.0, chi2))
    return dict(v0=r.x[0], th=r.x[1], k=r.x[2], rho=r.x[3], se_v0=se[0], se_th=se[1], se_k=se[2], se_rho=se[3], chi2=chi2)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--fps", type=float, default=240,
                    help="RECORDING frame rate (default 240)")
    ap.add_argument("--ruler-px", type=float, nargs=2, metavar=("X1", "X2"),
                    help="pixel x of the ruler's two ends")
    ap.add_argument("--ruler-mm", type=float, default=914.4,
                    help="real ruler length in mm (default 914.4 = 36 in)")
    ap.add_argument("--px-per-mm", type=float, help="give the scale directly")
    ap.add_argument("--region", type=int, nargs=4, metavar=("X", "Y", "W", "H"),
                    help="search region in pixels (default: right 70%% of frame, middle band)")
    ap.add_argument("--thresh", type=int, default=45, help="darkness threshold")
    ap.add_argument("--x-max", type=float,
                    help="ignore the bolt beyond this pixel x (default: yardstick end + 25 px)")
    ap.add_argument("--in-plane", action="store_true",
                    help="the ruler was in the bolt's own flight path (no parallax), so trust the ruler scale")
    ap.add_argument("--out", default="bolt_track", help="output file prefix")
    a = ap.parse_args()

    if a.px_per_mm:
        scale = a.px_per_mm
    elif a.ruler_px:
        scale = abs(a.ruler_px[1] - a.ruler_px[0]) / a.ruler_mm
    else:
        sys.exit("Give --ruler-px X1 X2 (and --ruler-mm) or --px-per-mm.")

    W, H, play_fps = probe(a.video)
    crop = tuple(a.region) if a.region else (int(W * 0.31), int(H * 0.23),
                                             int(W * 0.69), int(H * 0.51))
    crop = (crop[0], crop[1], min(crop[2], W - crop[0]), min(crop[3], H - crop[1]))
    print(f"video {W}x{H}, plays at {play_fps:g} fps; search region {crop}")
    print(f"scale {scale:.3f} px/mm; recording rate {a.fps:g} fps")

    print("building background...")
    bg = build_background(a.video, crop)

    print("scanning frames...")
    dets = {}
    for i, fr in enumerate(read_gray(a.video, crop)):
        d = detect(fr, bg, a.thresh, 40, 3.0)
        if d:
            dets[i] = d
    run = longest_run(dets, 10, 250)
    if len(run) < 8:
        sys.exit(f"No clear shot found (longest run {len(run)} frames). "
                 "Try --region, --thresh, or check the bolt is darker than the wall.")

    # Drop frames where the blob is clipped (touches region edge or is much
    # narrower than usual) and the first frame (launch blur).
    x_max = a.x_max if a.x_max else (max(a.ruler_px) + 25 if a.ruler_px else None)
    widths = np.array([d["w"] for _, d in run])
    wmed = np.median(widths)
    keep = []
    for k, (f, d) in enumerate(run):
        if k == 0:
            continue
        if d["x0"] <= 2 or d["x1"] >= crop[2] - 2 or d["y0"] <= 2 or d["y1"] >= crop[3] - 2 or d["w"] < 0.85 * wmed:
            continue
        if x_max is not None and d["cx"] + crop[0] > x_max:
            continue   # past the end of the yardstick: the background changes, so the blob edges are unreliable
        keep.append((f, d))
    if len(keep) < 6:
        sys.exit("Too few clean frames after trimming clipped ones.")

    f = np.array([k for k, _ in keep])
    n = f - f[0]
    x = np.array([d["cx"] for _, d in keep]) + crop[0]
    y = np.array([d["cy"] for _, d in keep]) + crop[1]

    # Reject outlier frames (blob clipped by a doorway, merged with something else, ...).
    # Fit, find points far from the fit, drop them, repeat.
    mask = np.ones(len(n), bool)
    for _ in range(4):
        px_ = np.polyfit(n[mask], x[mask], 1)
        py_ = np.polyfit(n[mask], y[mask], 2)
        rx, ry = x - np.polyval(px_, n), y - np.polyval(py_, n)
        sx = max(1.5, 1.4826 * np.median(np.abs(rx[mask] - np.median(rx[mask]))))
        sy = max(0.5, 1.4826 * np.median(np.abs(ry[mask] - np.median(ry[mask]))))
        new = (np.abs(rx) < 4 * sx) & (np.abs(ry) < 4 * sy)
        if (new == mask).all():
            break
        mask = new
    dropped = int((~mask).sum())
    if dropped:
        print(f"dropped {dropped} outlier frame(s)")
    used_frames = set(f[mask].tolist())
    f, n, x, y = f[mask], n[mask], x[mask], y[mask]
    if len(n) < 6:
        sys.exit("Too few clean frames after outlier rejection.")

    px = np.polyfit(n, x, 1)
    py = np.polyfit(n, y, 2)
    resid_x = float(np.sqrt(((x - np.polyval(px, n)) ** 2).sum() / max(1, len(n) - 2)))
    dt = 1.0 / a.fps

    vx = abs(px[0]) / scale / 1000 / dt            # m/s
    vy0 = -py[1] / scale / 1000 / dt               # m/s, up positive
    speed = float(np.hypot(vx, vy0))
    angle = float(np.degrees(np.arctan2(vy0, vx)))
    span = abs(x[-1] - x[0]) / scale
    T = n[-1] * dt

    # Scale check with gravity. Curvature of y(t) must equal g, so with a known
    # frame rate it gives the pixels-per-mm AT THE BOLT'S DISTANCE from the camera.
    a_px = 2 * py[0]
    resid = float(np.std(y - np.polyval(py, n)))
    t0 = (f[0]) / play_fps
    vpx, vypx = abs(px[0]), -py[1]
    k = a.fps / 1000.0
    speed_ruler = float(np.hypot(vpx, vypx)) * k / scale
    scale_g = a_px * a.fps ** 2 / (G * 1000) if a_px > 0 else float("nan")
    speed_grav = float(np.hypot(vpx, vypx)) * k / scale_g if scale_g == scale_g else float("nan")
    g_meas = a_px * a.fps ** 2 / (scale * 1000)
    fit = full_fit(n.astype(float), x, y, a.fps, scale, a.in_plane) if len(n) >= 8 else None
    stat_rel = (resid_x / np.sqrt(((n - n.mean()) ** 2).sum())) / vpx if vpx else 0.0
    if fit:
        sc_fit = fit["rho"] * scale
        best = float(np.hypot(vpx, vypx)) * k / sc_fit
        rl = 0.85 if a.in_plane else 1.0
        r_lo, r_hi = max(rl, fit["rho"] - fit["se_rho"]), fit["rho"] + fit["se_rho"]
        tt = float(np.hypot(stat_rel, 0.02))
        lo, hi = best * (fit["rho"] / r_hi) * (1 - tt), best * (fit["rho"] / r_lo) * (1 + tt)
    else:
        best = speed
        lo, hi = speed * 0.95, speed * 1.05

    print("\n=== RESULT ===")
    print(f"shot found at {t0:.2f} s (playback time), {len(keep)} clean frames")
    print(f"angle at start of track {angle:6.1f} deg   (does not depend on the scale)")
    print(f"tracked          {span:.0f} mm in {T*1000:.0f} ms (at the yardstick scale)")
    print(f"fit scatter (y)  {resid:.2f} px")
    print(f"\nspeed, yardstick scale      {speed_ruler:6.2f} m/s")
    if speed_grav == speed_grav:
        print(f"speed, gravity-calibrated   {speed_grav:6.2f} m/s   (shaky on a short track)")
    print(f"BEST ESTIMATE               {best:6.2f} m/s   (about {lo:.2f} to {hi:.2f})")
    if fit:
        print(f"full fit with air drag: speed {fit['v0']:.2f} +/- {fit['se_v0']:.2f} m/s, angle {fit['th']:.2f} deg, "
              f"drag k {fit['k']:.3f} +/- {fit['se_k']:.3f} per m, scale x{fit['rho']:.3f} of the yardstick's")
    print(f"gravity measured with the yardstick scale: {g_meas:.2f} m/s^2 (real: {G})")
    vx = vpx * k / scale
    vy0 = vypx * k / scale
    apex_n = -py[1] / (2 * py[0]) if py[0] > 0 else float("nan")
    rise = (np.polyval(py, 0) - np.polyval(py, apex_n)) / scale if apex_n == apex_n else float("nan")

    # JSON of raw pixel points (frame index counted from the first used frame), for the Crossbow Lab page
    import json
    f0 = min(used_frames)
    pts_json = [[int(fr - f0), round(float(d["cx"] + crop[0]), 1), round(float(d["cy"] + crop[1]), 1), 1 if fr in used_frames else 0] for fr, d in run]
    with open(f"{a.out}.pts.json", "w") as fh:
        json.dump({"fps": a.fps, "scale": round(scale, 4), "ruler": a.ruler_px, "pts": pts_json}, fh)
    print(f"points -> {a.out}.pts.json")

    # CSV of tracked points
    csv_path = f"{a.out}.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "t_ms", "x_mm", "height_mm"])
        for ni, xi, yi in zip(n, x, y):
            w.writerow([int(ni), round(ni * dt * 1000, 2),
                        round((xi - x[0]) / scale * np.sign(px[0]), 1),
                        round((np.polyval(py, 0) - yi) / scale, 1)])
    print(f"data -> {csv_path}")

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        X = (x - x[0]) / scale * np.sign(px[0])
        Hh = (np.polyval(py, 0) - y) / scale
        nf = np.linspace(0, n[-1], 100)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(X, Hh, "o", label="measured")
        ax.plot(np.polyval(px, nf) * 0 + (np.polyval(px, nf) - px[1]) / scale * np.sign(px[0]),
                (np.polyval(py, 0) - np.polyval(py, nf)) / scale, "-", label="parabola fit")
        ax.set_xlabel("distance (mm)")
        ax.set_ylabel("height above start (mm)")
        ax.set_title(f"{best:.1f} m/s at {angle:.1f} deg")
        ax.legend()
        ax.grid(alpha=.3)
        fig.tight_layout()
        fig.savefig(f"{a.out}.png", dpi=150)
        print(f"plot -> {a.out}.png")
    except ImportError:
        print("(matplotlib not installed, skipped plot)")


if __name__ == "__main__":
    main()
