// Loads the standalone page (no server, no claude.ai runtime) in jsdom and clicks through every tab.
// Run:  npm install  &&  node tests/smoke_jsdom.js
const { JSDOM } = require('jsdom'); const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '../web/crossbow-lab.html'), 'utf8');
const errors = [];
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://example.test/#results',
  beforeParse(w) {
    const ctx = new Proxy({}, { get(t, k) { if (k === 'measureText') return () => ({ width: 10 }); if (!(k in t)) t[k] = () => {}; return t[k]; }, set(t, k, v) { t[k] = v; return true; } });
    w.HTMLCanvasElement.prototype.getContext = () => ctx;
    Object.defineProperty(w.HTMLElement.prototype, 'clientWidth', { get() { return 390; } });
    w.scrollTo = () => {};
    w.addEventListener('error', e => errors.push('window error: ' + e.message));
    w.console.error = (...a) => errors.push('console.error: ' + a.join(' '));
  } });
const w = dom.window, d = w.document, wait = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await wait(100);
  const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  const text = s => (d.querySelector(s) || {}).textContent || '';
  let bad = 0; const check = (name, ok) => { console.log((ok ? 'ok   ' : 'FAIL ') + name); if (!ok) bad++; };
  check('three shots load without a server', d.querySelectorAll('.chip').length === 3);
  for (const t of ['results', 'math', 'simulate', 'data', 'replay']) { click(d.querySelector('#tabs button[data-t="' + t + '"]')); await wait(30); }
  click(d.querySelector('#tabs button[data-t="results"]')); await wait(30);
  check('results show a speed for shot 1', /10\.\d/.test(text('.big')));
  click(d.querySelector('.chip[data-id="s3"]')); await wait(30);
  check('selecting shot 3 works', /11\.\d/.test(text('.big')));
  click(d.querySelector('#tabs button[data-t="math"]')); await wait(30);
  check('math tab shows the steps', d.querySelectorAll('.step').length >= 10);
  click(d.querySelector('#tabs button[data-t="simulate"]')); await wait(30);
  click(d.querySelector('#sim-cal')); await wait(10);
  check('simulator landing calibration runs', !d.querySelector('#sim-cal-out').hidden);
  check('no script errors', errors.length === 0);
  if (errors.length) console.log(errors);
  console.log(bad ? bad + ' failed' : 'all passed'); process.exit(bad ? 1 : 0);
})();
