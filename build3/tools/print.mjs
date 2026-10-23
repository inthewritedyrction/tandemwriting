// Print out/volume_one.html to dist/ with Chromium, and record the page each
// contents entry lands on (out/toc_pages.json) for the second pass.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { try { playwright = require('/opt/node-tools/node_modules/playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); } }
const { chromium } = playwright;
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const htmlPath = path.join(root, 'out', 'volume_one.html');
const pdfPath = process.argv[2] || path.join(root, 'dist', 'TKC_Volume_One_World_Dossier.pdf');
fs.mkdirSync(path.dirname(pdfPath), { recursive: true });

const PINK = '#E5173F';
const header = `<div style="width:100%;margin:0 0.8in;font-family:Helvetica,Arial,sans-serif;font-size:7.2px;letter-spacing:0.3em;text-align:center;color:#1d1d1f;padding-bottom:4px;border-bottom:2.4px double #1d1d1f;">TKC VOLUME ONE · THE WORLD DOSSIER</div>`;
const footer = `<div style="width:100%;text-align:center;font-family:Georgia,serif;font-size:9.5px;color:#1d1d1f;"><span style="display:inline-block;width:34px;border-top:1px solid ${PINK};vertical-align:middle;margin-right:9px"></span><span class="pageNumber"></span><span style="display:inline-block;width:34px;border-top:1px solid ${PINK};vertical-align:middle;margin-left:9px"></span></div>`;

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.pdf({
  path: pdfPath, format: 'Letter', printBackground: true, displayHeaderFooter: true,
  headerTemplate: header, footerTemplate: footer, preferCSSPageSize: true,
});
await browser.close();
console.log('pdf written', pdfPath);
