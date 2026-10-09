# ו-1: "ייצוא ל-Word" makes a real .docx (Office Open XML) instead of an HTML page renamed .doc — right-to-left
# paragraphs, fonts / sizes / colours / bold / italic / underline per run, alignment, line spacing, tables and
# divider lines. Built in the browser (a small ZIP writer), so it works offline.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('ייצוא docx',
"""document.getElementById('export-btn').onclick = () => {
  const bodyHtml = editor.innerHTML || '';""",
r"""// ---------- ו-1: real .docx export ----------
const DocxExport = (function(){
  const enc = new TextEncoder();
  const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++){ let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  const crc32 = (b) => { let c = 0xFFFFFFFF; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  function zip(files){   // stored (no compression) — Word reads it fine
    const parts = [], central = []; let off = 0;
    const now = new Date(), dt = ((now.getFullYear() - 1980) << 25) | ((now.getMonth() + 1) << 21) | (now.getDate() << 16) | (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
    for (const [name, text] of files){
      const nb = enc.encode(name), data = enc.encode(text), crc = crc32(data);
      const h = new DataView(new ArrayBuffer(30));
      h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true); h.setUint16(8, 0, true);
      h.setUint32(10, dt, true); h.setUint32(14, crc, true); h.setUint32(18, data.length, true); h.setUint32(22, data.length, true);
      h.setUint16(26, nb.length, true); h.setUint16(28, 0, true);
      parts.push(new Uint8Array(h.buffer), nb, data);
      const c = new DataView(new ArrayBuffer(46));
      c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true); c.setUint16(10, 0, true);
      c.setUint32(12, dt, true); c.setUint32(16, crc, true); c.setUint32(20, data.length, true); c.setUint32(24, data.length, true);
      c.setUint16(28, nb.length, true); c.setUint32(42, off, true);
      central.push(new Uint8Array(c.buffer), nb);
      off += 30 + nb.length + data.length;
    }
    const csize = central.reduce((s, x) => s + x.length, 0);
    const e = new DataView(new ArrayBuffer(22));
    e.setUint32(0, 0x06054b50, true); e.setUint16(8, files.length, true); e.setUint16(10, files.length, true);
    e.setUint32(12, csize, true); e.setUint32(16, off, true);
    return new Blob(parts.concat(central, [new Uint8Array(e.buffer)]), { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
  }
  const x = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F-]/g, '');
  // the web fonts of the editor → the Windows font Word will find
  const FONT_MAP = { 'david libre': 'David', 'frank ruhl libre': 'FrankRuehl', 'miriam libre': 'Miriam', 'tinos': 'Times New Roman', 'arimo': 'Arial' };
  function fontName(css){
    const f = String(css || '').split(',')[0].trim().replace(/^["']|["']$/g, '');
    return FONT_MAP[f.toLowerCase()] || f || 'David';
  }
  const halfPts = (px) => { const v = parseFloat(px); return v > 0 ? Math.max(2, Math.round(v * 1.5)) : null; };   // px → pt (×0.75) → half-points
  function rPr(st, base, rtl){
    const font = fontName(st.font || base.font), sz = halfPts(st.size || base.size);
    let r = '<w:rPr><w:rFonts w:ascii="' + x(font) + '" w:hAnsi="' + x(font) + '" w:cs="' + x(font) + '"/>';
    if (st.bold) r += '<w:b/><w:bCs/>';
    if (st.italic) r += '<w:i/><w:iCs/>';
    if (st.color && /^#[0-9a-f]{6}$/i.test(st.color)) r += '<w:color w:val="' + st.color.slice(1).toUpperCase() + '"/>';
    if (sz) r += '<w:sz w:val="' + sz + '"/><w:szCs w:val="' + sz + '"/>';
    if (st.underline) r += '<w:u w:val="single"/>';
    if (rtl) r += '<w:rtl/>';
    return r + '<w:lang w:val="he-IL" w:bidi="he-IL"/></w:rPr>';
  }
  // Latin words get their own LTR runs; the rest is RTL (Hebrew, digits, punctuation)
  function runs(textPart, st, base, ltrLine){
    let out = '', last = 0;
    if (ltrLine){ return textPart ? '<w:r>' + rPr(st, base, false) + '<w:t xml:space="preserve">' + x(textPart) + '</w:t></w:r>' : ''; }   // an English-only line
    const re = /[A-Za-z][A-Za-z0-9]*(?:[ '\-.:\/][A-Za-z0-9]+)*/g;
    let m;
    const emit = (s, rtl) => { if (s) out += '<w:r>' + rPr(st, base, rtl) + '<w:t xml:space="preserve">' + x(s) + '</w:t></w:r>'; };
    while ((m = re.exec(textPart))){ emit(textPart.slice(last, m.index), true); emit(m[0], false); last = m.index + m[0].length; }
    emit(textPart.slice(last), true);
    return out;
  }
  function pPr(base, ltr, extra){
    let p = '<w:pPr>' + (ltr ? '<w:bidi w:val="0"/>' : '<w:bidi/>') + (extra || '');
    p += '<w:spacing w:before="0" w:after="0" w:line="' + Math.round(240 * (parseFloat(base.lineHeight) || 1.5)) + '" w:lineRule="auto"/>';
    const a = base.align;
    // in a right-to-left paragraph Word reads "left"/"right" from the reading start, so they are swapped there
    const jc = a === 'center' ? 'center' : a === 'justify' ? 'both' : a === 'left' ? (ltr ? 'left' : 'right') : (ltr ? 'right' : '');
    if (jc) p += '<w:jc w:val="' + jc + '"/>';
    return p + '</w:pPr>';
  }
  function divider(style, base){
    const ornament = { ornate: '❦', diamond: '◆   ◆   ◆', stars: '✦   ✦   ✦', wave: '〜〜〜〜〜〜〜〜' }[style];
    if (ornament) return '<w:p>' + pPr(Object.assign({}, base, { align: 'center' }), false) + runs(ornament, { color: '#B98A3E' }, base) + '</w:p>';
    const b = { simple: ['single', 6, 'auto'], double: ['double', 6, 'auto'], dashed: ['dashed', 6, 'auto'], dotted: ['dotted', 8, 'auto'], brass: ['single', 18, 'B98A3E'] }[style] || ['single', 6, 'auto'];
    return '<w:p><w:pPr><w:bidi/><w:pBdr><w:bottom w:val="' + b[0] + '" w:sz="' + b[1] + '" w:space="1" w:color="' + b[2] + '"/></w:pBdr><w:spacing w:before="120" w:after="120"/></w:pPr></w:p>';
  }
  // a plain (left-to-right) table with its columns in reverse order, aligned to the right margin: Word and
  // LibreOffice read the alignment of a right-to-left table (bidiVisual) differently, this looks the same in both
  function table(t, base){
    const cols = (t.rows[0] || []).length;
    const widths = (t.colWidths && t.colWidths.length === cols) ? t.colWidths : new Array(cols).fill(120);
    const order = widths.map((_, i) => cols - 1 - i);
    let s = '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:jc w:val="right"/><w:tblBorders>' +
      ['top', 'left', 'bottom', 'right', 'insideH', 'insideV'].map(k => '<w:' + k + ' w:val="single" w:sz="4" w:space="0" w:color="auto"/>').join('') +
      '</w:tblBorders><w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>' +
      order.map(i => '<w:gridCol w:w="' + Math.round(widths[i] * 15) + '"/>').join('') + '</w:tblGrid>';
    for (const row of t.rows){
      s += '<w:tr>';
      for (const i of order){
        const cell = row[i];
        s += '<w:tc><w:tcPr><w:tcW w:w="' + Math.round((widths[i] || 120) * 15) + '" w:type="dxa"/></w:tcPr>';
        for (const line of String(cell == null ? '' : cell).split('\n')) s += '<w:p>' + pPr(Object.assign({}, base, { lineHeight: 1.2 }), false) + runs(line, {}, base) + '</w:p>';
        s += '</w:tc>';
      }
      s += '</w:tr>';
    }
    return s + '</w:tbl><w:p><w:pPr><w:bidi/></w:pPr></w:p>';
  }
  function documentXml(text){
    const base = { font: editor.style.fontFamily || "'David Libre', serif", size: editor.style.fontSize || '19px',
                   lineHeight: editor.style.lineHeight || '2', align: editor.style.textAlign || 'right' };
    const embeds = findEmbeddedRanges(text);
    const segs = splitSegmentsAtEmbeds(computeFinalRuns(text), embeds);
    const ltr = findLtrLineStarts(text, embeds) || new Set();
    let body = '', para = '', paraStart = 0, skipNl = false;
    const flush = () => { body += '<w:p>' + pPr(base, ltr.has(paraStart)) + para + '</w:p>'; para = ''; };
    for (const seg of segs){
      const em = embeds.find(d => d.start === seg.start && d.end === seg.end);
      if (em){
        if (para) flush();
        if (em.kind === 'divider') body += divider(em.style, base);
        else { const t = tables.find(q => q.id === em.tableId); if (t) body += table(t, base); }
        skipNl = true;
        continue;
      }
      const chunk = text.slice(seg.start, seg.end);
      let pos = seg.start;
      chunk.split('\n').forEach((part, k) => {
        if (k > 0){
          if (skipNl && !para){ skipNl = false; } else flush();
          paraStart = pos;
        }
        if (part){ para += runs(part, seg.style, base, ltr.has(paraStart)); skipNl = false; }
        pos += part.length + 1;
      });
    }
    if (para || !body) flush();
    const W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"';
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document ' + W + '><w:body>' + body +
      '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr></w:body></w:document>';
  }
  function stylesXml(){
    const f = fontName(editor.style.fontFamily || "'David Libre', serif"), sz = halfPts(editor.style.fontSize || '19px') || 28;
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' +
      '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="' + x(f) + '" w:hAnsi="' + x(f) + '" w:cs="' + x(f) + '"/><w:sz w:val="' + sz + '"/><w:szCs w:val="' + sz + '"/>' +
      '<w:lang w:val="he-IL" w:bidi="he-IL"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:bidi/></w:pPr></w:pPrDefault></w:docDefaults>' +
      '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style></w:styles>';
  }
  function build(){
    const text = extractPlainText(editor);
    const ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>' +
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>' +
      '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>';
    const rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
      '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>';
    const drels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
      '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>';
    return zip([['[Content_Types].xml', ct], ['_rels/.rels', rels], ['word/document.xml', documentXml(text)], ['word/_rels/document.xml.rels', drels], ['word/styles.xml', stylesXml()]]);
  }
  function fileName(){
    let n = '';
    try { const d = currentDocId && loadDocs()[currentDocId]; n = d && d.name || ''; } catch (e) { /* ignore */ }
    n = (n || 'מסמך-מעוצב').replace(/[\\\/:*?"<>|]+/g, '-').trim() || 'מסמך-מעוצב';
    return n + '.docx';
  }
  return { build, fileName, documentXml };
})();
window.DocxExport = DocxExport;

document.getElementById('export-btn').onclick = () => {
  try {
    const blob = DocxExport.build();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = DocxExport.fileName();
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 60000);
    flashStatus('קובץ Word (‎.docx) הורד.');
    return;
  } catch (e) { console.error('docx export failed — saving the older .doc instead:', e); }
  exportOldDoc();
};
function exportOldDoc(){   // the earlier export (an HTML page Word can open), kept as a fallback
  const bodyHtml = editor.innerHTML || '';""")

step('סוף הייצוא הישן',
"""  a.download = 'מסמך-מעוצב.doc';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  flashStatus('קובץ Word הורד.');
};""",
"""  a.download = 'מסמך-מעוצב.doc';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  flashStatus('קובץ Word הורד.');
}""")

step('מדריך',
"""      { n: 'ייצוא ל-Word', s: '#export-btn', d: 'שומר את המסמך כקובץ שנפתח ב-Word.' }""",
"""      { n: 'ייצוא ל-Word', s: '#export-btn', d: 'שומר את המסמך כקובץ Word אמיתי (‎.docx) בשם הקובץ: מימין לשמאל, עם הגופנים, הגדלים, הצבעים, ההדגשות, היישור, הריווח, הטבלאות והקווים המפרידים. גופני הרשת של העורך מוחלפים בגופני Windows המקבילים (David Libre ← David, Frank Ruhl Libre ← FrankRuehl, Miriam Libre ← Miriam).' }""")

MARK = "// ---------- ו-1: real .docx export"
NEED = {'mark': "// ה-3: common words one slip away from a rarer one", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
