/* The Tandem Companion — Build 1 paginator.
   Flows the source blocks into fixed Letter pages. Rules (docs/production-rules.md):
   - nothing enters the footer safe zone (y > 960);
   - blocks never shrink: a block that doesn't fit moves to the next page;
   - tables split between rows and repeat their header row;
   - captions and subheads stay with what follows them;
   - leftover space on a page goes to that page's writing areas, in whole lines;
   - Part III sections that end with room to spare get a ruled NOTES area. */
(function () {
  'use strict';
  const D = window.BOOK;
  const LIMIT = 960, PAGE_W = 816, COL_L = 72, COL_R = 744, LINE = 30;
  const book = document.getElementById('book');
  const src = document.getElementById('src');
  const pages = [];
  let cur = null;
  const flags = [];

  const STN = ['SPINE', '3SL', 'FTE', 'ADST', 'TSWK', 'CONTINUITY'];
  const STC = ['#2B2B2B', '#74399A', '#B8332A', '#2C63C4', '#0E7F74', '#C46F0D'];

  function route(st) {
    return '<div class="route">' + STN.map((n, k) => k === st
      ? `<div class="stn on"><i style="background:${STC[k]};border-color:${STC[k]}"></i>${n}</div>`
      : `<div class="stn"><i></i>${n}</div>`).join('') + '</div>';
  }

  function makePage(sec, opener) {
    const m = D.secmeta[sec];
    const pg = document.createElement('div');
    pg.className = 'pg' + (m.work ? ' work' : '');
    pg.dataset.sec = sec;
    const bare = sec === 'TITLE';
    pg.innerHTML = (bare ? '' : route(m.station) + `<div class="btab" style="left:${COL_L + m.station * 112}px;background:${m.color}"></div>`) +
      `<div class="body"></div>` + (bare ? '' : `<div class="ft"><span class="fl1"></span>${m.work ? '<span class="fms">MS CHECK · CH.<u></u>DATE<u></u></span>' : ''}<span class="fr"></span></div>`);
    book.appendChild(pg);
    const body = pg.querySelector('.body');
    if (!opener && m.running) {
      const rh = document.createElement('div');
      rh.className = 'rh';
      rh.innerHTML = `<span>${m.running}</span><span>CONTINUED</span>`;
      body.appendChild(rh);
    }
    cur = { el: pg, body, sec, opener, crumb: m.crumb };
    pages.push(cur);
    return cur;
  }

  function top(el) { return el.getBoundingClientRect().top - cur.el.getBoundingClientRect().top; }
  function bottom(el, page) { const p = page || cur; return el.getBoundingClientRect().bottom - p.el.getBoundingClientRect().top; }
  function fits(el) { return bottom(el) <= LIMIT + 0.5; }
  function content(body) { return [...body.children].filter(e => !e.classList.contains('rh')); }
  function lastBottom(page) {
    const c = content(page.body);
    if (!c.length) return 0;
    let b = 0;
    for (const e of c) b = Math.max(b, bottom(e, page));
    return b;
  }

  // ---- fill: leftover space on a page becomes writing space, in whole lines
  function fill(page, sectionEnd) {
    const m = D.secmeta[page.sec];
    let left = LIMIT - lastBottom(page) - 2;
    const flex = [...page.body.querySelectorAll('[data-flex]')];
    if (flex.length && left >= LINE) {
      let lines = Math.floor(left / LINE);
      const w = flex.map(e => +e.dataset.flex || 1), tw = w.reduce((a, b) => a + b, 0);
      const add = w.map(x => Math.floor(lines * x / tw));
      let rem = lines - add.reduce((a, b) => a + b, 0);
      for (let k = 0; rem > 0; k = (k + 1) % add.length, rem--) add[k]++;
      flex.forEach((e, k) => { const rl = e.querySelector(':scope > .rl'); if (rl) rl.style.height = (rl.offsetHeight + add[k] * LINE) + 'px'; });
      // guard against rounding: trim whole lines until the page clears the safe zone
      let guard = 0;
      while (lastBottom(page) > LIMIT + 0.5 && guard++ < 50) {
        const rl = flex.map(e => e.querySelector(':scope > .rl')).filter(r => r && r.offsetHeight > (+r.dataset.min) * LINE).pop();
        if (!rl) break;
        rl.style.height = (rl.offsetHeight - LINE) + 'px';
      }
      return;
    }
    if (sectionEnd && m.notes) {
      const need = 5 * LINE + 34;
      if (left >= need) {
        const n = document.createElement('div');
        n.className = 'notes';
        n.innerHTML = `<div class="sh">NOTES · ${page.sec}</div><div class="rl" data-min="4"></div>`;
        page.body.appendChild(n);
        const used = lastBottom(page);
        const rl = n.querySelector('.rl');
        const lines = Math.floor((LIMIT - used - 2) / LINE);
        let L = Math.max(0, lines);
        rl.style.height = L * LINE + 'px';
        while (L > 0 && lastBottom(page) > LIMIT + 0.5) { L--; rl.style.height = L * LINE + 'px'; }
        if (L < 4) n.remove();
      }
    }
  }

  function closePage(sectionEnd) { if (cur) fill(cur, sectionEnd); }

  // move trailing keep-with-next elements (captions, subheads, OD boxes) to the next page with the block
  function trailingKeeps() {
    const c = content(cur.body), out = [];
    for (let k = c.length - 1; k >= 0; k--) {
      if (c[k].dataset.keepNext) out.unshift(c[k]); else break;
    }
    if (out.length === c.length) return [];
    return out;
  }

  function freshPage(sec) { closePage(false); makePage(sec, false); }

  function fixColumns(tbl) {
    if (tbl.querySelector('colgroup')) { tbl.style.tableLayout = 'fixed'; return; }
    tbl.style.tableLayout = 'auto';
    const ths = [...tbl.tHead.rows[0].cells];
    const widths = ths.map(th => th.getBoundingClientRect().width);
    const cg = document.createElement('colgroup');
    widths.forEach(w => { const c = document.createElement('col'); c.style.width = w + 'px'; cg.appendChild(c); });
    tbl.insertBefore(cg, tbl.firstChild);
    tbl.style.tableLayout = 'fixed';
  }

  function placeTable(tbl, sec, depth) {
    cur.body.appendChild(tbl);
    fixColumns(tbl);
    if (fits(tbl)) return;
    const tb = tbl.tBodies[0];
    const rest = [];
    while (tb.rows.length && !fits(tbl)) { const r = tb.rows[tb.rows.length - 1]; rest.unshift(r); r.remove(); }
    const freshTop = content(cur.body).length === 1 || (content(cur.body).length && content(cur.body)[0] === tbl);
    if (!tb.rows.length) {
      rest.forEach(r => tb.appendChild(r));
      tbl.remove();
      if (freshTop || depth > 2) { // a single row taller than a page: place it and flag
        cur.body.appendChild(tbl);
        flags.push({ page: pages.length, type: 'oversize-row', sec });
        return;
      }
      const keeps = trailingKeeps();
      keeps.forEach(k => k.remove());
      freshPage(sec);
      keeps.forEach(k => cur.body.appendChild(k));
      return placeTable(tbl, sec, depth + 1);
    }
    const t2 = tbl.cloneNode(false);
    t2.appendChild(tbl.querySelector('colgroup').cloneNode(true));
    t2.appendChild(tbl.tHead.cloneNode(true));
    const b2 = document.createElement('tbody');
    rest.forEach(r => b2.appendChild(r));
    t2.appendChild(b2);
    t2.classList.add('cont');
    freshPage(sec);
    placeTable(t2, sec, 0);
  }

  function placeBlock(el, sec) {
    if (el.tagName === 'TABLE' && el.dataset.split) return placeTable(el, sec, 0);
    cur.body.appendChild(el);
    if (fits(el)) return;
    const onlyThis = content(cur.body).length === 1;
    if (onlyThis) { flags.push({ page: pages.length, type: 'oversize-block', sec, cls: el.className }); return; }
    el.remove();
    const keeps = trailingKeeps();
    keeps.forEach(k => k.remove());
    freshPage(sec);
    keeps.forEach(k => cur.body.appendChild(k));
    cur.body.appendChild(el);
    if (!fits(el)) flags.push({ page: pages.length, type: 'oversize-block', sec, cls: el.className });
  }

  // ---- pre-pass: resolve references before layout so widths are final (page numbers use reserved width)
  function refTitle(r) { return D.titles[r] || ''; }
  function prepass() {
    src.querySelectorAll('.xr').forEach(x => { if (!D.anchor[x.dataset.ref]) x.classList.add('out'); });
    src.querySelectorAll('.chip[data-ref]').forEach(c => {
      const r = c.dataset.ref, a = D.anchor[r], t = refTitle(r);
      const disp = r === 'III.20W' ? 'III.20' : r;
      if (a) {
        const via = a === 'CR' && r !== 'CR' ? ' → 3SL concordance' : '';
        c.innerHTML = `${disp}${t && !c.closest('.wq, .fixed, .ith, .endl, .tb, .sh') ? ' ' + t : ''}${via} · <span class="pn" data-anchor="${a}">p.000</span>`;
      } else {
        c.classList.add('out');
        c.innerHTML = `${disp}${t ? ' ' + t : ''} †`;
      }
    });
    src.querySelectorAll('.chip[data-wref]').forEach(c => { c.innerHTML = `<span class="pn" data-anchor="${c.dataset.wref}">p.000</span>`; });
    // contents
    const toc = src.querySelector('#toc-src');
    if (toc) {
      let h = '<table class="toc" data-split="1"><colgroup><col style="width:80px"><col><col style="width:60px"></colgroup><thead><tr><th></th><th></th><th></th></tr></thead><tbody>';
      for (const [part, anchor, items] of D.toc) {
        h += `<tr class="part"><td colspan="2">${part}</td><td class="pgn">${anchor ? `<span class="pn" data-anchor="${anchor}">000</span>` : ''}</td></tr>`;
        for (const [code, title] of items) {
          const disp = code.startsWith('APP-') || code === 'ABOUT' ? '' : (code === 'III.20W' ? 'III.20' : (code === 'CR' ? 'VII·3SL' : code));
          h += `<tr><td class="cd">${disp}</td><td>${title}</td><td class="pgn"><span class="pn" data-anchor="${code}">000</span></td></tr>`;
        }
      }
      h += '</tbody></table>';
      const t = document.createElement('div');
      t.innerHTML = h;
      const tbl = t.firstChild;
      tbl.dataset.sec = 'TOC';
      toc.replaceWith(tbl);
    }
    src.querySelectorAll('.wn').forEach(s => { s.textContent = '00 OF 00'; });
    src.querySelectorAll('td.pgn[data-pref]').forEach(td => { td.innerHTML = `<span class="pn" data-anchor="${D.anchor[td.dataset.pref] || td.dataset.pref}">000</span>`; });
  }

  // ---- post-pass: folios, counters, page numbers, footer fit
  function postpass() {
    const first = {}, bySec = {};
    pages.forEach((p, i) => {
      p.n = i + 1;
      (bySec[p.sec] = bySec[p.sec] || []).push(p);
      if (!(p.sec in first)) first[p.sec] = p.n;
      p.el.querySelectorAll('[data-anchor-at]').forEach(() => {});
    });
    // anchors placed on working openers (W-A … W-E)
    const anchorPage = Object.assign({}, first);
    pages.forEach(p => p.body.querySelectorAll('.hd[data-anchor]').forEach(h => { anchorPage[h.dataset.anchor] = p.n; }));
    // working pages: "k OF N" and per-item spans
    const work = bySec['III.20W'] || [];
    work.forEach((p, k) => p.body.querySelectorAll('.wn').forEach(s => { s.textContent = `${k + 1} OF ${work.length}`; }));
    const itemPages = {};
    let curItem = null;
    work.forEach(p => { const h = p.body.querySelector('.hd[data-anchor]'); if (h) curItem = h.dataset.anchor; if (curItem) (itemPages[curItem] = itemPages[curItem] || []).push(p.n); });
    document.querySelectorAll('.pn').forEach(s => {
      const a = s.dataset.anchor;
      const isWork = s.closest('.qt');
      let n = anchorPage[a];
      if (isWork && itemPages[a]) {
        const ps = itemPages[a];
        s.textContent = ps.length > 1 ? `p.${ps[0]}–${ps[ps.length - 1]}` : `p.${ps[0]}`;
        return;
      }
      if (n == null) { flags.push({ type: 'unresolved-anchor', anchor: a }); s.textContent = '??'; return; }
      s.textContent = s.closest('.chip') ? `p.${n}` : String(n);
    });
    // footers
    for (const sec in bySec) {
      const list = bySec[sec], m = D.secmeta[sec];
      list.forEach((p, k) => {
        const ft = p.el.querySelector('.ft');
        if (!ft) return;
        let crumb = m.crumb;
        if (sec === 'III.20W') {
          const h = [...p.body.querySelectorAll('.hd .kind')].pop();
          let item = null;
          for (const q of work) { const hh = q.body.querySelector('.hd .kind'); if (hh) item = hh.textContent; if (q === p) break; }
          const mm = item && item.match(/ITEM ([A-E])/);
          crumb = '3SL › III.20 · ' + (mm ? 'ITEM ' + mm[1] : 'THE QUEUE');
        }
        const more = k < list.length - 1 ? ' · CONTINUES →' : '';
        ft.querySelector('.fl1').textContent = crumb + more;
        const fol = m.folio ? `${m.folio}${list.length > 1 || m.folio.length < 6 ? ' / ' + (k + 1) : ''} · ` : '';
        ft.querySelector('.fr').textContent = `${fol}${p.n}`;
        // single-line check: if the three parts can't share one line, give the footer a second row inside the safe zone
        const tot = [...ft.children].reduce((a, c) => a + c.scrollWidth, 0) + 16 * (ft.children.length - 1);
        if (tot > ft.clientWidth) ft.classList.add('two');
      });
    }
    return { first, anchorPage, itemPages };
  }

  // ---- QA
  function qa(info) {
    const issues = [];
    pages.forEach(p => {
      const pr = p.el.getBoundingClientRect();
      p.body.querySelectorAll('*').forEach(e => {
        const r = e.getBoundingClientRect();
        if (!r.width && !r.height) return;
        if (r.bottom - pr.top > LIMIT + 1) issues.push({ page: p.n, type: 'safe-zone', el: e.className || e.tagName, by: Math.round(r.bottom - pr.top - LIMIT) });
        if (r.right - pr.left > COL_R + 1.5 || r.left - pr.left < COL_L - 1.5) issues.push({ page: p.n, type: 'margin', el: e.className || e.tagName, l: Math.round(r.left - pr.left), r: Math.round(r.right - pr.left) });
        if ((e.tagName === 'TD' || e.tagName === 'TH' || e.classList.contains('chip') || e.classList.contains('pt')) && e.scrollWidth > e.clientWidth + 1)
          issues.push({ page: p.n, type: 'clip-x', el: e.className || e.tagName, text: e.textContent.slice(0, 60) });
      });
      const ft = p.el.querySelector('.ft');
      if (ft) {
        const fr = ft.getBoundingClientRect();
        if (fr.top - pr.top < LIMIT) issues.push({ page: p.n, type: 'footer-above-safe-line', top: Math.round(fr.top - pr.top) });
        [...ft.children].forEach(c => { if (c.getBoundingClientRect().height > 20) issues.push({ page: p.n, type: 'footer-wrap', text: c.textContent }); });
        if (fr.bottom - pr.top > 1056) issues.push({ page: p.n, type: 'footer-off-page' });
      }
      const c = content(p.body);
      if (!c.length) issues.push({ page: p.n, type: 'empty-page' });
      const last = c[c.length - 1];
      if (last && (last.classList.contains('cap') || last.dataset.keepNext) && !last.classList.contains('lg')) issues.push({ page: p.n, type: 'orphaned-caption', text: last.textContent.slice(0, 60) });
      if (last && last.classList.contains('lg') && last.classList.contains('od') && p.sec.startsWith('III.') && p.sec !== 'III.20W') {
        // OD box at page foot is allowed; its working space follows on the next page
      }
    });
    const writing = [];
    document.querySelectorAll('#book .rl').forEach(rl => {
      const min = +(rl.dataset.min || 0), h = rl.offsetHeight, pg = rl.closest('.pg');
      const lines = Math.round(h / LINE);
      if (h + 0.5 < min * LINE) issues.push({ page: pages.find(p => p.el === pg).n, type: 'writing-below-min', min, lines });
      writing.push({ page: pages.find(p => p.el === pg).n, sec: pg.dataset.sec, kind: rl.parentElement.className.split(' ')[0] || rl.parentElement.tagName, min, lines });
    });
    // every printed page reference must land on a page that carries that section
    const refCheck = [];
    document.querySelectorAll('#book .pn').forEach(s => {
      const a = s.dataset.anchor, m = s.textContent.match(/(\d+)/);
      if (!m) { issues.push({ type: 'pageref-missing', anchor: a }); return; }
      const n = +m[1], pg = pages[n - 1];
      const ok = pg && (pg.sec === a || pg.body.querySelector(`.hd[data-anchor="${a}"]`));
      refCheck.push({ anchor: a, page: n, ok: !!ok, from: pages.find(p => p.el === s.closest('.pg')).n });
      if (!ok) issues.push({ type: 'pageref-wrong', anchor: a, page: n });
    });
    const out = [...document.querySelectorAll('#book .xr.out, #book .chip.out')].map(e => e.dataset.ref);
    const resolved = [...document.querySelectorAll('#book .chip[data-ref]:not(.out)')].map(e => e.dataset.ref);
    const footerRows = pages.filter(p => p.el.querySelector('.ft.two')).map(p => p.n);
    const pageSecs = pages.map(p => p.sec);
    return { pages: pages.length, issues, flags, writing, refCheck, footerRows, pageSecs, refs: { outside: out, resolved }, sections: Object.fromEntries(Object.entries(info.first)), itemPages: info.itemPages,
      sectionPages: pages.reduce((a, p) => { a[p.sec] = (a[p.sec] || 0) + 1; return a; }, {}) };
  }

  window.paginate = function () {
    prepass();
    const blocks = [...src.children];
    for (let k = 0; k < blocks.length; k++) {
      const el = blocks[k];
      const sec = el.dataset.sec;
      if (!sec) continue;
      if (el.dataset.newpage) { closePage(cur && cur.sec !== sec); makePage(sec, true); }
      else if (el.dataset.newpageSoft) { closePage(false); makePage(sec, false); }
      else if (!cur || cur.sec !== sec) { closePage(true); makePage(sec, false); }
      placeBlock(el, sec);
    }
    closePage(true);
    const info = postpass();
    const result = qa(info);
    // text order check: every source block made it into the book
    result.blocksPlaced = blocks.length;
    result.blocksInBook = document.querySelectorAll('#book .body > *:not(.rh):not(.notes)').length;
    return result;
  };
})();
