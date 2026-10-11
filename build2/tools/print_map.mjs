// Prints dist/Remnian_Lineage_Map.html to dist/Remnian_Lineage_Map.pdf (charts on 11x17 landscape, the rest on letter).
// Usage: node tools/print_map.mjs [screenshot-dir]
import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = path.join(ROOT, 'dist', 'Remnian_Lineage_Map.html');
const pdf = path.join(ROOT, 'dist', 'Remnian_Lineage_Map.pdf');
const shots = process.argv[2];

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.goto('file://' + html, { waitUntil: 'networkidle' });
await page.evaluate(async () => {
  await Promise.all(['600 16px "Barlow Condensed"', '400 16px "Atkinson Hyperlegible"', '700 16px "Atkinson Hyperlegible"',
    '400 12px "JetBrains Mono"', '600 12px "JetBrains Mono"'].map(f => document.fonts.load(f)));
  await document.fonts.ready;
});
const fonts = await page.evaluate(() => ['Atkinson Hyperlegible', 'Barlow Condensed', 'JetBrains Mono'].map(f => [f, document.fonts.check(`16px "${f}"`)]));
// text that runs past its box in the charts
const overflow = await page.evaluate(() => {
  const bad = [];
  for (const g of document.querySelectorAll('svg.chart g.box')) {
    const r = g.querySelector('rect.card').getBBox();
    for (const t of g.querySelectorAll('text')) {
      const b = t.getBBox();
      if (b.x + b.width > r.x + r.width - 4) bad.push(`${t.textContent} (${Math.round(b.x + b.width - r.x - r.width + 4)}px)`);
    }
  }
  return bad;
});
if (shots) {
  for (const id of ['imperial', 'london']) await page.locator('#' + id + ' svg').screenshot({ path: path.join(shots, id + '.png') });
  await page.screenshot({ path: path.join(shots, 'top.png') });
  await page.setViewportSize({ width: 400, height: 900 });
  await page.screenshot({ path: path.join(shots, 'phone.png') });
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.locator('#imperial svg').screenshot({ path: path.join(shots, 'imperial-dark.png') });
  await page.emulateMedia({ colorScheme: 'light' });
}
await page.emulateMedia({ media: 'print' });
await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
await browser.close();
console.log(JSON.stringify({ fonts, overflow }));
