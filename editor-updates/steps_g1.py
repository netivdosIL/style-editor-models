# ג-1: install the Hebrew model (GigaAM-He) in the 🌐/⚙️ dialog and from the install folder.
# Each step: (name, find, replace). `find` must occur exactly once in the editor.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

# 1. the model list + where the Hebrew parts live
step('רשימת המודלים',
"""    base: { label: 'Base', desc: 'מדויק יותר, איטי יותר', archive: 'sherpa-onnx-whisper-base.tar.bz2', size: '208MB' }
  };""",
"""    base: { label: 'Base', desc: 'מדויק יותר, איטי יותר', archive: 'sherpa-onnx-whisper-base.tar.bz2', size: '208MB' },
    // ג-1: Hebrew speech model GigaAM-He (MIT) — 5 parts + a list of their checksums, from our own GitHub release
    he: { label: 'עברית מדויק', desc: 'מודל עברי, מדויק ומהיר', kind: 'ctc', size: '236MB',
          parts: ['hebrew-gigaam-int8.zip.part01', 'hebrew-gigaam-int8.zip.part02', 'hebrew-gigaam-int8.zip.part03',
                  'hebrew-gigaam-int8.zip.part04', 'hebrew-gigaam-int8.zip.part05', 'hebrew-gigaam-int8.zip.parts.json'] }
  };
  const GH_HE = 'https://github.com/netivdosIL/style-editor-models/releases/download/gigaam-he-v2/';
  const GH_HE_PAGE = 'https://github.com/netivdosIL/style-editor-models/releases/tag/gigaam-he-v2';
  const HE_KINDS = ['model', 'info'];
  function kindsOf(id){ return MODELS[id] && MODELS[id].kind === 'ctc' ? HE_KINDS : KINDS; }
  // the engine for the Hebrew model arrives in the next update (ג-2); until then it can be installed but not chosen
  function engineFor(id){ return !(MODELS[id] && MODELS[id].kind === 'ctc') || !!window.GigaAMOffline; }""")

# 2. status per model
step('בדיקת התקנה',
"""    const st = { files: {}, complete: true };
    for (const kind of KINDS){""",
"""    const st = { files: {}, complete: true };
    for (const kind of kindsOf(modelId)){""")

# 3. the dialog rows
step('שורות החלון',
"""      if (st.complete){
        html += '<div class="file-item off-model' + (id === active ? ' active' : '') + '" data-model="' + id + '">' +
          '<input type="radio" name="off-model" value="' + id + '"' + (id === active ? ' checked' : '') + (busy ? ' disabled' : '') + '>' +
          head + '<div class="fdate off-status ok">✓ מותקן</div></div>' +""",
"""      if (st.complete){
        const canUse = engineFor(id);
        html += '<div class="file-item off-model' + (id === active ? ' active' : '') + '" data-model="' + id + '">' +
          '<input type="radio" name="off-model" value="' + id + '"' + (id === active ? ' checked' : '') + (busy || !canUse ? ' disabled' : '') + '>' +
          head + '<div class="fdate off-status ok">✓ מותקן' + (canUse ? '' : ' · ייכנס לשימוש בעדכון הבא') + '</div></div>' +""")

step('שורת הורדה',
"""          '<div class="fdate off-status">צריך הורדה (' + M.size + ')</div>' +
          (altShownFor === id ? '<a class="off-alt" data-act="alt" href="' + GH_ALT + M.archive + '" target="_blank" rel="noopener">ההורדה לא התחילה? הורד מהשרת החלופי</a>' : '') +""",
"""          '<div class="fdate off-status">צריך הורדה (' + M.size + (M.parts ? ', ' + (M.parts.length - 1) + ' חלקים' : '') + ')</div>' +
          (altShownFor === id ? (M.parts
            ? '<a class="off-alt" data-act="alt" href="' + GH_HE_PAGE + '" target="_blank" rel="noopener">חלק מההורדות לא התחילו? הורד מדף הקבצים</a>'
            : '<a class="off-alt" data-act="alt" href="' + GH_ALT + M.archive + '" target="_blank" rel="noopener">ההורדה לא התחילה? הורד מהשרת החלופי</a>') : '') +""")

# 4. download: the Hebrew model is 6 files, started one after the other
step('הורדה',
"""  function startDownload(id){
    const a = document.createElement('a');""",
"""  function startDownload(id){
    if (MODELS[id].parts){   // ג-1: six small files; if one is cut off, only that one is downloaded again
      MODELS[id].parts.forEach((name, i) => setTimeout(() => {
        const a = document.createElement('a');
        a.href = GH_HE + name; a.download = name; a.rel = 'noopener'; a.style.display = 'none';
        document.body.appendChild(a); a.click(); a.remove();
      }, i * 1200));
      downloadStarted = true; pickBox.hidden = false;
      setModalMsg('יורדים 6 קבצים. אם הדפדפן שואל "להוריד כמה קבצים?" — לוחצים "אפשר". כשכולם ירדו: "בחר את הקובץ שהורד" ומסמנים את כל 6 הקבצים יחד.');
      if (altShownFor !== id){ altShownFor = id; renderModels(); }
      return;
    }
    const a = document.createElement('a');""")

# 5. installing the Hebrew model from its parts (or from the whole zip)
step('התקנת המודל העברי',
"""  async function installRaw(files){ // already-unpacked files, e.g. "tiny-encoder.int8.onnx\"""".replace('\\"', ''),
"""  // ---- ג-1: the Hebrew model: parts → one zip → model.int8.onnx + model_info.json (+ test_vectors.json) ----
  function isHebrewFile(f){ return /hebrew-gigaam/i.test(f.name) && /(\\.part\\d+|\\.parts\\.json|\\.zip)$/i.test(f.name); }
  function zipEntries(u8){
    const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
    let e = -1;
    for (let i = u8.length - 22; i >= Math.max(0, u8.length - 65557); i--) if (dv.getUint32(i, true) === 0x06054b50){ e = i; break; }
    if (e < 0) throw new Error('הקבצים לא שלמים — חסר חלק, או שאחד מהם לא ירד עד הסוף.');
    const count = dv.getUint16(e + 10, true); let p = dv.getUint32(e + 16, true);
    const out = [];
    for (let k = 0; k < count; k++){
      if (dv.getUint32(p, true) !== 0x02014b50) throw new Error('הקובץ פגום.');
      const method = dv.getUint16(p + 10, true), csize = dv.getUint32(p + 20, true);
      const nlen = dv.getUint16(p + 28, true), xlen = dv.getUint16(p + 30, true), clen = dv.getUint16(p + 32, true);
      const loc = dv.getUint32(p + 42, true);
      const name = new TextDecoder().decode(u8.subarray(p + 46, p + 46 + nlen));
      p += 46 + nlen + xlen + clen;
      if (name.endsWith('/')) continue;
      const lnl = dv.getUint16(loc + 26, true), lxl = dv.getUint16(loc + 28, true);
      out.push({ name, method, data: u8.subarray(loc + 30 + lnl + lxl, loc + 30 + lnl + lxl + csize) });
    }
    return out;
  }
  async function zipBytes(en){
    if (en.method === 0) return en.data;
    if (en.method !== 8 || typeof DecompressionStream === 'undefined') throw new Error('הדפדפן לא פותח את סוג הדחיסה.');
    return new Uint8Array(await new Response(new Blob([en.data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());
  }
  async function sha256hex(buf){
    if (!(window.crypto && crypto.subtle)) return null;
    const h = await crypto.subtle.digest('SHA-256', buf);
    return Array.from(new Uint8Array(h), b => b.toString(16).padStart(2, '0')).join('');
  }
  async function installHebrew(files, onProgress){
    const report = onProgress || ((p) => setModalMsg('מתקין… ' + Math.round(p * 100) + '%'));
    const manifestFile = files.find(f => /\\.parts\\.json$/i.test(f.name));
    const whole = files.find(f => /\\.zip$/i.test(f.name));
    let parts = files.filter(f => /\\.part\\d+$/i.test(f.name)).sort((a, b) => a.name.localeCompare(b.name, 'en', { numeric: true }));
    let manifest = null;
    if (manifestFile){ try { manifest = JSON.parse(await manifestFile.text()); } catch (e) { manifest = null; } }
    let all;
    if (parts.length){
      if (manifest && manifest.parts){
        const missing = manifest.parts.map(p => p.name).filter(n => !parts.some(f => f.name === n));
        if (missing.length) throw new Error('חסרים חלקים: ' + missing.map(n => n.replace(/^.*\\./, '')).join(', ') + '. מסמנים יחד את כל 6 הקבצים.');
        parts = manifest.parts.map(p => parts.find(f => f.name === p.name));
      } else {
        const nums = parts.map(f => +/\\.part(\\d+)$/i.exec(f.name)[1]);
        for (let i = 0; i < nums.length; i++) if (nums[i] !== i + 1) throw new Error('חסר חלק מספר ' + (i + 1) + '.');
      }
      all = new Uint8Array(parts.reduce((s, f) => s + f.size, 0));
      let off = 0; const bad = [];
      for (let i = 0; i < parts.length; i++){
        const buf = await parts[i].arrayBuffer();
        if (manifest && manifest.parts){
          const m = manifest.parts[i];
          if (buf.byteLength !== m.size) bad.push(parts[i].name);
          else { const h = await sha256hex(buf); if (h && h !== m.sha256) bad.push(parts[i].name); }
        }
        all.set(new Uint8Array(buf), off); off += buf.byteLength;
        report(0.8 * (i + 1) / parts.length);
      }
      if (bad.length) throw new Error('צריך להוריד מחדש רק את: ' + bad.map(n => n.replace(/^.*\\./, '')).join(', ') + ' (לא ירד עד הסוף או פגום).');
    } else if (whole){
      all = new Uint8Array(await whole.arrayBuffer()); report(0.8);
    } else throw new Error('בחר את קבצי המודל העברי (part01 עד part05 ו-parts.json).');
    const ents = zipEntries(all);
    const infoE = ents.find(x => /model_info\\.json$/.test(x.name));
    if (!infoE) throw new Error('הקבצים לא מכילים את המודל העברי.');
    const info = JSON.parse(new TextDecoder().decode(await zipBytes(infoE)));
    if (info.type !== 'ctc' || !info.features || !info.vocab) throw new Error('הקבצים לא מכילים את המודל העברי.');
    const modelE = ents.find(x => x.name.split('/').pop() === info.file);
    if (!modelE) throw new Error('חסר קובץ המודל בתוך הקבצים.');
    const tvE = ents.find(x => /test_vectors\\.json$/.test(x.name));
    const modelBlob = new Blob([await zipBytes(modelE)]);
    const tvBlob = tvE ? new Blob([await zipBytes(tvE)]) : null;
    all = null;
    report(0.9);
    await dbPut('he/model', modelBlob);
    if (tvBlob) await dbPut('he/tv', tvBlob);
    await dbPut('he/info', new Blob([JSON.stringify(info)], { type: 'application/json' }));
    report(1);
    return 'he';
  }
  async function installRaw(files){ // already-unpacked files, e.g. "tiny-encoder.int8.onnx\"""".replace('\\"', ''))

# 6. route the picked files
step('בחירת קבצים',
"""      const archive = files.find(f => /\\.bz2$/i.test(f.name));
      const id = archive ? await installArchive(archive) : await installRaw(files);""",
"""      const archive = files.find(f => /\\.bz2$/i.test(f.name));
      const id = files.some(isHebrewFile) ? await installHebrew(files.filter(isHebrewFile))
               : archive ? await installArchive(archive) : await installRaw(files);""")

step('הודעת סיום התקנה',
"""      setActiveModel(id);
      if (loadedModel === id) disposeEngine();
      downloadStarted = false;""",
"""      if (engineFor(id)) setActiveModel(id);
      if (loadedModel === id) disposeEngine();
      downloadStarted = false;""")

step('הודעת שגיאה',
"""      const msg = /bzip2|CRC/i.test(errText(e)) ? 'הקובץ לא הורד עד הסוף או פגום — הורד/י שוב.' : errText(e);""",
"""      const msg = /bzip2|CRC/i.test(errText(e)) ? 'הקובץ לא הורד עד הסוף או פגום — הורד/י שוב.'
                : /quota/i.test(((e && e.name) || '') + errText(e)) ? 'אין מספיק מקום בדיסק בשביל המודל.' : errText(e);""")

step('סוגי קבצים בחלון הבחירה',
"""          types: [{ description: 'קובץ מודל', accept: { 'application/octet-stream': ['.bz2', '.onnx', '.txt'] } }] });""",
"""          types: [{ description: 'קובץ מודל', accept: { 'application/octet-stream': ['.bz2', '.onnx', '.txt', '.zip', '.json',
            '.part01', '.part02', '.part03', '.part04', '.part05', '.part06', '.part07', '.part08', '.part09'] } }] });""")

step('מחיקה',
"""      for (const k of KINDS.concat(['encoderF'])) { try { await dbDel(id + '/' + k); } catch (err) { /* ignore */ } }""",
"""      for (const k of (MODELS[id].kind === 'ctc' ? HE_KINDS.concat(['tv']) : KINDS.concat(['encoderF']))) { try { await dbDel(id + '/' + k); } catch (err) { /* ignore */ } }
      if (getActiveModel() === id) setActiveModel('tiny');""")

step('ממשק להתקנה מתיקייה',
"""  window.OfflineVoice = {
    MODELS,""",
"""  window.OfflineVoice = {
    MODELS,
    isHebrewFile,
    async installHebrewFiles(files, onProgress){   // ג-1: used by "התקן מתיקייה"
      if (busy) throw new Error('התקנה אחרת של ההקלדה הקולית כבר פועלת.');
      if (isRecording || stopping || isLoading) throw new Error('עצור את ההקלטה האופליין קודם.');
      busy = true;
      try {
        const id = await installHebrew(files, onProgress);
        if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
        if (loadedModel === id) disposeEngine();
        if (engineFor(id) && !(await window.OfflineVoice.isInstalled(getActiveModel()))) setActiveModel(id);
        return id;
      } finally { busy = false; if (!modal.hidden) renderModels(); refreshIdleNote(); }
    },""")

step('שם המודל במדידה',
"""  const MODEL_NAMES = { tiny: 'Tiny', base: 'Base' };""",
"""  const MODEL_NAMES = { tiny: 'Tiny', base: 'Base', he: 'עברית מדויק' };""")

step('קלט הקבצים',
"""<input type="file" id="offline-file" accept=".bz2,.onnx,.txt" multiple hidden>""",
"""<input type="file" id="offline-file" accept=".bz2,.onnx,.txt,.zip,.json,.part01,.part02,.part03,.part04,.part05,.part06,.part07,.part08,.part09" multiple hidden>""")

# 7. install from folder
step('תיקייה: רשימה',
"""    { id: 'base',    label: 'הקלדה קולית — Base', file: 'sherpa-onnx-whisper-base.tar.bz2' }
  ];""",
"""    { id: 'base',    label: 'הקלדה קולית — Base', file: 'sherpa-onnx-whisper-base.tar.bz2' },
    { id: 'he',      label: 'הקלדה קולית — עברית מדויק', file: 'hebrew-gigaam-int8.zip.part01–05 + parts.json' }
  ];""")

step('תיקייה: מה מותקן',
"""      base: !!(v && await v.isInstalled('base'))
    };""",
"""      base: !!(v && await v.isInstalled('base')),
      he: !!(v && v.installHebrewFiles && await v.isInstalled('he'))
    };""")

step('תיקייה: לא נתמך',
"""      if (!v && (it.id === 'tiny' || it.id === 'base')){""",
"""      if ((!v && (it.id === 'tiny' || it.id === 'base' || it.id === 'he')) || (it.id === 'he' && v && !v.installHebrewFiles)){""")

step('תיקייה: סריקת קבצים',
"""      if (h.kind === 'file'){ if (/\\.(zip|bz2|whl|onnx)$/i.test(h.name)) out.push(await h.getFile()); }""",
"""      if (h.kind === 'file'){ if (/\\.(zip|bz2|whl|onnx|json|part\\d+)$/i.test(h.name)) out.push(await h.getFile()); }""")

step('תיקייה: בחירה רגילה',
"""  input.onchange = () => { const files = Array.from(input.files || []).filter(f => /\\.(zip|bz2|whl|onnx)$/i.test(f.name)); input.value = ''; run(files); };""",
"""  input.onchange = () => { const files = Array.from(input.files || []).filter(f => /\\.(zip|bz2|whl|onnx|json|part\\d+)$/i.test(f.name)); input.value = ''; run(files); };""")

step('תיקייה: זיהוי',
"""    const p = P(), found = {};
    for (const f of files){
      if (K() && K().supported && /\\.(whl|onnx)$/i.test(f.name)){""",
"""    const p = P(), found = {};
    for (const f of files){
      if (V() && V().isHebrewFile && V().isHebrewFile(f)){   // ג-1: the Hebrew model's parts
        found.he = found.he || { files: [] }; found.he.files.push(f);
        continue;
      }
      if (/\\.json$/i.test(f.name) || /\\.part\\d+$/i.test(f.name)) continue;
      if (K() && K().supported && /\\.(whl|onnx)$/i.test(f.name)){""")

step('תיקייה: התקנה',
"""          } else {
            setRow(it.id, 'קורא את הקובץ…');
            let last = -1;
            await V().installArchiveFile(f.file, (p) => {""",
"""          } else if (it.id === 'he'){
            setRow(it.id, 'קורא את הקבצים…');
            let last = -1;
            await V().installHebrewFiles(f.files, (p) => {
              const pct = Math.round(p * 100);
              if (pct !== last){ last = pct; setRow(it.id, 'מתקין… ' + pct + '%'); }
            });
            setRow(it.id, '✓ הותקן', 'ok'); results.ok++;
          } else {
            setRow(it.id, 'קורא את הקובץ…');
            let last = -1;
            await V().installArchiveFile(f.file, (p) => {""")

MARK = "const GH_HE = 'https://github.com/netivdosIL/style-editor-models/releases/download/gigaam-he-v2/';"
