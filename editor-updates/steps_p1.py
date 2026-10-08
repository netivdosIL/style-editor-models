# פ-1: paste from outside either as clean text (as before) or keeping font, size, bold, italic and underline (no colour).
# The choice is a fixed setting in "🖇️ הגדרות העתקה".
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('הגדרה בחלון הגדרות העתקה',
"""      <div class="field">
        <label>שם ההגדרה (לזיהוי בלבד)</label>
        <input type="text" id="in-preset-name" placeholder="למשל: ציטוט">""",
"""      <div class="field paste-keep-field">
        <label>הדבקה מתוכנה אחרת (וורד, אתר וכו')</label>
        <label class="paste-keep-opt"><input type="radio" name="paste-keep" value="clean"> טקסט נקי — העיצוב של העורך</label>
        <label class="paste-keep-opt"><input type="radio" name="paste-keep" value="keep"> לשמור גופן, גודל והדגשות מהמקור (בלי צבע)</label>
      </div>
      <div class="field">
        <label>שם ההגדרה (לזיהוי בלבד)</label>
        <input type="text" id="in-preset-name" placeholder="למשל: ציטוט">""")

step('עיצוב ההגדרה',
"""  .wl-chips .folder-install-btn{""",
"""  .paste-keep-field{ margin-top:16px; padding-bottom:12px; margin-bottom:14px; border-bottom:1px dashed var(--line); }
  .paste-keep-opt{ display:flex !important; align-items:center; gap:8px; font-size:13.5px; color: var(--parchment) !important; margin:4px 0 !important; cursor:pointer; }
  .paste-keep-opt input{ width:auto !important; margin:0; }
  .wl-chips .folder-install-btn{""")

step('הדבקה עם עיצוב',
"""editor.addEventListener('paste', (e) => {
  e.preventDefault();
  const pasted = (e.clipboardData || window.clipboardData).getData('text/plain');
  if (!pasted) return;
  const { start, end } = getSelectionOffsets(editor);
  const text = extractPlainText(editor);
  const newText = text.slice(0, start) + pasted + text.slice(end);
  remapManualStylesForNewText(newText);
  renderTextIntoEditor(newText, start + pasted.length);
  pushHistory(true);""",
"""// ---------- פ-1: paste keeping the source font / size / bold / italic / underline (no colour) ----------
const PASTE_KEEP_KEY = 'heb-style-editor-paste-keep-v1';
function pasteKeepMode(){ try { return localStorage.getItem(PASTE_KEEP_KEY) === 'keep'; } catch (e) { return false; } }
(function setupPasteKeepSetting(){
  const radios = document.querySelectorAll('input[name="paste-keep"]');
  radios.forEach(r => { r.checked = (r.value === 'keep') === pasteKeepMode(); r.onchange = () => { if (r.checked) try { localStorage.setItem(PASTE_KEEP_KEY, r.value); } catch (e) { /* ignore */ } }; });
})();
// Lays the pasted HTML out in a hidden, script-free frame and reads what each piece of text really looks like there
// (so Word's class styles count too). Returns { text, runs } with runs only where the source set something.
// Word keeps the font of Hebrew text in mso-bidi-font-family / -size / -weight / -style, which browsers ignore.
function wordBidiToCss(html){
  if (!/[\\u0590-\\u05ff]/.test(html) || !/mso-bidi-font/i.test(html)) return html;
  const fix = (decl) => {
    const parts = decl.split(';'), bidi = {};
    for (const p of parts){ const m = /^\\s*mso-bidi-(font-family|font-size|font-weight|font-style)\\s*:\\s*(.+?)\\s*$/i.exec(p); if (m) bidi[m[1].toLowerCase()] = m[2]; }
    if (!Object.keys(bidi).length) return decl;
    const kept = parts.filter(p => { const m = /^\\s*(font-family|font-size|font-weight|font-style)\\s*:/i.exec(p); return !(m && bidi[m[1].toLowerCase()]); });
    return kept.concat(Object.keys(bidi).map(k => k + ':' + bidi[k])).join(';');
  };
  return html
    .replace(/(<style[^>]*>)([\\s\\S]*?)(<\\/style>)/gi, (all, a, css, c) => a + css.replace(/\\{([^{}]*)\\}/g, (m, d) => '{' + fix(d) + '}') + c)
    .replace(/(\\sstyle\\s*=\\s*)(['"])([\\s\\S]*?)\\2/gi, (all, a, q, d) => a + q + fix(q === '"' ? d.replace(/&quot;/g, "'") : d) + q);
}
function htmlToStyledText(html){
  const parsed = new DOMParser().parseFromString(wordBidiToCss(html), 'text/html');
  parsed.querySelectorAll('script, iframe, object, embed, link, img, picture, video, audio, svg, canvas, input, button, select, textarea, meta, title').forEach(n => n.remove());
  parsed.querySelectorAll('*').forEach(el => { for (const a of Array.from(el.attributes)) if (/^on/i.test(a.name) || /^(src|href|srcset)$/i.test(a.name)) el.removeAttribute(a.name); });
  const frame = document.createElement('iframe');
  frame.setAttribute('sandbox', 'allow-same-origin');
  frame.setAttribute('aria-hidden', 'true'); frame.tabIndex = -1;
  frame.style.cssText = 'position:fixed; left:-20000px; top:0; width:900px; height:400px; visibility:hidden; border:0;';
  document.body.appendChild(frame);
  try {
    const doc = frame.contentDocument;
    doc.open(); doc.write('<!doctype html><html><head></head><body></body></html>'); doc.close();
    parsed.querySelectorAll('style').forEach(s => doc.head.appendChild(doc.importNode(s, true)));
    doc.body.innerHTML = parsed.body ? parsed.body.innerHTML : '';
    const win = frame.contentWindow;
    const probe = doc.createElement('span'); probe.textContent = 'x'; doc.documentElement.appendChild(probe);
    const def = win.getComputedStyle(probe), defFont = def.fontFamily, defSize = def.fontSize;
    probe.remove();
    let out = '';
    const runs = [];
    const BLOCK = /^(block|list-item|table|table-row|table-caption|flex|grid)$/;
    const nl = () => { if (out && !out.endsWith('\\n')) out += '\\n'; };
    const styleOf = (el) => {
      const cs = win.getComputedStyle(el);
      let underline = false;
      for (let a = el; a && a !== doc.documentElement; a = a.parentElement){ if (/underline/.test(win.getComputedStyle(a).textDecorationLine || '')){ underline = true; break; } }
      const fam = (cs.fontFamily || '').split(',')[0].trim().replace(/^["']|["']$/g, '');
      const font = cs.fontFamily && cs.fontFamily !== defFont && fam ? "'" + fam.replace(/'/g, '') + "', sans-serif" : null;
      const px = parseFloat(cs.fontSize);
      const size = cs.fontSize !== defSize && px > 0 ? Math.round(px) + 'px' : null;
      return { font, size, bold: (parseInt(cs.fontWeight, 10) || 400) >= 600, italic: /italic|oblique/.test(cs.fontStyle), underline };
    };
    const walk = (node) => {
      if (node.nodeType === 3){
        const el = node.parentElement; if (!el) return;
        const cs = win.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;
        let t = node.nodeValue.replace(/\\u00a0/g, ' ').replace(/[\\u200b\\u200c\\u200d\\ufeff]/g, '');
        if (!/^pre/.test(cs.whiteSpace)){ t = t.replace(/[\\s]+/g, ' '); if (!out || /[ \\n]$/.test(out)) t = t.replace(/^ /, ''); }
        if (!t) return;
        const st = styleOf(el), s0 = out.length;
        out += t;
        const last = runs[runs.length - 1];
        if (last && last.end === s0 && last.font === st.font && last.size === st.size && last.bold === st.bold && last.italic === st.italic && last.underline === st.underline) last.end = out.length;
        else runs.push(Object.assign({ start: s0, end: out.length }, st));
        return;
      }
      if (node.nodeType !== 1) return;
      const tag = node.tagName;
      if (tag === 'BR'){ out += '\\n'; return; }
      if (tag === 'STYLE' || tag === 'HEAD') return;
      const cs = win.getComputedStyle(node);
      if (cs.display === 'none') return;
      const block = BLOCK.test(cs.display);
      if (block) nl();
      if (cs.display === 'table-cell' && out && !/[ \\n]$/.test(out)) out += ' ';
      for (const c of node.childNodes) walk(c);
      if (block) nl();
    };
    walk(doc.body);
    // trailing spaces / blank lines at the edges are layout, not content
    let a = 0; while (a < out.length && /[\\s]/.test(out[a])) a++;
    let b = out.length; while (b > a && /[\\s]/.test(out[b - 1])) b--;
    const text = out.slice(a, b).replace(/ +\\n/g, (m) => '\\n'.padStart(1));
    if (!text) return null;
    // map runs onto the trimmed text (only spaces before line breaks were dropped inside it)
    const map = []; let j = 0;
    const raw = out.slice(a, b);
    for (let i = 0; i < raw.length; i++){ map[i] = j; if (!(raw[i] === ' ' && /^ *\\n/.test(raw.slice(i)))) j++; }
    map[raw.length] = j;
    const outRuns = [];
    for (const r of runs){
      const s = map[Math.max(0, Math.min(raw.length, r.start - a))], en = map[Math.max(0, Math.min(raw.length, r.end - a))];
      if (en <= s) continue;
      if (!r.font && !r.size && !r.bold && !r.italic && !r.underline) continue;
      outRuns.push({ start: s, end: en, font: r.font, size: r.size, bold: r.bold, italic: r.italic, underline: r.underline });
    }
    return { text, runs: outRuns };
  } finally { frame.remove(); }
}

editor.addEventListener('paste', (e) => {
  e.preventDefault();
  const cd = (e.clipboardData || window.clipboardData);
  let pasted = cd.getData('text/plain'), keptRuns = null;
  if (pasteKeepMode()){
    const html = cd.getData('text/html');
    if (html){ try { const r = htmlToStyledText(html); if (r){ pasted = r.text; keptRuns = r.runs; } } catch (err) { console.warn('paste with formatting failed, pasting clean text:', err); } }
  }
  if (!pasted) return;
  const { start, end } = getSelectionOffsets(editor);
  const text = extractPlainText(editor);
  const newText = text.slice(0, start) + pasted + text.slice(end);
  remapManualStylesForNewText(newText);
  if (keptRuns && keptRuns.length){
    for (const r of keptRuns){
      manualStyles.push({ start: start + r.start, end: start + r.end, font: r.font, size: r.size, color: null, bold: r.bold, italic: r.italic, fromPaste: true });
      if (r.underline) underlineOverrides = replaceOverrideRange(underlineOverrides, start + r.start, start + r.end, true);
    }
  }
  renderTextIntoEditor(newText, start + pasted.length);
  pushHistory(true);""")

step('עיגול צבע מחליף את העיצוב שהודבק',
"""    showPastePresetPopup(x, y, (preset) => {
      manualStyles.push({""",
"""    showPastePresetPopup(x, y, (preset) => {
      // פ-1: a colour circle replaces the formatting that came with the paste
      manualStyles = manualStyles.filter(m => !(m.fromPaste && m.start >= pasteStart && m.end <= pasteEnd));
      underlineOverrides = underlineOverrides.filter(u => !(u.start >= pasteStart && u.end <= pasteEnd));
      manualStyles.push({""")

MARK = "const PASTE_KEEP_KEY = 'heb-style-editor-paste-keep-v1';"
NEED = None
