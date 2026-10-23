// Prints the page's full-flight fit for every stored shot as JSON (used by fit_reference.py).
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '../web/crossbow-lab.html'), 'utf8');
const src = html.slice(html.indexOf('//#MATH-START'), html.indexOf('//#MATH-END'));
const { analyze } = new Function(src + ';return {analyze};')();
const shots = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/shots.json'), 'utf8'));
console.log(JSON.stringify(shots.map(s => { const F = analyze(s, { mode: 'fit' }).fit; return F ? { v0: F.v0, th: F.th, k: F.k, rho: F.rho } : null; })));
