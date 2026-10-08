# ק-1: read the text aloud with the voices already on the computer (Windows "Asaf", Edge's natural voices).
# 🔊 reads the selection, or from the caret on; the sentence being read is highlighted; ⚙️ picks voice and speed.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

SPK = ('<svg class="tts-ico ico-idle" viewBox="0 0 24 20" aria-hidden="true"><path d="M3 7.5h3.5L11 3.5v13L6.5 12.5H3z"/>'
       '<path class="tw" d="M14.5 7a4 4 0 0 1 0 6"/><path class="tw" d="M17.5 4.5a8 8 0 0 1 0 11"/></svg>'
       '<svg class="tts-ico ico-stop" viewBox="0 0 24 20" aria-hidden="true"><rect x="7" y="5" width="10" height="10" rx="1.8"/></svg>')

step('כפתורים בסרגל',
"""  <div class="tb-group tb-mode">
    <button class="tb-btn wide text-mode-btn" id="tb-text-mode\"""",
"""  <div class="tb-group tb-tts-grp">
    <button class="tb-btn tts-btn" id="tb-tts" type="button" title="הקראת הטקסט — המסומן, או מהסמן והלאה" aria-label="הקראת הטקסט">""" + SPK + """</button>
    <button class="info-btn" id="tb-tts-settings" type="button" title="הגדרות הקראה — קול ומהירות">⚙️</button>
  </div>
  <div class="tb-group tb-mode">
    <button class="tb-btn wide text-mode-btn" id="tb-text-mode\"""")

step('חלון הגדרות הקראה',
"""<div id="offline-modal" class="modal-overlay" hidden>""",
"""<div id="tts-modal" class="modal-overlay" hidden>
  <div class="modal-box" style="max-width:440px;">
    <div class="modal-head">
      <h2>🔊 הגדרות הקראה</h2>
      <button id="tts-close" aria-label="סגירה">✕</button>
    </div>
    <div class="modal-body">
      <div class="field">
        <label for="tts-voice">קול</label>
        <select id="tts-voice"></select>
        <label class="tts-all"><input type="checkbox" id="tts-all-voices"> להציג גם קולות בשפות אחרות</label>
      </div>
      <div class="field">
        <label for="tts-rate">מהירות: <span id="tts-rate-val"></span></label>
        <input type="range" id="tts-rate" min="0.6" max="1.8" step="0.1">
      </div>
      <button type="button" class="folder-install-btn" id="tts-test">▶ השמע דוגמה</button>
      <div id="tts-msg" role="status" aria-live="polite"></div>
      <div class="tts-help" id="tts-help">
        <b>אין קול עברי ברשימה?</b> ב-Windows: הגדרות ← זמן ושפה ← דיבור ← "הוסף קולות" ← עברית.
        אחרי ההתקנה סוגרים את הדפדפן לגמרי ופותחים מחדש. אם הקול עדיין לא מופיע בכרום, הוא כן יופיע באדג'.
        באדג' יש גם קולות עבריים טבעיים ("Avri", "Hila") שעובדים עם אינטרנט.
      </div>
    </div>
  </div>
</div>

<div id="offline-modal" class="modal-overlay" hidden>""")

step('עיצוב',
"""  .ov-measure-tip{""",
"""  /* ק-1: read aloud */
  .tts-btn{ display:inline-flex; align-items:center; justify-content:center; min-width:34px; }
  .tts-btn .tts-ico{ width:21px; height:18px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
  .tts-btn .tts-ico .tw{ opacity:.85; }
  .tts-btn .ico-idle path:first-child{ fill:currentColor; fill-opacity:.18; }
  .tts-btn .ico-stop{ display:none; fill:currentColor; stroke:none; }
  #toolbar .tb-btn.tts-btn.speaking:not(:disabled), .tts-btn.speaking{ background: var(--danger); border-color: var(--danger); color:#fff; }
  .tts-btn.speaking .ico-idle{ display:none; }
  .tts-btn.speaking .ico-stop{ display:block; }
  ::highlight(tts-current){ background-color: rgba(216,167,82,.38); }
  #tts-modal select, #tts-modal input[type=range]{ width:100%; }
  #tts-modal input[type=range]{ accent-color: var(--brass); }
  #tts-modal .tts-all{ display:flex; align-items:center; gap:6px; margin-top:6px; font-size:12.5px; color: var(--parchment-dim); cursor:pointer; }
  #tts-modal .tts-all input{ width:auto; margin:0; }
  #tts-msg{ min-height:20px; font-size:13px; font-weight:600; margin-top:8px; }
  #tts-msg.err{ color: var(--danger, #c0533f); } #tts-msg.ok{ color:#5f9a63; }
  .tts-help{ font-size:12.5px; line-height:1.7; color: var(--parchment-dim); margin-top:10px; padding:8px 10px; border:1px dashed var(--line); border-radius:4px; }
  .tts-help b{ color: var(--parchment); }
  .ov-measure-tip{""")

step('מנוע ההקראה',
"""// ---------- Footer actions ----------""",
"""// ---------- ק-1: read aloud (speechSynthesis — the computer's / browser's own voices) ----------
const TTS = (function(){
  const KEY = 'heb-style-editor-tts-v1', synth = window.speechSynthesis;
  const btn = document.getElementById('tb-tts'), modal = document.getElementById('tts-modal');
  const voiceSel = document.getElementById('tts-voice'), allBox = document.getElementById('tts-all-voices');
  const rateIn = document.getElementById('tts-rate'), rateVal = document.getElementById('tts-rate-val');
  let prefs = { voice: '', rate: 1, all: false };
  try { Object.assign(prefs, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) { /* ignore */ }
  const savePrefs = () => { try { localStorage.setItem(KEY, JSON.stringify(prefs)); } catch (e) { /* ignore */ } };
  let run = 0, speaking = false;
  const isHe = (v) => /^(he|iw)\\b/i.test(v.lang || '') || /hebrew|עברית/i.test(v.name || '');
  const score = (v) => (isHe(v) ? 100 : 0) + (/natural|online|neural/i.test(v.name) ? 10 : 0) + (v.localService ? 1 : 0);
  function voices(){ return synth ? synth.getVoices() : []; }
  function pickVoice(){
    const vs = voices();
    const saved = prefs.voice && vs.find(v => v.voiceURI === prefs.voice);
    if (saved) return saved;
    const he = vs.filter(isHe).sort((a, b) => score(b) - score(a));
    return he[0] || null;
  }
  function fillVoices(){
    const vs = voices(), cur = pickVoice();
    const list = vs.filter(v => prefs.all || isHe(v)).sort((a, b) => score(b) - score(a) || a.name.localeCompare(b.name));
    voiceSel.innerHTML = '';
    if (!list.length){
      const o = document.createElement('option'); o.value = ''; o.textContent = vs.length ? 'אין במחשב קול עברי' : 'הדפדפן לא מצא קולות'; voiceSel.appendChild(o);
    }
    list.forEach(v => {
      const o = document.createElement('option'); o.value = v.voiceURI;
      o.textContent = v.name.replace(/^Microsoft\\s+/, '').replace(/\\s*-\\s*Hebrew \\(Israel\\)/, '') + (v.localService ? '' : ' · דרך האינטרנט');
      voiceSel.appendChild(o);
    });
    if (cur && list.includes(cur)) voiceSel.value = cur.voiceURI;
    document.getElementById('tts-help').hidden = vs.some(isHe);
  }
  function say(t, cls){ const m = document.getElementById('tts-msg'); m.textContent = t; m.className = cls || ''; }
  function setRateText(){ rateVal.textContent = (Math.round(prefs.rate * 10) / 10).toFixed(1).replace('.0', '') + '×'; }
  // sentences of the text, with their offsets in the editor's plain text
  function chunks(text, start, end){
    const out = [], re = /[^.!?\\n]*[.!?]+["'״׳)\\]]*|[^.!?\\n]+/g;
    const part = text.slice(start, end);
    let m;
    while ((m = re.exec(part))){
      let s = m.index, e = s + m[0].length;
      while (s < e && /\\s/.test(part[s])) s++;
      while (e > s && /\\s/.test(part[e - 1])) e--;
      if (e <= s || !/[\\p{L}\\p{N}]/u.test(part.slice(s, e))) continue;
      // very long sentences: cut at a comma or a space, so the browser never drops the end
      while (e - s > 220){
        const slice = part.slice(s, s + 220);
        let cut = Math.max(slice.lastIndexOf(','), slice.lastIndexOf('،'));
        if (cut < 80) cut = slice.lastIndexOf(' ');
        if (cut < 40) cut = 220;
        out.push({ s: start + s, e: start + s + cut + 1 });
        s += cut + 1; while (s < e && /\\s/.test(part[s])) s++;
      }
      if (e > s) out.push({ s: start + s, e: start + e });
    }
    return out;
  }
  function highlight(c){
    if (!(window.CSS && CSS.highlights && window.Highlight)) return;
    if (!c){ CSS.highlights.delete('tts-current'); return; }
    try {
      const a = resolveOffsetPoint(editor, c.s), b = resolveOffsetPoint(editor, c.e), r = document.createRange();
      r.setStart(a.node, a.offset); r.setEnd(b.node, b.offset);
      CSS.highlights.set('tts-current', new Highlight(r));
      const rect = r.getBoundingClientRect();
      if (rect.height && (rect.top < 80 || rect.bottom > window.innerHeight - 40)) (a.node.nodeType === 1 ? a.node : a.node.parentElement).scrollIntoView({ block: 'center', behavior: 'smooth' });
    } catch (e) { /* the text changed under us */ }
  }
  function setState(on){
    speaking = on;
    btn.classList.toggle('speaking', on);
    btn.title = on ? 'ההקראה פעילה — לחיצה עוצרת' : 'הקראת הטקסט — המסומן, או מהסמן והלאה';
    btn.setAttribute('aria-label', on ? 'עצירת ההקראה' : 'הקראת הטקסט');
    if (!on) highlight(null);
  }
  function stop(){ run++; if (synth) synth.cancel(); setState(false); }
  function speakList(list, i, myRun, onEnd){
    if (myRun !== run) return;
    if (i >= list.length){ setState(false); if (onEnd) onEnd(); return; }
    const c = list[i], u = new SpeechSynthesisUtterance(c.text);
    const v = pickVoice(); if (v){ u.voice = v; u.lang = v.lang; } else u.lang = 'he-IL';
    u.rate = prefs.rate;
    u.onstart = () => { if (myRun === run && c.s != null) highlight(c); };
    u.onend = () => speakList(list, i + 1, myRun, onEnd);
    u.onerror = (e) => { if (myRun !== run) return; if (e.error === 'interrupted' || e.error === 'canceled') return; setState(false); flashStatus('ההקראה נעצרה: הקול לא זמין. בחרו קול אחר ב-⚙️ הגדרות הקראה.'); };
    synth.speak(u);
  }
  function start(){
    if (!synth){ flashStatus('הדפדפן הזה לא תומך בהקראה.'); return; }
    const text = extractPlainText(editor).replace(/\\uE000[^\\uE000]*\\uE000/g, m => ' '.repeat(m.length));   // tables are skipped
    let { start: s, end: e } = getSelectionOffsets(editor);
    const inEditor = editor.contains(window.getSelection().anchorNode);
    if (!inEditor || s === e){   // nothing selected: from the caret (start of its word) to the end, or the whole text
      s = inEditor ? s : 0; e = text.length;
      if (s >= text.length || !/[\\p{L}\\p{N}]/u.test(text.slice(s))) s = 0;
      while (s > 0 && /[\\p{L}\\p{M}\\p{N}"'״׳]/u.test(text[s - 1])) s--;
    }
    const list = chunks(text, s, e).map(c => Object.assign(c, { text: text.slice(c.s, c.e) }));
    if (!list.length){ flashStatus('אין טקסט להקראה.'); return; }
    if (!pickVoice() && voices().length) flashStatus('אין במחשב קול עברי — ההקראה תהיה בקול אחר. הסבר בהגדרות ההקראה ⚙️.');
    stop();
    const myRun = ++run;
    setState(true);
    speakList(list, 0, myRun);
  }
  btn.onclick = () => { if (speaking) stop(); else start(); };
  editor.addEventListener('input', () => { if (speaking) stop(); });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (!modal.hasAttribute('hidden')){ e.preventDefault(); close(); return; }
    if (speaking){ e.preventDefault(); stop(); }
  });
  window.addEventListener('beforeunload', () => { if (synth) synth.cancel(); });
  // settings window
  function open(){ fillVoices(); allBox.checked = !!prefs.all; rateIn.value = prefs.rate; setRateText(); say(''); modal.removeAttribute('hidden'); }
  function close(){ modal.setAttribute('hidden', ''); }
  document.getElementById('tb-tts-settings').onclick = open;
  document.getElementById('tts-close').onclick = close;
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  voiceSel.onchange = () => { prefs.voice = voiceSel.value; savePrefs(); };
  allBox.onchange = () => { prefs.all = allBox.checked; savePrefs(); fillVoices(); };
  rateIn.oninput = () => { prefs.rate = parseFloat(rateIn.value) || 1; setRateText(); savePrefs(); };
  document.getElementById('tts-test').onclick = () => {
    if (!synth){ say('הדפדפן הזה לא תומך בהקראה.', 'err'); return; }
    stop(); const myRun = ++run;
    setState(true);
    speakList([{ s: null, e: null, text: 'שלום, זו דוגמה לקול שנבחר. אפשר לשנות את המהירות למטה.' }], 0, myRun, () => say('✓ אם לא נשמע כלום — בדקו את עוצמת הקול במחשב, או בחרו קול אחר.', 'ok'));
  };
  if (synth && 'onvoiceschanged' in synth) synth.addEventListener('voiceschanged', () => { if (!modal.hasAttribute('hidden')) fillVoices(); });
  return { start, stop, isSpeaking: () => speaking, chunks };
})();

// ---------- Footer actions ----------""")

step('מדריך',
"""      { n: '🎤 אישור קבוע למיקרופון', s: '#tb-offline-settings',""",
"""      { n: '🔊 הקראה', s: '#tb-tts', d: 'מקריא את הטקסט המסומן, ואם לא סומן כלום — מהסמן והלאה (או מתחילת המסמך). המשפט שמוקרא מסומן ברקע. לחיצה נוספת, או Esc, עוצרת. טבלאות מדולגות.' },
      { n: '⚙️ הגדרות הקראה', s: '#tb-tts-settings', d: 'בחירת קול ומהירות. העורך משתמש בקולות של המחשב והדפדפן: ב-Windows הקול העברי "Asaf" (בלי אינטרנט), ובאדג\\' גם הקולות הטבעיים "Avri" ו"Hila" (עם אינטרנט). אם אין קול עברי — בחלון יש הסבר איך מוסיפים אותו ב-Windows.' },
      { n: '🎤 אישור קבוע למיקרופון', s: '#tb-offline-settings',""")

MARK = "// ---------- ק-1: read aloud"
NEED = {'mark': "// ---------- מ-1: permanent microphone permission", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
