// Print out/workbook.html: fill writing areas with ruled lines, report any page
// whose content overflows, then write the PDF.
// Usage: node workbook/wb_print.mjs [out.pdf]
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { try { playwright = require('/opt/node-tools/node_modules/playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); } }
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pdfPath = process.argv[2] || path.join(root, 'dist', 'TKC_Volume_One_Workbook.pdf');
fs.mkdirSync(path.dirname(pdfPath), { recursive: true });

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 816, height: 1056 } });
await page.goto('file://' + path.join(root, 'out', 'workbook.html'), { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.emulateMedia({ media: 'print' });

const report = await page.evaluate(() => {
  const lineH = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--line')) * 96 || 34;
  // a fill area takes whatever space is left, so it is measured after layout
  for (const box of document.querySelectorAll('.fill .lines')) {
    const h = box.getBoundingClientRect().height;
    const li = box.closest('.side') ? 0.33 * 96 : lineH;
    const n = Math.max(1, Math.floor(h / li));
    box.innerHTML = '<i></i>'.repeat(n);
  }
  const over = [];
  const short = [];
  document.querySelectorAll('.page').forEach((pg, idx) => {
    const fl = pg.querySelectorAll('.main .fill .lines');
    if (fl.length !== 1) return;
    const main = pg.querySelector('.main');
    const overflowing = main.scrollHeight > main.clientHeight + 2;
    fl.forEach(box => {
      if (overflowing || (box.children.length < 6 && !box.parentElement.classList.contains('rest'))) {
        const k = box.parentElement.querySelector('.k');
        short.push({ page: idx + 1, prompt: k ? k.textContent : '', mode: (overflowing || box.children.length < 3) ? 'move' : 'add' });
      }
    });
  });
  document.querySelectorAll('.page').forEach((pg, idx) => {
    for (const col of pg.querySelectorAll('.main, .side, .margin')) {
      if (col.scrollHeight > col.clientHeight + 8) {
        over.push(`${idx + 1}: ${col.className} over by ${col.scrollHeight - col.clientHeight}px · ${(pg.querySelector('.rh') || {}).textContent || pg.className}`);
      }
    }
    const fills = pg.querySelectorAll('.fill');
    fills.forEach(f => { if (f.getBoundingClientRect().height < 30) over.push(`${idx + 1}: writing space squeezed to ${Math.round(f.getBoundingClientRect().height)}px`); });
  });
  return { pages: document.querySelectorAll('.page').length, over, short };
});
fs.writeFileSync(path.join(root, 'out', 'overflow.json'), JSON.stringify(report, null, 1));
console.log(`${report.short.length} short writing areas`);
await page.pdf({ path: pdfPath, width: '8.5in', height: '11in', printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log(`${report.pages} pages · ${report.over.length} layout problems`);
for (const o of report.over) console.log('  ' + o);
// record which prompts need a working page, for the next wb.py run
{
  const html = fs.readFileSync(path.join(root, 'out', 'workbook.html'), 'utf8');
  const conts = report.short.map(s => {
    const re = new RegExp('<section class="page[^"]*">', 'g');
    let m, n = 0, start = -1;
    while ((m = re.exec(html))) { n++; if (n === s.page) { start = m.index; break; } }
    const seg = start >= 0 ? html.slice(start, html.indexOf('</section>', start)) : '';
    const rh = (seg.match(/<div class="rh">(.*?)<\/div>/) || [, ''])[1].replace(/<[^>]+>/g, '');
    return { rh: rh.replace(/&amp;/g, '&'), prompt: s.prompt.replace(/\s+/g, ' ').trim().toUpperCase(), mode: s.mode };
  });
  const prev = fs.existsSync(path.join(root, 'out', 'continuations.json')) ? JSON.parse(fs.readFileSync(path.join(root, 'out', 'continuations.json'), 'utf8')) : [];
  const key = c => c.rh + '|' + c.prompt;
  const all = [...prev, ...conts.filter(c => !c.rh.endsWith('WORKING SPACE'))];
  const m = new Map();
  for (const c of all) { const old = m.get(key(c)); m.set(key(c), old && old.mode === 'move' ? old : c); }
  const uniq = [...m.values()];
  fs.writeFileSync(path.join(root, 'out', 'continuations.json'), JSON.stringify(uniq, null, 1));
}
