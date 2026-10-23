"""Cross-check: the web page's JavaScript fit versus the tracker's SciPy fit, on every stored shot.
Run:  python3 tests/fit_reference.py     (needs numpy, scipy, node)"""
import json, os, subprocess, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..', 'tracker'))
import bolt_track as bt
js = json.loads(subprocess.check_output(['node', os.path.join(here, 'print_fit.js')]))
shots = json.load(open(os.path.join(here, '..', 'data', 'shots.json')))
worst = 0.0
for i, (s, j) in enumerate(zip(shots, js), 1):
    P = np.array(s['pts']); U = P[P[:, 3] == 1]
    r = bt.full_fit(U[:, 0].astype(float), U[:, 1], U[:, 2], s['fps'], s['scale'], bool(s.get('inPlane')))
    diffs = [abs(r['v0'] - j['v0']), abs(r['th'] - j['th']), abs(r['k'] - j['k']), abs(r['rho'] - j['rho'])]
    worst = max(worst, max(diffs))
    print(f"shot {i}: python v0={r['v0']:.4f} th={r['th']:.3f} k={r['k']:.4f} rho={r['rho']:.4f} | js v0={j['v0']:.4f} th={j['th']:.3f} k={j['k']:.4f} rho={j['rho']:.4f}")
print('largest difference between the two implementations:', f'{worst:.1e}')
sys.exit(0 if worst < 2e-3 else 1)
