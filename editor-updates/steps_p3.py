# פ-3: punctuation AI works in "תורני" too (source references in ( ) / [ ] are protected), and offline dictation
# gets AI punctuation automatically — each dictated sentence is punctuated once the next one arrives (it needs the
# following words as context), and the last one when the recording stops. A switch in ⚙️ turns it off.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('המודל גם בתורני',
"""async function punctAIStatus(){
  if (textModeCache !== 'regular') return 'off';
  if (!window.PunctAI || !window.PunctAI.supported) return 'off';""",
"""async function punctAIStatus(){
  // פ-3: the model works in "תורני" too (references inside ( ) / [ ] are protected in punctAIInsertRange)
  if (!window.PunctAI || !window.PunctAI.supported) return 'off';""")

step('תורני: בלי סימנים בתוך סוגריים',
"""      const at = a + t.end;
      if (at <= start || at > end) return;              // with a selection: only words that end inside it
      inserts.push({ at, ch: sign });""",
"""      const at = a + t.end;
      if (at <= start || at > end) return;              // with a selection: only words that end inside it
      if (textModeCache === 'torani'){                  // פ-3: (פ"ג ה) / [דף כ ע"ב] — no marks inside brackets
        const before = text.slice(a, at);
        const depth = (before.match(/[(\\[]/g) || []).length - (before.match(/[)\\]]/g) || []).length;
        if (depth > 0) return;
      }
      inserts.push({ at, ch: sign });""")

step('סימון אוטומטי גם בתורני',
"""    if (mRunning || !pIsOn() || punctBusy || textModeCache !== 'regular') return;""",
"""    if (mRunning || !pIsOn() || punctBusy) return;   // פ-3: in "תורני" too""")

step('כיתוב הכפתור',
"""ו-? אחרי שאלה (המודל רק ברגיל). ' : '') +""",
"""ו-? אחרי שאלה. ' : '') +""")

step('מדריך: תורני/רגיל',
"""ובו גם מודל הפיסוק AI פועל.' }""",
"""ומודל הפיסוק AI פועל בשניהם (בתורני הוא לא מוסיף סימנים בתוך סוגריים, כדי לשמור על מראי מקום).' }""")

step('מדריך: ▶ פיסוק',
"""d: 'מפסק את כל המסמך. במצב "רגיל" נעזר גם במודל AI, אם הוא מותקן.' }""",
"""d: 'מפסק את כל המסמך, או את המסומן. נעזר גם במודל AI, אם הוא מותקן.' },
      { n: 'פיסוק AI בהכתבה', s: '#tb-offline-settings', d: 'בהכתבה אופליין, כשמודל הפיסוק מותקן, כל משפט שהוכתב מקבל פסיקים ונקודות לבד — אחרי שמגיע המשפט הבא, והאחרון כשעוצרים. מכבים ב-⚙️ ("פיסוק AI אוטומטי בהכתבה").' }""")

step('מתג בהגדרות האופליין',
"""      <label class="spoken-punct-row"><input type="checkbox" id="spoken-punct-toggle"> פקודות פיסוק בדיבור</label>""",
"""      <label class="spoken-punct-row"><input type="checkbox" id="spoken-punct-toggle"> פקודות פיסוק בדיבור</label>
      <label class="spoken-punct-row dict-punct-row"><input type="checkbox" id="dict-punct-toggle"> פיסוק AI אוטומטי בהכתבה</label>
      <div id="dict-punct-note" hidden></div>""")

step('עיצוב המתג',
"""  .ov-measure-tip{""",
"""  .dict-punct-row{ margin-top:6px !important; padding-top:0 !important; border-top:none !important; }
  #dict-punct-note{ font-size:12px; color: var(--parchment-dim); margin:2px 0 0 0; padding-inline-start:26px; }
  .ov-measure-tip{""")

step('הכתבה: מחזירה איפה נכנס הטקסט',
"""  return { newText: text.slice(0, start) + body + text.slice(base + oldLen), caret: start + body.length };
}""",
"""  return { newText: text.slice(0, start) + body + text.slice(base + oldLen), caret: start + body.length, start };
}""")

step('הכתבה: טווח המשפט',
"""  const { newText, caret } = spliceDictation(text, start, end - start, chunk);
  remapManualStylesForNewText(newText);
  renderTextIntoEditor(newText, caret);
  pushHistory(false); // debounced, like normal typing — a whole dictation run becomes one undo step
}""",
"""  const { newText, caret, start: at } = spliceDictation(text, start, end - start, chunk);
  remapManualStylesForNewText(newText);
  renderTextIntoEditor(newText, caret);
  pushHistory(false); // debounced, like normal typing — a whole dictation run becomes one undo step
  return { start: at, end: caret };   // פ-3: where the chunk went (for AI punctuation)
}

// ---------- פ-3: AI punctuation for offline dictation ----------
// A sentence is punctuated when the next one arrives (the model needs the words after it), the last one on stop.
// Only marks inside the dictated text are added; text the user typed meanwhile is never touched.
const DictPunct = (function(){
  const KEY = 'heb-style-editor-dict-punct-v1';
  const isOn = () => { try { return localStorage.getItem(KEY) !== '0'; } catch (e) { return true; } };
  let queue = [], busy = false, again = false;
  function add(s, e){
    if (!isOn() || e <= s) return;
    queue.push({ s, e, txt: extractPlainText(editor).slice(s, e) });
    if (queue.length > 1) run(false);
  }
  function finish(){ if (queue.length) run(true); }
  async function run(all){
    if (busy){ again = again || all || 'one'; return; }
    if (!isOn()){ queue = []; return; }
    let st = 'off';
    try { st = await punctAIStatus(); } catch (e) { /* ignore */ }
    if (st !== 'ready'){ queue = []; return; }
    const n = all ? queue.length : queue.length - 1;   // the newest sentence waits as context
    if (n <= 0) return;
    busy = true;
    try {
      const text = extractPlainText(editor);
      const jobs = queue.slice(0, n).filter(j => text.slice(j.s, j.e) === j.txt);   // still there, unchanged
      if (!jobs.length){ queue = queue.slice(n); return; }
      const s = Math.min(...jobs.map(j => j.s)), e = Math.max(...jobs.map(j => j.e));
      const ai = await punctAIInsertRange(text, s, e, null);
      const now = extractPlainText(editor);
      let p = 0; while (p < text.length && p < now.length && text[p] === now[p]) p++;   // unchanged prefix
      if (p < e){ return; }                              // edited inside the sentences meanwhile: try again later
      queue = queue.slice(n);
      if (!ai) return;
      const shift = ai.map[p] - p;
      const out = ai.text.slice(0, ai.map[p]) + now.slice(p);
      const map = new Array(now.length + 1);
      for (let i = 0; i <= now.length; i++) map[i] = i <= p ? ai.map[i] : i + shift;
      const sel = getSelectionOffsets(editor), focused = document.activeElement === editor;
      manualStyles = remapRangesByMap(manualStyles, map);
      boldOverrides = remapRangesByMap(boldOverrides, map);
      italicOverrides = remapRangesByMap(italicOverrides, map);
      underlineOverrides = remapRangesByMap(underlineOverrides, map);
      queue = queue.map(j => ({ s: map[j.s], e: map[j.e], txt: out.slice(map[j.s], map[j.e]) }));
      renderTextIntoEditor(out, focused ? (sel.end > sel.start ? { start: map[sel.start], end: map[sel.end] } : map[sel.start]) : map[now.length]);
      pushHistory(false);
    } catch (err) {
      if (!(err && err.stage === 'cancel')) console.warn('dictation punctuation — the model failed:', err);
      queue = queue.slice(n);
    } finally {
      busy = false;
      if (again){ const a = again === true; again = false; setTimeout(() => run(a), 30); }
    }
  }
  (function setupToggle(){
    const box = document.getElementById('dict-punct-toggle'), note = document.getElementById('dict-punct-note');
    if (!box) return;
    box.checked = isOn();
    box.onchange = () => { try { localStorage.setItem(KEY, box.checked ? '1' : '0'); } catch (e) { /* ignore */ } if (!box.checked) queue = []; };
    const showNote = async () => {
      let st = 'off'; try { st = await punctAIStatus(); } catch (e) { /* ignore */ }
      note.hidden = st === 'ready';
      note.textContent = st === 'locked' ? 'נדרש קוד הפעלה.' : 'עובד אחרי שמתקינים את מודל הפיסוק (🤖).';
    };
    document.getElementById('tb-offline-settings').addEventListener('click', () => setTimeout(showNote, 50));
  })();
  return { add, finish, isOn, pending: () => queue.length, busy: () => busy };
})();
window.DictPunct = DictPunct;""")

step('הכתבה: שליחה לפיסוק',
"""      case 'text': insertDictatedText(m.text + ' '); if (window.OfflineVoiceMeasure) OfflineVoiceMeasure.record(m, Date.now()); break;""",
"""      case 'text': { const r = insertDictatedText(m.text + ' '); if (r && window.DictPunct) DictPunct.add(r.start, r.end); if (window.OfflineVoiceMeasure) OfflineVoiceMeasure.record(m, Date.now()); break; }""")

step('הכתבה: בסוף — גם המשפט האחרון',
"""    pendingFlush = null;
    stopping = false;""",
"""    pendingFlush = null;
    if (window.DictPunct) DictPunct.finish();   // פ-3: the last sentence
    stopping = false;""")

MARK = "// ---------- פ-3: AI punctuation for offline dictation"
NEED = {'mark': "// ---------- ק-1: read aloud", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
