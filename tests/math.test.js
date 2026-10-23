// Unit tests for the page's math. Run:  node tests/math.test.js
// The math lives between //#MATH-START and //#MATH-END in web/crossbow-lab.html and has no DOM dependencies.
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '../web/crossbow-lab.html'), 'utf8');
const src = html.slice(html.indexOf('//#MATH-START'), html.indexOf('//#MATH-END'));
const { analyze, simulate, polyfit, parseTrackCsv, f } = new Function(src + ';return {analyze,simulate,polyfit,parseTrackCsv,f};')();
const shots = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/shots.json'), 'utf8'));
let fails = 0, passes = 0;
function close(name, got, want, tol) {
  const ok = Math.abs(got - want) <= tol;
  ok ? passes++ : fails++;
  console.log((ok ? 'ok   ' : 'FAIL ') + name + ': got ' + (+got).toPrecision(6) + ', want ' + (+want).toPrecision(6) + ' (tol ' + tol + ')');
}

// 1. Synthetic flights with known truth (no noise): every output must match to rounding error.
function synth(v, thDeg, fps, sTrue, sRuler) {
  const th = thDeg * Math.PI / 180, vx = v * Math.cos(th), vy = v * Math.sin(th), pts = [];
  for (let n = 0; n < 20; n++) { const t = n / fps; pts.push([n, 500 + vx * 1000 * t * sTrue, 600 - (vy * 1000 * t - 0.5 * 9.81 * 1000 * t * t) * sTrue, 1]); }
  return { fps, scale: sRuler, pts };
}
let S1 = synth(10, 5, 240, 1.2, 1.0);
close('gravity-calibrated speed recovers truth', analyze(S1, { mode: 'gravity' }).speed, 10, 1e-9);
close('angle recovers truth', analyze(S1, { mode: 'gravity' }).angle, 5, 1e-9);
close('gravity scale recovers true px/mm', analyze(S1, { mode: 'gravity' }).sg, 1.2, 1e-9);
close('yardstick scale reads high by exactly sTrue/sRuler', analyze(S1, { mode: 'ruler' }).speed, 12, 1e-9);
close('custom exact scale recovers truth', analyze(S1, { mode: 'custom', scale: 1.2 }).speed, 10, 1e-9);
close('apex height = vy^2 / 2g (mm)', analyze(S1, { mode: 'custom', scale: 1.2 }).rise, (10 * Math.sin(5 * Math.PI / 180)) ** 2 / (2 * 9.81) * 1000, 1e-6);
let S3 = synth(10, 5, 240, 1.0, 1.0); S3.inPlane = true;
close('in-plane shot: fit mode recovers truth', analyze(S3, { mode: 'fit' }).speed, 10, 0.02);
close('measured g = 9.81 when the scale is right', analyze(S3, { mode: 'ruler' }).gmeas, 9.81, 1e-9);

// 2. polyfit against an exact quadratic
const xs = [0, 1, 2, 3, 4], c = polyfit(xs, xs.map(x => 1 + 2 * x + 0.5 * x * x), 2);
close('polyfit c0', c[0], 1, 1e-9); close('polyfit c1', c[1], 2, 1e-9); close('polyfit c2', c[2], 0.5, 1e-9);

// 3. simulator against closed-form projectile motion (no drag)
for (const [v, ang, h, g] of [[11.3, 4.4, 0.2, 9.81], [8, 30, 0, 9.81], [20, 60, 1, 1.62], [5, -5, 1.5, 3.71]]) {
  const th = ang * Math.PI / 180, vx = v * Math.cos(th), vy = v * Math.sin(th), T = (vy + Math.sqrt(vy * vy + 2 * g * h)) / g;
  const s = simulate({ v, ang, h, k: 0, g });
  close('sim range ' + [v, ang, h, g], s.range, vx * T, 2e-4);
  close('sim time', s.T, T, 2e-4);
}
close('drag terminal speed = sqrt(g/k)', simulate({ v: 0.0001, ang: -90, h: 200, k: 0.05, g: 9.81, dt: 0.001 }).impact, Math.sqrt(9.81 / 0.05), 0.2);
let best = 0, br = 0; for (let a = 0; a <= 90; a++) { const r = simulate({ v: 10, ang: a, h: 0, k: 0, g: 9.81, dt: 0.002 }).range; if (r > br) { br = r; best = a; } }
close('best range angle from the ground is 45 deg', best, 45, 0);
close('best range = v^2/g', br, 100 / 9.81, 0.01);

// 4. CSV import
const csv = parseTrackCsv('frame,t_ms,x_mm,height_mm\n0,0,0,0\n1,4.17,47,3.6\n2,8.3,94,6.8\n3,12.5,141,9.5\n4,16.7,188,13\n5,20.8,235,15');
close('CSV import keeps 6 rows', csv.pts.length, 6, 0);

// 5. Real shots (regression values, published results)
const [a1, a2, a3] = shots;
close('shot 1 speed, yardstick scale', analyze(a1, { mode: 'ruler' }).speed, 11.312, 0.005);
close('shot 1 angle', analyze(a1, { mode: 'ruler' }).angle, 4.434, 0.005);
close('shot 1 headline (full fit)', analyze(a1, { mode: 'fit' }).speed, 10.182, 0.05);
close('shot 1 fitted drag k', analyze(a1, { mode: 'fit' }).fit.k, 0.061, 0.005);
close('shot 2 speed, yardstick scale', analyze(a2, { mode: 'ruler' }).speed, 10.832, 0.005);
close('shot 2 angle', analyze(a2, { mode: 'ruler' }).angle, 16.281, 0.005);
close('shot 2 headline (full fit)', analyze(a2, { mode: 'fit' }).speed, 10.832, 0.05);
close('shot 3 speed, yardstick scale', analyze(a3, { mode: 'ruler' }).speed, 10.96, 0.01);
close('shot 3 angle', analyze(a3, { mode: 'ruler' }).angle, 29.96, 0.01);
// Shot 2: matching the real 5.194 m landing needs k about 0.093 (see docs/AUDIT.md)
let lo = 0, hi = 0.6; for (let i = 0; i < 50; i++) { const m = (lo + hi) / 2; (simulate({ v: 10.8, ang: 16.3, h: 0.2, k: m, g: 9.81, dt: 0.001 }).range > 5.194 - 0.07) ? lo = m : hi = m; }
close('shot 2 landing implies drag k', (lo + hi) / 2, 0.093, 0.01);

console.log('\n' + passes + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
