# ד-1: "תיקוני הכתבה" — a personal list of words that voice typing writes wrong ("שולחן ארוך" → "שולחן ערוך").
# Applied to every dictated chunk (online and offline), before spoken punctuation and AI punctuation.
# A Hebrew word also matches with ו/ה/ב/כ/ל/מ/ש in front (for words of 3+ letters). One pass, so fixes never chain.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('עיצוב החלון',
r"""  #dict-punct-note{ font-size:12px; color: var(--parchment-dim); margin:2px 0 0 0; padding-inline-start:26px; }""",
r"""  #dict-punct-note{ font-size:12px; color: var(--parchment-dim); margin:2px 0 0 0; padding-inline-start:26px; }
  /* ד-1: תיקוני הכתבה */
  .dfix-box{ max-width:470px; }
  .dfix-row{ display:flex; gap:6px; align-items:flex-end; }
  .dfix-row label{ flex:1; min-width:0; display:flex; flex-direction:column; gap:3px; font-size:12px; color: var(--parchment-dim); }
  .dfix-row input{ width:100%; box-sizing:border-box; padding:7px 10px; border-radius:4px; border:1px solid var(--line); background: var(--panel-2);
    color: var(--parchment); font-family:'Rubik', sans-serif; font-size:14px; }
  .dfix-row input:focus{ outline:none; border-color: var(--brass); }
  .dfix-arrow{ padding:0 0 8px; color: var(--brass-bright); font-size:15px; }
  #dfix-add{ height:34px; padding:0 14px; border-radius:4px; border:1px solid var(--brass); background: var(--brass); color:#1a1608;
    font-family:'Rubik', sans-serif; font-size:13px; font-weight:600; cursor:pointer; white-space:nowrap; }
  #dfix-add:hover:not(:disabled){ background: var(--brass-bright); }
  #dfix-add:disabled{ opacity:.4; cursor:default; }
  #dfix-msg{ font-size:12.5px; min-height:1.3em; margin:6px 0 4px; color: var(--parchment-dim); line-height:1.5; }
  #dfix-msg.ok{ color:#7fbf7f; }
  #dfix-msg.err{ color:#e0786a; }
  #dfix-msg button{ background:none; border:none; color: var(--brass-bright); cursor:pointer; font-family:'Rubik', sans-serif;
    font-size:12.5px; text-decoration:underline; padding:0 4px; }
  #dfix-list{ border:1px solid var(--line); border-radius:4px; max-height:min(300px, calc(40vh / var(--uiz, 1))); overflow-y:auto; flex:0 1 auto; min-height:64px; }
  #dfix-modal .modal-body{ display:flex; flex-direction:column; min-height:0; }
  #dfix-modal .modal-body > *{ flex:none; }
  #dfix-modal #dfix-list{ flex:0 1 auto; }
  .dfix-pair{ flex:1; min-width:0; cursor:pointer; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .dfix-pair .dfix-from{ color: var(--parchment-dim); }
  .dfix-pair .dfix-sep{ color: var(--brass-bright); padding:0 6px; }
  .dfix-pair .dfix-none{ color: var(--parchment-dim); font-style:italic; font-size:13px; }""")

step('כפתור בחלון ההגדרות',
r"""      <div id="dict-punct-note" hidden></div>""",
r"""      <div id="dict-punct-note" hidden></div>
      <button type="button" class="folder-install-btn" id="dfix-open" title="מילים שההכתבה כותבת לא נכון — יתוקנו מעצמן">🔁 תיקוני הכתבה</button>""")

step('החלון',
r"""<input type="file" id="udict-file" accept=".txt,text/plain" hidden>""",
r"""<input type="file" id="udict-file" accept=".txt,text/plain" hidden>
<div id="dfix-modal" class="modal-overlay" hidden>
  <div class="modal-box udict-box dfix-box" role="dialog" aria-labelledby="dfix-title">
    <div class="modal-head">
      <h2 id="dfix-title">🔁 תיקוני הכתבה</h2>
      <button id="dfix-close" title="סגירה (Esc)">✕</button>
    </div>
    <div class="modal-body">
      <p class="udict-sub" id="dfix-count"></p>
      <div class="dfix-row">
        <label>ההכתבה כותבת<input id="dfix-from" type="text" dir="rtl" autocomplete="off" spellcheck="false" placeholder="למשל: שולחן ארוך"></label>
        <span class="dfix-arrow" aria-hidden="true">←</span>
        <label>צריך להיות<input id="dfix-to" type="text" dir="rtl" autocomplete="off" spellcheck="false" placeholder="שולחן ערוך"></label>
        <button id="dfix-add" type="button" disabled>➕ הוסף</button>
      </div>
      <div id="dfix-msg" aria-live="polite"></div>
      <div id="dfix-list"></div>
      <div class="udict-foot">
        <button id="dfix-export" type="button">⬇ ייצוא לקובץ</button>
        <button id="dfix-import" type="button">⬆ ייבוא מקובץ</button>
      </div>
    </div>
  </div>
</div>
<input type="file" id="dfix-file" accept=".txt,text/plain" hidden>""")

step('ייבוא נתונים: מיזוג התיקונים',
r"""      } else if (k === K.first){
        const a = parseInt(cur, 10), b = parseInt(v, 10);""",
r"""      } else if (k === PREFIX + 'dict-fix-v1'){   // ד-1: the two lists join; a word already here keeps its fix
        const mine = parseJSON(cur, []), theirs = parseJSON(v, []);
        if (!Array.isArray(theirs)) return;
        const list = Array.isArray(mine) ? mine.filter(p => Array.isArray(p) && typeof p[0] === 'string') : [];
        let added = 0;
        theirs.forEach(p => {
          if (Array.isArray(p) && typeof p[0] === 'string' && typeof p[1] === 'string' && p[0] && !list.some(q => q[0] === p[0])){ list.push([p[0], p[1]]); added++; }
        });
        if (added){ writes[k] = JSON.stringify(list); info.fixAdd = added; }
      } else if (k === K.first){
        const a = parseInt(cur, 10), b = parseInt(v, 10);""")

step('ייבוא נתונים: שורת סיכום',
r"""    if (i.dictAdd) lines.push('• ' + num(i.dictAdd, 'מילה אחת', 'מילים') + ' ל"המילון שלי"');""",
r"""    if (i.dictAdd) lines.push('• ' + num(i.dictAdd, 'מילה אחת', 'מילים') + ' ל"המילון שלי"');
    if (i.fixAdd) lines.push('• ' + num(i.fixAdd, 'תיקון הכתבה אחד', 'תיקוני הכתבה'));""")

step('תפריט האיות',
r"""    menu.appendChild(item('', '📖 המילון שלי', n ? (n === 1 ? 'מילה אחת שהוספת' : n + ' מילים שהוספת') : 'עדיין ריק', () => UserDictWindow.open()));""",
r"""    menu.appendChild(item('', '📖 המילון שלי', n ? (n === 1 ? 'מילה אחת שהוספת' : n + ' מילים שהוספת') : 'עדיין ריק', () => UserDictWindow.open()));
    if (window.DictFix){   // ד-1
      const f = DictFix.count();
      menu.appendChild(item('', '🔁 תיקוני הכתבה', f ? (f === 1 ? 'תיקון אחד' : f + ' תיקונים') + ' למילים שההכתבה כותבת לא נכון' : 'מילים שההכתבה כותבת לא נכון', () => DictFix.open()));
    }""")

step('המודול',
r"""
function openSpellCredits(){""",
r"""
// ---------- ד-1: dictation fixes — words voice typing writes wrong are replaced as they arrive ----------
var DictFix = window.DictFix = (function(){
  const KEY = 'heb-style-editor-dict-fix-v1', MAX = 3000;
  const WORDCH = '\\u0591-\\u05C7\\u05D0-\\u05EAA-Za-z0-9';
  let pairs = [], rules = [];
  function clean(s){ return String(s || '').replace(/[֑-ׇ]/g, '').replace(/\s+/g, ' ').trim().replace(/^[,.;:!?]+|[,.;:!?]+$/g, '').trim(); }
  function cleanTo(s){ return String(s || '').replace(/\s+/g, ' ').trim(); }
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  function ruleOf(from, to){
    const f = clean(from);
    const letters = (f.match(/[א-ת]/g) || []).length;
    // a Hebrew word may come with ו/ה/ב/כ/ל/מ/ש in front ("ושולחן ארוך"); short words only on their own
    const pre = /^[א-ת]/.test(f) && letters >= 3 ? '([ובכלמשה]{0,2})' : '()';
    return { len: f.length, to: to, re: new RegExp('(?<![' + WORDCH + '])' + pre + f.split(' ').map(esc).join('[ \\t]+') + '(?![' + WORDCH + '])', 'g') };
  }
  function build(){ rules = pairs.map(p => ruleOf(p[0], p[1])).sort((a, b) => b.len - a.len); }
  function load(){
    let a = [];
    try { a = JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { a = []; }
    pairs = Array.isArray(a) ? a.filter(p => Array.isArray(p) && typeof p[0] === 'string' && typeof p[1] === 'string' && clean(p[0])) : [];
    build();
  }
  function save(){ build(); try { localStorage.setItem(KEY, JSON.stringify(pairs)); return true; } catch (e) { return false; } }
  // one pass: each fix is parked as a private character, so one fix's result is never fixed again by another
  function fix(text, list){
    if (!text || !list.length) return text;
    const outs = [];
    let s = text;
    for (const r of list){
      r.re.lastIndex = 0;
      s = s.replace(r.re, (m, p) => { if (outs.length >= 6000) return m; outs.push(p + r.to); return String.fromCharCode(0xE200 + outs.length - 1); });
    }
    return outs.length ? s.replace(/[-]/g, c => outs[c.charCodeAt(0) - 0xE200]) : text;
  }
  function apply(text){ return fix(text, rules); }

  // ---- fixing what is already in the document (offered right after a fix is added) ----
  function hitsIn(text, from, to){
    const r = ruleOf(from, to), out = [];
    let m;
    r.re.lastIndex = 0;
    while ((m = r.re.exec(text))){ const s = m.index + m[1].length; out.push({ s, e: m.index + m[0].length }); if (!m[0].length) r.re.lastIndex++; }
    return out;
  }
  function countInDoc(from, to){ try { return hitsIn(extractPlainText(editor), from, to).length; } catch (e) { return 0; } }
  function fixInDoc(from, to){
    const text = extractPlainText(editor), hits = hitsIn(text, from, to);
    if (!hits.length) return 0;
    flushPendingHistory();
    const map = new Array(text.length + 1);
    let newText = '', last = 0, delta = 0;
    for (const h of hits){
      for (let k = last; k < h.s; k++) map[k] = k + delta;
      newText += text.slice(last, h.s) + to;
      for (let k = h.s; k < h.e; k++) map[k] = h.s + delta + Math.min(k - h.s, to.length);
      delta += to.length - (h.e - h.s);
      last = h.e;
    }
    for (let k = last; k <= text.length; k++) map[k] = k + delta;
    newText += text.slice(last);
    const caret = map[Math.min(getSelectionOffsets(editor).start, text.length)] || 0;
    manualStyles = remapRangesByMap(manualStyles, map);
    boldOverrides = remapRangesByMap(boldOverrides, map);
    italicOverrides = remapRangesByMap(italicOverrides, map);
    underlineOverrides = remapRangesByMap(underlineOverrides, map);
    renderTextIntoEditor(newText, caret);
    pushHistory(true);   // one undo step
    return hits.length;
  }

  // ---- the window ----
  const $ = id => document.getElementById(id);
  const modal = $('dfix-modal');
  const fromIn = $('dfix-from'), toIn = $('dfix-to'), addBtn = $('dfix-add'), msg = $('dfix-msg'), list = $('dfix-list'), count = $('dfix-count'), fileIn = $('dfix-file');
  const collator = (typeof Intl !== 'undefined' && Intl.Collator) ? new Intl.Collator('he') : null;
  let lastDeleted = null;
  function setMsg(text, kind, btnText, onBtn){
    if (!msg) return;
    msg.textContent = text || '';
    msg.className = kind || '';
    if (btnText){
      const b = document.createElement('button');
      b.type = 'button'; b.textContent = btnText; b.onclick = onBtn;
      msg.appendChild(b);
    }
  }
  function updateOpenBtn(){
    const b = $('dfix-open');
    if (b) b.textContent = '🔁 תיקוני הכתבה' + (pairs.length ? ' (' + pairs.length + ')' : '');
  }
  function bdi(text, cls){ const e = document.createElement('bdi'); e.className = cls; e.textContent = text; return e; }
  function render(){
    if (!modal) return;
    const n = pairs.length;
    count.textContent = n
      ? (n === 1 ? 'תיקון אחד' : n + ' תיקונים') + '. כל מה שמוכתב, באינטרנט ובאופליין, מתוקן לפי הרשימה. לחיצה על שורה מאפשרת לשנות אותה.'
      : 'כשההכתבה כותבת מילה לא נכון, רושמים כאן מה נכתב ומה צריך להיות — ומעכשיו זה יתוקן מעצמו, בשתי ההקלדות הקוליות. אם בחרתם מילה במסמך לפני שפתחתם, היא כבר מופיעה כאן.';
    list.textContent = '';
    const q = clean(fromIn.value);
    const all = pairs.slice().sort((a, b) => collator ? collator.compare(a[0], b[0]) : (a[0] < b[0] ? -1 : 1));
    const shown = q ? all.filter(p => p[0].includes(q) || p[1].includes(q)) : all;
    if (!shown.length){
      const e = document.createElement('div'); e.className = 'udict-empty';
      e.textContent = n ? 'אין תיקון שמתאים לחיפוש' : 'הרשימה עדיין ריקה';
      list.appendChild(e);
    }
    for (const p of shown){
      const row = document.createElement('div'); row.className = 'udict-row';
      const pair = document.createElement('span'); pair.className = 'dfix-pair'; pair.title = 'לשינוי';
      pair.appendChild(bdi(p[0], 'dfix-from'));
      const sep = document.createElement('span'); sep.className = 'dfix-sep'; sep.textContent = '←'; pair.appendChild(sep);
      pair.appendChild(p[1] ? bdi(p[1], 'dfix-to') : bdi('(נמחק)', 'dfix-none'));
      pair.onclick = () => { fromIn.value = p[0]; toIn.value = p[1]; refreshAdd(); toIn.focus(); toIn.select(); };
      const del = document.createElement('button'); del.type = 'button'; del.textContent = '✕'; del.title = 'מחיקה';
      del.onclick = () => remove(p[0]);
      row.appendChild(pair); row.appendChild(del);
      list.appendChild(row);
    }
    $('dfix-export').disabled = !n;
    updateOpenBtn();
  }
  function refreshAdd(){ if (addBtn) addBtn.disabled = !clean(fromIn.value); }
  function add(){
    const from = clean(fromIn.value), to = cleanTo(toIn.value);
    if (!from) return;
    if (to === from){ setMsg('"צריך להיות" זהה למה שנכתב — אין מה לתקן', 'err'); return; }
    if (pairs.length >= MAX && !pairs.some(p => p[0] === from)){ setMsg('הרשימה מלאה (' + MAX + ' תיקונים)', 'err'); return; }
    const i = pairs.findIndex(p => p[0] === from), was = i >= 0;
    if (was) pairs[i] = [from, to]; else pairs.push([from, to]);
    if (!save()){ setMsg('השמירה נכשלה — אין מספיק מקום בדפדפן', 'err'); return; }
    fromIn.value = ''; toIn.value = ''; refreshAdd();
    render();
    const head = '"' + from + '" ← ' + (to ? '"' + to + '"' : 'יימחק') + (was ? ' — עודכן.' : ' — נוסף.');
    const inDoc = countInDoc(from, to);
    if (inDoc) setMsg(head + ' במסמך יש ' + (inDoc === 1 ? 'מקום אחד' : inDoc + ' מקומות') + ' כאלה.', 'ok',
      inDoc === 1 ? 'לתקן גם אותו' : 'לתקן גם אותם', () => {
        const k = fixInDoc(from, to);
        setMsg(k ? (k === 1 ? 'תוקן מקום אחד במסמך' : 'תוקנו ' + k + ' מקומות במסמך') + ' (Ctrl+Z מבטל)' : 'הטקסט השתנה — לא נמצא מה לתקן', k ? 'ok' : '');
      });
    else setMsg(head + ' מההכתבה הבאה זה יתוקן מעצמו.', 'ok');
    fromIn.focus();
  }
  function remove(from){
    const i = pairs.findIndex(p => p[0] === from);
    if (i < 0) return;
    lastDeleted = pairs[i];
    pairs.splice(i, 1); save(); render();
    setMsg('"' + from + '" נמחק מהרשימה.', '', 'ביטול', () => {
      if (lastDeleted && !pairs.some(p => p[0] === lastDeleted[0])){ pairs.push(lastDeleted); save(); }
      lastDeleted = null; render(); setMsg('הוחזר לרשימה', 'ok');
    });
  }
  function exportFile(){
    if (!pairs.length) return;
    const lines = pairs.map(p => p[0] + ' → ' + p[1]);
    const blob = new Blob(['﻿' + lines.join('\r\n') + '\r\n'], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'תיקוני הכתבה.txt';
    a.style.display = 'none';
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
    setMsg('נשמר הקובץ "תיקוני הכתבה.txt" (' + pairs.length + ' תיקונים) בתיקיית ההורדות', 'ok');
  }
  async function importFile(file){
    if (!file) return;
    let text = '';
    try {
      const buf = await file.arrayBuffer();
      text = new TextDecoder('utf-8').decode(buf);
      if (text.includes('�')){ try { text = new TextDecoder('windows-1255').decode(buf); } catch (e) { /* keep utf-8 */ } }
    } catch (e) { setMsg('לא ניתן לקרוא את הקובץ', 'err'); return; }
    let added = 0, upd = 0, bad = 0;
    text.replace(/^﻿/, '').split(/\r?\n/).forEach(line => {
      if (!line.trim()) return;
      const m = line.match(/^(.*?)\s*(?:→|->|=>|=|←|\t)\s*(.*)$/);
      const from = m ? clean(m[1]) : '', to = m ? cleanTo(m[2]) : '';
      if (!from || to === from){ bad++; return; }
      const i = pairs.findIndex(p => p[0] === from);
      if (i >= 0){ if (pairs[i][1] !== to){ pairs[i] = [from, to]; upd++; } }
      else if (pairs.length < MAX){ pairs.push([from, to]); added++; }
      else bad++;
    });
    if (added || upd) save();
    render();
    if (!added && !upd && bad){ setMsg('לא נמצאו בקובץ תיקונים. כל שורה צריכה להיות: מה שנכתב → מה שצריך להיות', 'err'); return; }
    let s = added ? (added === 1 ? 'נוסף תיקון אחד' : 'נוספו ' + added + ' תיקונים') : 'לא נוספו תיקונים חדשים';
    if (upd) s += upd === 1 ? ', אחד עודכן' : ', ' + upd + ' עודכנו';
    if (bad) s += bad === 1 ? ', שורה אחת לא תקינה דולגה' : ', ' + bad + ' שורות לא תקינות דולגו';
    setMsg(s, (added || upd) ? 'ok' : '');
  }
  function selectedWord(){
    try {
      const sel = window.getSelection();
      if (!sel || !sel.rangeCount || !editor.contains(sel.anchorNode)) return '';
      const t = sel.toString();
      return (t && t.length <= 60 && !/\n/.test(t)) ? clean(t) : '';
    } catch (e) { return ''; }
  }
  function open(){
    if (!modal) return;
    const w = selectedWord();
    lastDeleted = null;
    fromIn.value = w; toIn.value = '';
    const i = w ? pairs.findIndex(p => p[0] === w) : -1;
    if (i >= 0) toIn.value = pairs[i][1];
    setMsg('', '');
    refreshAdd(); render();
    modal.removeAttribute('hidden');
    (w ? toIn : fromIn).focus();
  }
  function close(){ if (modal) modal.setAttribute('hidden', ''); }

  load();
  if (modal){
    fromIn.addEventListener('input', () => { refreshAdd(); if (msg.className === 'err') setMsg('', ''); render(); });
    toIn.addEventListener('input', () => { if (msg.className === 'err') setMsg('', ''); });
    const onEnter = (e) => { if (e.key === 'Enter'){ e.preventDefault(); e.stopPropagation(); if (e.target === fromIn && !toIn.value) toIn.focus(); else add(); } };
    fromIn.addEventListener('keydown', onEnter); toIn.addEventListener('keydown', onEnter);
    addBtn.onclick = add;
    $('dfix-close').onclick = close;
    $('dfix-export').onclick = exportFile;
    $('dfix-import').onclick = () => { fileIn.value = ''; fileIn.click(); };
    fileIn.addEventListener('change', () => importFile(fileIn.files && fileIn.files[0]));
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
    document.addEventListener('keydown', (e) => {   // capture: only this window closes, not the settings window under it
      if (e.key === 'Escape' && !modal.hasAttribute('hidden')){ e.preventDefault(); e.stopImmediatePropagation(); close(); }
    }, true);
    const ob = $('dfix-open');
    if (ob){ ob.addEventListener('mousedown', (e) => e.preventDefault()); ob.onclick = open; }
    updateOpenBtn();
    window.addEventListener('storage', (e) => { if (e.key === KEY){ load(); render(); } });   // another tab changed the list
  }
  return { apply, open, close, count: () => pairs.length, _fixInDoc: fixInDoc, _import: importFile };
})();

function openSpellCredits(){""")

step('החלה על כל הכתבה',
r"""function spliceDictation(text, base, oldLen, rawChunk){
  const chunk = applySpokenPunctuation(rawChunk);""",
r"""function spliceDictation(text, base, oldLen, rawChunk){
  if (window.DictFix) rawChunk = DictFix.apply(rawChunk);   // ד-1: words voice typing writes wrong
  const chunk = applySpokenPunctuation(rawChunk);""")

step('מדריך',
r"""      { n: 'פקודות פיסוק בדיבור', s: '#tb-offline-settings',""",
r"""      { n: '🔁 תיקוני הכתבה', s: '#tb-offline-settings', d: 'מילים שההכתבה כותבת לא נכון מתוקנות מעצמן. בחלון ⚙️ (או בתפריט שליד ✓ איות): רושמים מה נכתב ומה צריך להיות — למשל "שולחן ארוך" ← "שולחן ערוך". זה פועל בשתי ההקלדות הקוליות, וגם כשיש ו/ה/ב/כ/ל/מ/ש לפני המילה. אם המילה כבר במסמך, אפשר לתקן גם שם בלחיצה. כדאי לבחור את המילה השגויה במסמך לפני שפותחים — היא תופיע בחלון מעצמה.' },
      { n: 'פקודות פיסוק בדיבור', s: '#tb-offline-settings',""")

MARK = "// ---------- ד-1: dictation fixes"
NEED = {'mark': "// ---------- א-1: the files live in IndexedDB", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
