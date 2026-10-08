# ק-2: read aloud with automatic nikud — each sentence goes through the nikud model (ניקוד AI) before it is spoken,
# so the voice pronounces words correctly. The editor's text is not changed. A switch in ⚙️ הגדרות הקראה.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('מתג בחלון',
"""        <label class="tts-all"><input type="checkbox" id="tts-all-voices"> להציג גם קולות בשפות אחרות</label>
      </div>""",
"""        <label class="tts-all"><input type="checkbox" id="tts-all-voices"> להציג גם קולות בשפות אחרות</label>
      </div>
      <div class="field">
        <label class="tts-all tts-nikud"><input type="checkbox" id="tts-nikud"> ניקוד אוטומטי לפני ההקראה — הגייה נכונה יותר (הטקסט בעורך לא משתנה)</label>
        <div id="tts-nikud-note" class="tts-sub" hidden></div>
      </div>""")

step('עיצוב',
"""  #tts-msg{ min-height:20px;""",
"""  #tts-modal .tts-nikud{ color: var(--parchment); font-size:13px; align-items:flex-start; }
  #tts-modal .tts-nikud input{ margin-top:3px; }
  #tts-modal .tts-sub{ font-size:12px; color: var(--parchment-dim); padding-inline-start:22px; margin-top:2px; }
  #tts-msg{ min-height:20px;""")

step('הגדרה',
"""  let prefs = { voice: '', rate: 1, all: false };""",
"""  let prefs = { voice: '', rate: 1, all: false, nikud: true };   // ק-2: nikud is used only when its model is installed""")

step('ניקוד לפני הקראה',
"""  function speakList(list, i, myRun, onEnd){
    if (myRun !== run) return;
    if (i >= list.length){ setState(false); if (onEnd) onEnd(); return; }
    const c = list[i], u = new SpeechSynthesisUtterance(c.text);""",
"""  // ק-2: the nikud model, when it is installed and switched on; sentences are prepared one ahead of the voice
  let nikudOk = null;
  async function nikudReady(){
    if (!prefs.nikud) return false;
    const k = window.NikudAI;
    if (!k || !k.supported) return false;
    try { const info = await k.getInfo(); return !!(info && (!info.selfTest || info.selfTest.ok)) && !(k.isBusy && k.isBusy()); } catch (e) { return false; }
  }
  function vocalized(c){
    if (c.ready) return c.ready;
    c.ready = (async () => {
      if (!nikudOk || !/[\\u05D0-\\u05EA]/.test(c.text)) return c.text;
      try {
        const r = (await window.NikudAI.vocalizeParagraphs([c.text], {}))[0];
        if (!r || !r.inserts || !r.inserts.length) return c.text;
        const ins = r.inserts.slice().sort((a, b) => a.at - b.at);
        let out = '', at = 0;
        for (const x of ins){ out += c.text.slice(at, x.at) + x.s; at = x.at; }
        return out + c.text.slice(at);
      } catch (e) { console.warn('read aloud — nikud failed, reading without it:', e); nikudOk = false; return c.text; }
    })();
    return c.ready;
  }
  async function speakList(list, i, myRun, onEnd){
    if (myRun !== run) return;
    if (i >= list.length){ setState(false); if (onEnd) onEnd(); return; }
    if (i === 0 && nikudOk === null) nikudOk = await nikudReady();
    const said = await vocalized(list[i]);
    if (list[i + 1]) vocalized(list[i + 1]);           // the next sentence gets its nikud while this one is spoken
    if (myRun !== run) return;
    const c = list[i], u = new SpeechSynthesisUtterance(said);""")

step('כל הקראה בודקת מחדש',
"""    stop();
    const myRun = ++run;
    setState(true);
    speakList(list, 0, myRun);""",
"""    stop();
    const myRun = ++run;
    nikudOk = null;
    setState(true);
    speakList(list, 0, myRun);""")

step('דוגמה',
"""    stop(); const myRun = ++run;
    setState(true);
    speakList([{ s: null, e: null, text: 'שלום, זו דוגמה לקול שנבחר. אפשר לשנות את המהירות למטה.' }]""",
"""    stop(); const myRun = ++run;
    nikudOk = null;
    setState(true);
    speakList([{ s: null, e: null, text: 'שלום, זו דוגמה לקול שנבחר. אפשר לשנות את המהירות למטה.' }]""")

step('פתיחת החלון',
"""  function open(){ fillVoices(); allBox.checked = !!prefs.all; rateIn.value = prefs.rate; setRateText(); say(''); modal.removeAttribute('hidden'); }""",
"""  function open(){
    fillVoices(); allBox.checked = !!prefs.all; rateIn.value = prefs.rate; setRateText(); say('');
    const nb = document.getElementById('tts-nikud'), nn = document.getElementById('tts-nikud-note');
    nb.checked = prefs.nikud !== false;
    nn.hidden = true;
    (async () => {
      const k = window.NikudAI;
      let info = null; try { info = k && k.supported ? await k.getInfo() : null; } catch (e) { info = null; }
      nn.hidden = !!info;
      nn.textContent = 'עובד אחרי שמתקינים את מודל הניקוד (🤖). עד אז ההקראה בלי ניקוד.';
    })();
    modal.removeAttribute('hidden');
  }
  document.getElementById('tts-nikud').onchange = (e) => { prefs.nikud = e.target.checked; savePrefs(); };""")

step('מדריך',
"""טבלאות מדולגות.' },""",
"""טבלאות מדולגות. כשמודל הניקוד מותקן, כל משפט מנוקד לפני ההקראה (רק לקול — הטקסט לא משתנה), וההגייה נכונה יותר.' },""")

MARK = "// ק-2: the nikud model, when it is installed and switched on"
NEED = {'mark': "// ---------- ק-1: read aloud", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
