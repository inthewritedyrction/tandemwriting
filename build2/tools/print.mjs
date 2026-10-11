// Renders out/book.html in Chromium, runs the paginator + layout QA, and prints the PDF.
// Usage: node tools/print.mjs
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// optional: node tools/print.mjs <out/page.html> <dist/file.pdf> <out/layout_name.json>
const html = path.join(ROOT, process.argv[2] || path.join('out', 'book.html'));
const pdf = path.join(ROOT, process.argv[3] || path.join('dist', 'Tandem_Companion_Build2_FTE.pdf'));
const qaOut = process.argv[4] || 'layout_qa.json';
fs.mkdirSync(path.join(ROOT, 'dist'), { recursive: true });

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1000, height: 1200 } });
page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
page.on('pageerror', e => { console.error('pageerror:', e.message); process.exitCode = 1; });
await page.goto('file://' + html);
await page.evaluate(async () => {
  const fams = ['400 16px "Atkinson Hyperlegible"', '700 16px "Atkinson Hyperlegible"', 'italic 400 16px "Atkinson Hyperlegible"', 'italic 700 16px "Atkinson Hyperlegible"',
    '500 16px "Barlow Condensed"', '600 16px "Barlow Condensed"', '700 16px "Barlow Condensed"', '400 12px "JetBrains Mono"', '600 12px "JetBrains Mono"'];
  await Promise.all(fams.map(f => document.fonts.load(f, 'AaBb→†–’')));
  await document.fonts.ready;
});
const fontsOk = await page.evaluate(() => ['Atkinson Hyperlegible', 'Barlow Condensed', 'JetBrains Mono'].map(f => [f, document.fonts.check(`16px "${f}"`)]));
const qa = await page.evaluate(() => window.paginate());
qa.fonts = fontsOk;
qa.bookText = await page.evaluate(() => [...document.querySelectorAll('#book .pg')].map(p => p.innerText));
fs.writeFileSync(path.join(ROOT, 'out', qaOut), JSON.stringify(qa, null, 1));
if (!process.argv[2]) fs.writeFileSync(path.join(ROOT, 'out', 'book.paginated.html'), await page.content());
await page.emulateMedia({ media: 'print' });
await page.pdf({ path: pdf, width: '8.5in', height: '11in', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, preferCSSPageSize: true });
await browser.close();
console.log(`pages: ${qa.pages}  issues: ${qa.issues.length}  flags: ${qa.flags.length}  fonts: ${JSON.stringify(fontsOk)}`);
const byType = {};
qa.issues.forEach(i => { byType[i.type] = (byType[i.type] || 0) + 1; });
console.log('issue types:', JSON.stringify(byType));
console.log('flags:', JSON.stringify(qa.flags.slice(0, 20)));
