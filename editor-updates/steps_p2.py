# פ-2: add fonts — from a font file (kept inside the editor, works offline) or a font installed on the PC.
# Entry: "➕ הוספת גופן…" at the end of every font list. Added fonts appear in all font lists.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('חלון גופנים',
"""<div id="offline-modal" class="modal-overlay" hidden>""",
"""<div id="fonts-modal" class="modal-overlay" hidden>
  <div class="modal-box" style="max-width:480px;">
    <div class="modal-head">
      <h2>🔤 הוספת גופנים</h2>
      <button id="fonts-close" aria-label="סגירה">✕</button>
    </div>
    <div class="modal-body">
      <div class="hint" style="margin-top:0; border-top:none; padding-top:0;">גופן שמוסיפים כאן מופיע בכל רשימות הגופנים בעורך: גופן בסיס, עיצוב הגדרות והגדרות העתקה.</div>
      <div class="mf-sec">
        <h3>מקובץ גופן</h3>
        <p class="mf-note">קובץ ttf, otf או woff. הגופן נשמר בתוך העורך ועובד גם בלי אינטרנט.</p>
        <input type="file" id="mf-file" accept=".ttf,.otf,.woff,.woff2,font/ttf,font/otf,font/woff,font/woff2" multiple hidden>
        <button type="button" class="mf-btn" id="mf-file-btn">📄 בחירת קובץ גופן</button>
      </div>
      <div class="mf-sec">
        <h3>גופן שמותקן במחשב</h3>
        <button type="button" class="mf-btn" id="mf-local-btn" hidden>🖥️ הצגת הגופנים שבמחשב</button>
        <div id="mf-local-wrap" hidden>
          <input type="text" id="mf-local-search" placeholder="חיפוש גופן…" autocomplete="off">
          <div id="mf-local-list" role="listbox" aria-label="הגופנים שבמחשב"></div>
        </div>
        <p class="mf-note">או כותבים את שם הגופן, כמו שהוא מופיע בוורד:</p>
        <div class="mf-row"><input type="text" id="mf-name" placeholder="למשל: David" autocomplete="off"><button type="button" class="mf-btn" id="mf-name-btn">הוסף</button></div>
      </div>
      <div id="mf-msg" role="status" aria-live="polite"></div>
      <div class="mf-sec">
        <h3>הגופנים שלי</h3>
        <div id="mf-list"></div>
        <p class="mf-note">בקובץ Word שהעורך מוריד, גופן שנוסף מקובץ יוצג רק במחשב שהגופן מותקן בו.</p>
      </div>
    </div>
  </div>
</div>

<div id="offline-modal" class="modal-overlay" hidden>""")

step('עיצוב חלון הגופנים',
"""  button.primary:hover{ background: var(--brass-bright); }
""",
"""  /* פ-2: my fonts */
  #fonts-modal .mf-sec{ padding:12px 0; border-bottom:1px dashed var(--line); }
  #fonts-modal .mf-sec:last-child{ border-bottom:none; }
  #fonts-modal h3{ margin:0 0 6px; font-size:14.5px; color: var(--parchment); font-weight:600; }
  #fonts-modal .mf-note{ margin:4px 0 8px; font-size:12.5px; color: var(--parchment-dim); line-height:1.6; }
  #fonts-modal .mf-btn{ font:inherit; font-size:13.5px; padding:6px 12px; border-radius:4px; border:1px solid var(--line); background: var(--panel); color: var(--parchment); cursor:pointer; }
  #fonts-modal .mf-btn:hover{ border-color: var(--brass); }
  #fonts-modal .mf-row{ display:flex; gap:8px; }
  #fonts-modal input[type=text]{ flex:1; min-width:0; font:inherit; font-size:14px; padding:6px 9px; border-radius:4px; border:1px solid var(--line); background: var(--panel); color: var(--parchment); }
  #fonts-modal input[type=text]:focus{ outline:none; border-color: var(--brass); }
  #mf-local-wrap{ margin-top:8px; }
  #mf-local-search{ width:100%; box-sizing:border-box; }
  #mf-local-list{ max-height:230px; overflow-y:auto; margin-top:6px; border:1px solid var(--line); border-radius:4px; }
  #mf-local-list button{ display:flex; justify-content:space-between; gap:10px; width:100%; text-align:right; background:none; border:none; border-bottom:1px solid var(--line); color: var(--parchment); padding:6px 10px; cursor:pointer; font-size:16px; }
  #mf-local-list button:last-child{ border-bottom:none; }
  #mf-local-list button:hover, #mf-local-list button:focus{ background: var(--panel); outline:none; }
  #mf-local-list .mf-fam{ font-family:'Rubik', sans-serif; font-size:13px; color: var(--parchment-dim); white-space:nowrap; }
  #mf-local-list .mf-added{ color: var(--brass); }
  #mf-msg{ min-height:20px; font-size:13px; font-weight:600; margin-top:6px; }
  #mf-msg.ok{ color:#5f9a63; } #mf-msg.err{ color: var(--danger, #c0533f); }
  #mf-list .rule-card .mf-sample{ font-size:19px; display:block; margin-top:2px; color: var(--parchment); }
  button.primary:hover{ background: var(--brass-bright); }
""")

step('גופנים שלי: טעינה, הוספה ומחיקה',
"""baseFontSelect.value = "'David Libre', serif";
""",
"""baseFontSelect.value = "'David Libre', serif";

// ---------- פ-2: my fonts — from a font file (stored in IndexedDB) or a font installed on the PC ----------
const MYFONTS_DB = 'heb-style-editor-fonts', MYFONTS_LOCAL_KEY = 'heb-style-editor-fonts-local-v1', ADD_FONT_VALUE = '__add_font__';
let myFonts = [];             // { id, name, kind: 'file' | 'local' }
const myFontFaces = {};       // id -> FontFace (file fonts)
let fontsTargetSelect = null; // the list "➕ הוספת גופן…" was picked from
const myFontValue = (name) => "'" + name + "', serif";
const cleanFontName = (s) => String(s || '').replace(/["'`\\\\;{}<>]/g, '').replace(/\\s+/g, ' ').trim().slice(0, 60);
function myFontsDb(){
  return new Promise((res, rej) => {
    const r = indexedDB.open(MYFONTS_DB, 1);
    r.onupgradeneeded = () => r.result.createObjectStore('fonts', { keyPath: 'id' });
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  });
}
async function myFontsTx(mode, fn){
  const db = await myFontsDb();
  return new Promise((res, rej) => {
    const tx = db.transaction('fonts', mode), q = fn(tx.objectStore('fonts'));
    let out; if (q) q.onsuccess = () => { out = q.result; };
    tx.oncomplete = () => { db.close(); res(out); };
    tx.onerror = tx.onabort = () => { db.close(); rej(tx.error || new Error('db')); };
  });
}
function loadLocalFontNames(){ try { const a = JSON.parse(localStorage.getItem(MYFONTS_LOCAL_KEY) || '[]'); return Array.isArray(a) ? a.map(cleanFontName).filter(Boolean) : []; } catch (e) { return []; } }
function saveLocalFontNames(){ try { localStorage.setItem(MYFONTS_LOCAL_KEY, JSON.stringify(myFonts.filter(f => f.kind === 'local').map(f => f.name))); } catch (e) { /* ignore */ } }
// the family name written inside a ttf/otf file (name table, id 1; English Windows name first), or null
function sfntFamilyName(buf){
  try {
    const v = new DataView(buf); let off = 0;
    if (v.getUint32(0) === 0x74746366) off = v.getUint32(12);   // collection: first font
    const n = v.getUint16(off + 4);
    for (let i = 0; i < n; i++){
      const r = off + 12 + i * 16;
      if (v.getUint32(r) !== 0x6e616d65) continue;
      const t = v.getUint32(r + 8), cnt = v.getUint16(t + 2), so = t + v.getUint16(t + 4);
      let best = null, score = -1;
      for (let j = 0; j < cnt; j++){
        const e = t + 6 + j * 12, pid = v.getUint16(e), lid = v.getUint16(e + 4), nid = v.getUint16(e + 6), len = v.getUint16(e + 8), o = so + v.getUint16(e + 10);
        if (nid !== 1 && nid !== 16) continue;
        let s = '';
        if (pid === 0 || pid === 3){ for (let k = 0; k + 1 < len; k += 2) s += String.fromCharCode(v.getUint16(o + k)); }
        else if (pid === 1){ for (let k = 0; k < len; k++) s += String.fromCharCode(v.getUint8(o + k)); }
        else continue;
        const sc = (nid === 1 ? 4 : 0) + (pid === 3 ? 1 : 0) + (pid === 3 && lid === 0x409 ? 2 : 0);
        if (s.trim() && sc > score){ score = sc; best = s; }
      }
      return best ? cleanFontName(best) : null;
    }
  } catch (e) { /* not a plain ttf/otf */ }
  return null;
}
function fontIsInstalled(name){   // the text measures differently than every generic fallback
  const c = document.createElement('canvas').getContext('2d'), t = 'אבגדהוזחטיכלמנסעפצקרשת abcdefghijklmnop 0123456789';
  for (const base of ['monospace', 'serif', 'sans-serif']){
    c.font = '40px ' + base; const w0 = c.measureText(t).width;
    c.font = "40px '" + name + "', " + base;
    if (Math.abs(c.measureText(t).width - w0) > 0.5) return true;
  }
  return false;
}
function refreshFontSelects(){
  [fontSelect, baseFontSelect, presetFontSelect].forEach(sel => {
    const keep = sel.value;
    sel.querySelectorAll('optgroup.my-fonts, option.add-font').forEach(n => n.remove());
    if (myFonts.length){
      const g = document.createElement('optgroup'); g.className = 'my-fonts'; g.label = 'הגופנים שלי';
      myFonts.forEach(f => { const o = document.createElement('option'); o.value = myFontValue(f.name); o.textContent = f.name; o.style.fontFamily = o.value; g.appendChild(o); });
      sel.appendChild(g);
    }
    const add = document.createElement('option'); add.className = 'add-font'; add.value = ADD_FONT_VALUE; add.textContent = '➕ הוספת גופן…';
    sel.appendChild(add);
    if ([...sel.options].some(o => o.value === keep)) sel.value = keep;
  });
  // the base list follows the editor's real font (a saved document may use one of my fonts)
  const norm = v => String(v || '').replace(/["']/g, '').replace(/\\s*,\\s*/g, ',').trim().toLowerCase();
  const edEl = document.getElementById('editor');   // (the editor's own variable is declared further down)
  const want = edEl && norm(edEl.style.fontFamily);
  const opt = want && [...baseFontSelect.options].find(o => norm(o.value) === want);
  if (opt) baseFontSelect.value = opt.value;
  [fontSelect, baseFontSelect, presetFontSelect].forEach(sel => { if (sel.value !== ADD_FONT_VALUE) sel.dataset.prev = sel.value; });
}
[fontSelect, baseFontSelect, presetFontSelect].forEach(sel => {
  const remember = () => { if (sel.value !== ADD_FONT_VALUE) sel.dataset.prev = sel.value; };
  sel.addEventListener('focus', remember); sel.addEventListener('pointerdown', remember);
  sel.addEventListener('change', (e) => {   // registered before the list's own handler, so it can stop it
    if (sel.value !== ADD_FONT_VALUE){ sel.dataset.prev = sel.value; return; }
    e.stopImmediatePropagation();
    sel.value = sel.dataset.prev || sel.options[0].value;
    openFontsModal(sel);
  });
});
function mfSay(t, cls){ const el = document.getElementById('mf-msg'); el.textContent = t; el.className = cls || ''; }
function renderMyFontsList(){
  const el = document.getElementById('mf-list'); el.innerHTML = '';
  if (!myFonts.length){ el.innerHTML = '<div class="mf-note" style="margin:0">עוד לא נוספו גופנים.</div>'; return; }
  myFonts.forEach(f => {
    const card = document.createElement('div'); card.className = 'rule-card';
    card.innerHTML = '<button class="del" title="הסרת הגופן">✕</button><span class="rule-name" style="text-decoration:none;"></span>'
      + '<div class="rule-meta"><span></span></div><span class="mf-sample">אבגד הוזח טיכל — שלום עולם</span>';
    card.querySelector('.rule-name').textContent = f.name;
    card.querySelector('.rule-meta span').textContent = f.kind === 'file' ? 'מקובץ · שמור בעורך' : 'מותקן במחשב';
    card.querySelector('.mf-sample').style.fontFamily = myFontValue(f.name);
    card.querySelector('.del').onclick = () => removeMyFont(f.id);
    el.appendChild(card);
  });
}
function afterFontAdded(name){
  myFonts.sort((a, b) => a.name.localeCompare(b.name, 'he'));
  refreshFontSelects(); renderMyFontsList();
  const sel = fontsTargetSelect;
  if (sel){ sel.value = myFontValue(name); sel.dataset.prev = sel.value; sel.dispatchEvent(new Event('change')); }
}
async function addFontFiles(files){
  let added = 0, bad = [];
  for (const file of files){
    try {
      if (file.size > 30 * 1024 * 1024){ bad.push(file.name + ' (גדול מדי)'); continue; }
      const buf = await file.arrayBuffer();
      let name = sfntFamilyName(buf) || cleanFontName(file.name.replace(/\\.[^.]+$/, '').replace(/[-_]+/g, ' '));
      if (!name){ bad.push(file.name); continue; }
      if (FONTS.some(f => f.value.split(',')[0].replace(/'/g, '').trim().toLowerCase() === name.toLowerCase())) name += ' (שלי)';
      const face = new FontFace(name, buf);
      await face.load();
      const old = myFonts.find(f => f.name.toLowerCase() === name.toLowerCase());
      if (old) await removeMyFont(old.id, true);
      const id = 'f' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      try { await myFontsTx('readwrite', st => st.put({ id, name, data: buf, file: file.name })); }
      catch (e) { bad.push(file.name + ' (לא היה מקום לשמור)'); continue; }
      document.fonts.add(face); myFontFaces[id] = face;
      myFonts.push({ id, name, kind: 'file' });
      afterFontAdded(name); added++;
    } catch (e) { bad.push(file.name); }
  }
  if (bad.length) mfSay((added ? '✓ נוסף. ' : '') + 'לא הצלחתי להוסיף: ' + bad.join(', ') + ' — זה לא נראה קובץ גופן תקין.', 'err');
  else if (added) mfSay('✓ ' + (added === 1 ? 'הגופן נוסף' : 'נוספו ' + added + ' גופנים') + ' לרשימות הגופנים.', 'ok');
}
function addLocalFont(raw, checked){
  const name = cleanFontName(raw);
  if (!name){ mfSay('כתבו את שם הגופן.', 'err'); return false; }
  if (myFonts.some(f => f.name.toLowerCase() === name.toLowerCase())){ mfSay('הגופן "' + name + '" כבר ברשימה.', 'err'); return false; }
  if (!checked && !fontIsInstalled(name)){ mfSay('לא מצאתי במחשב גופן בשם "' + name + '". בודקים את האיות בדיוק כמו בוורד.', 'err'); return false; }
  myFonts.push({ id: 'l:' + name, name, kind: 'local' });
  saveLocalFontNames(); afterFontAdded(name);
  mfSay('✓ הגופן "' + name + '" נוסף לרשימות הגופנים.', 'ok');
  return true;
}
async function removeMyFont(id, quiet){
  const f = myFonts.find(x => x.id === id); if (!f) return;
  myFonts = myFonts.filter(x => x.id !== id);
  if (f.kind === 'file'){
    try { await myFontsTx('readwrite', st => st.delete(id)); } catch (e) { /* ignore */ }
    if (myFontFaces[id]){ document.fonts.delete(myFontFaces[id]); delete myFontFaces[id]; }
  } else saveLocalFontNames();
  if (!quiet){ refreshFontSelects(); renderMyFontsList(); renderLocalFontList(); mfSay('הגופן "' + f.name + '" הוסר מהרשימות.', 'ok'); }
}
let localFamilies = null;
function renderLocalFontList(){
  const box = document.getElementById('mf-local-list'); if (!localFamilies) return;
  const q = document.getElementById('mf-local-search').value.trim().toLowerCase();
  const list = localFamilies.filter(n => !q || n.toLowerCase().includes(q)).slice(0, 400);
  box.innerHTML = '';
  if (!list.length){ box.innerHTML = '<div class="mf-note" style="padding:6px 10px; margin:0">לא נמצא גופן כזה.</div>'; return; }
  list.forEach(n => {
    const b = document.createElement('button'); b.type = 'button';
    const added = myFonts.some(f => f.name.toLowerCase() === n.toLowerCase());
    const s1 = document.createElement('span'); s1.textContent = 'אבגד שלום'; s1.style.fontFamily = myFontValue(n);
    const s2 = document.createElement('span'); s2.className = 'mf-fam' + (added ? ' mf-added' : ''); s2.textContent = n + (added ? ' ✓' : '');
    b.append(s2, s1);
    b.onclick = () => { if (addLocalFont(n, true)) renderLocalFontList(); };
    box.appendChild(b);
  });
}
async function showLocalFonts(){
  try {
    const fonts = await window.queryLocalFonts();
    localFamilies = [...new Set(fonts.map(f => cleanFontName(f.family)).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'he'));
    if (!localFamilies.length){ mfSay('הדפדפן לא החזיר את רשימת הגופנים. אפשר לכתוב את שם הגופן למטה.', 'err'); return; }
    document.getElementById('mf-local-wrap').hidden = false; document.getElementById('mf-local-btn').hidden = true;
    renderLocalFontList(); document.getElementById('mf-local-search').focus(); mfSay('');
  } catch (e) {
    mfSay('אין הרשאה לרשימת הגופנים שבמחשב. אפשר לכתוב את שם הגופן למטה.', 'err');
  }
}
function openFontsModal(sel){
  fontsTargetSelect = sel || null;
  mfSay(''); renderMyFontsList();
  document.getElementById('mf-local-btn').hidden = !(typeof window.queryLocalFonts === 'function') || !!localFamilies;
  document.getElementById('fonts-modal').removeAttribute('hidden');
}
function closeFontsModal(){ document.getElementById('fonts-modal').setAttribute('hidden', ''); fontsTargetSelect = null; }
document.getElementById('fonts-close').onclick = closeFontsModal;
document.getElementById('fonts-modal').addEventListener('click', (e) => { if (e.target.id === 'fonts-modal') closeFontsModal(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !document.getElementById('fonts-modal').hasAttribute('hidden')){ e.preventDefault(); e.stopPropagation(); closeFontsModal(); } });
document.getElementById('mf-file-btn').onclick = () => document.getElementById('mf-file').click();
document.getElementById('mf-file').onchange = async (e) => { const files = [...e.target.files]; e.target.value = ''; if (files.length){ mfSay('טוען…'); await addFontFiles(files); } };
document.getElementById('mf-local-btn').onclick = showLocalFonts;
document.getElementById('mf-local-search').oninput = renderLocalFontList;
document.getElementById('mf-name-btn').onclick = () => { const i = document.getElementById('mf-name'); if (addLocalFont(i.value)) i.value = ''; };
document.getElementById('mf-name').addEventListener('keydown', (e) => { if (e.key === 'Enter'){ e.preventDefault(); document.getElementById('mf-name-btn').click(); } });
refreshFontSelects();
(async function loadMyFonts(){
  myFonts = loadLocalFontNames().map(name => ({ id: 'l:' + name, name, kind: 'local' }));
  try {
    const rows = await myFontsTx('readonly', st => st.getAll()) || [];
    for (const r of rows){
      try { const face = new FontFace(r.name, r.data); await face.load(); document.fonts.add(face); myFontFaces[r.id] = face; myFonts.push({ id: r.id, name: r.name, kind: 'file' }); }
      catch (e) { console.warn('font file could not be loaded:', r.name, e); }
    }
  } catch (e) { /* storage not available: only installed fonts */ }
  myFonts.sort((a, b) => a.name.localeCompare(b.name, 'he'));
  if (myFonts.length) refreshFontSelects();
})();
""")

step('טעינת מסמך: גם גופן שלי',
"""    const opt = [...baseFontSelect.options].find(o => norm(o.value) === want);
    baseFontSelect.value = opt ? opt.value : editor.style.fontFamily;""",
"""    const opt = [...baseFontSelect.options].find(o => norm(o.value) === want && o.value !== '__add_font__');
    baseFontSelect.value = opt ? opt.value : editor.style.fontFamily;""")

MARK = "const MYFONTS_DB = 'heb-style-editor-fonts'"
NEED = None
