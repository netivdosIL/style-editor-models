# א-1: "הקבצים שלי" move from localStorage (~5MB for everything) to IndexedDB (hundreds of MB).
# The rest of the editor keeps its synchronous loadDocs()/saveDocs(): a cache in memory, written through to IndexedDB.
# Existing files are copied over once, checked, and only then removed from localStorage. A small name index stays in
# localStorage so the editor knows the open file's name before IndexedDB has loaded.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('אחסון הקבצים',
"""function loadDocs(){
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
  catch (e) { return {}; }
}
function saveDocs(docs){
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(docs)); return true; }
  catch (e) { return false; }
}""",
"""// ---------- א-1: the files live in IndexedDB; loadDocs()/saveDocs() work on a cache in memory ----------
const DocStore = (function(){
  const DB = 'heb-style-editor-docs', STORE = 'docs', INDEX_KEY = 'heb-style-editor-docs-index-v1', MOVED_KEY = 'heb-style-editor-docs-in-idb-v1';
  let cache = {}, ready = false, failed = false, writing = Promise.resolve();
  const waiters = [];
  const lsGet = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  function open(){
    return new Promise((res, rej) => {
      const r = indexedDB.open(DB, 1);
      r.onupgradeneeded = () => r.result.createObjectStore(STORE);
      r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
    });
  }
  function tx(mode, fn){
    return open().then(db => new Promise((res, rej) => {
      const t = db.transaction(STORE, mode), out = fn(t.objectStore(STORE));
      t.oncomplete = () => { db.close(); res(out && out.result); };
      t.onerror = t.onabort = () => { db.close(); rej(t.error || new Error('idb')); };
    }));
  }
  function readAll(){
    return open().then(db => new Promise((res, rej) => {
      const out = {}, t = db.transaction(STORE, 'readonly'), c = t.objectStore(STORE).openCursor();
      c.onsuccess = () => { const cur = c.result; if (cur){ out[cur.key] = cur.value; cur.continue(); } };
      t.oncomplete = () => { db.close(); res(out); };
      t.onerror = () => { db.close(); rej(t.error); };
    }));
  }
  function writeIndex(){
    const idx = {};
    for (const id of Object.keys(cache)){ const d = cache[id]; idx[id] = { name: d.name, updatedAt: d.updatedAt || 0 }; }
    try { localStorage.setItem(INDEX_KEY, JSON.stringify(idx)); } catch (e) { /* only a convenience */ }
  }
  function setReady(){ ready = true; waiters.splice(0).forEach(f => { try { f(); } catch (e) { /* ignore */ } }); }
  // start: files still in localStorage are usable at once (and are moved); otherwise the name index until IndexedDB loads
  const legacy = lsGet(STORAGE_KEY);
  if (legacy !== null){
    try { cache = JSON.parse(legacy) || {}; } catch (e) { cache = {}; }
    setReady();
    setTimeout(async () => {   // move them, check every file arrived, and only then free the old space
      try {
        // files already in IndexedDB (saved by the updated editor) join the ones from localStorage — the newer copy wins
        const have = await readAll();
        for (const id of Object.keys(have)) if (!cache[id] || (have[id].updatedAt || 0) > (cache[id].updatedAt || 0)) cache[id] = have[id];
        await tx('readwrite', st => { for (const id of Object.keys(cache)) st.put(cache[id], id); });
        const back = await readAll();
        if (Object.keys(cache).every(id => back[id] && JSON.stringify(back[id]) === JSON.stringify(cache[id]))){
          writeIndex();
          localStorage.setItem(MOVED_KEY, '1');
          localStorage.removeItem(STORAGE_KEY);
        }
      } catch (e) { console.warn('files: could not move to IndexedDB yet, they stay where they are:', e); failed = true; }
    }, 1500);
  } else {
    try { const idx = JSON.parse(lsGet(INDEX_KEY) || '{}') || {}; for (const id of Object.keys(idx)) cache[id] = { name: idx[id].name, updatedAt: idx[id].updatedAt, __stub: true }; } catch (e) { /* ignore */ }
    readAll().then(all => { cache = all; writeIndex(); setReady(); })
      .catch(e => { console.error('files: IndexedDB is not available:', e); failed = true; cache = {}; setReady(); });
  }
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (e) { /* ask the browser not to clear it */ }
  function load(){ return Object.assign({}, cache); }
  function save(docs){
    if (!ready) return false;
    const before = cache, puts = [], dels = [];
    for (const id of Object.keys(docs)) if (docs[id] !== before[id]) puts.push(id);
    for (const id of Object.keys(before)) if (!(id in docs)) dels.push(id);
    cache = Object.assign({}, docs);
    writeIndex();
    if (lsGet(STORAGE_KEY) !== null && !failed){   // not moved yet: keep the old copy in step too
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(cache)); } catch (e) { /* IndexedDB has it */ }
    }
    if (!puts.length && !dels.length) return true;
    writing = writing.then(() => tx('readwrite', st => { puts.forEach(id => st.put(cache[id], id)); dels.forEach(id => st.delete(id)); }))
      .catch(e => {
        console.error('files: saving to IndexedDB failed:', e);
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(cache)); localStorage.removeItem(MOVED_KEY); }   // last resort
        catch (e2) { flashStatus('⚠ השמירה ל"הקבצים שלי" נכשלה — אין מספיק מקום בדפדפן', 8000); }
      });
    return true;
  }
  return {
    load, save, isReady: () => ready, onReady: (f) => { if (ready) f(); else waiters.push(f); },
    json: () => JSON.stringify(cache), flush: () => writing,
    replaceAll: (docs) => { const ok = save(docs); return ok ? writing : Promise.reject(new Error('not ready')); },
    usage: async () => { try { return navigator.storage && navigator.storage.estimate ? await navigator.storage.estimate() : null; } catch (e) { return null; } }
  };
})();
window.DocStore = DocStore;
function loadDocs(){ return DocStore.load(); }
function saveDocs(docs){ return DocStore.save(docs); }
function docsStillLoading(){
  if (DocStore.isReady()) return false;
  flashStatus('טוען את "הקבצים שלי"… נסו שוב בעוד רגע');
  return true;
}""")

step('שמירה: מחכה שהקבצים ייטענו',
"""function doSave(promptForName){
  if (!isActivated() && !isTrialActive()){ requireActivation(() => doSave(promptForName)); return; }""",
"""function doSave(promptForName){
  if (!isActivated() && !isTrialActive()){ requireActivation(() => doSave(promptForName)); return; }
  if (docsStillLoading()) return;   // א-1""")

step('רשימת הקבצים: אחרי הטעינה',
"""function renderFilesList(){
  const docs = loadDocs();
  const listEl = document.getElementById('files-list');""",
"""function renderFilesList(){
  const listEl = document.getElementById('files-list');
  if (!DocStore.isReady()){   // א-1: IndexedDB is still loading (a moment after start)
    listEl.innerHTML = '<div class="files-empty">טוען…</div>';
    DocStore.onReady(renderFilesList);
    return;
  }
  const docs = loadDocs();""")

step('ייצוא נתונים: כולל הקבצים',
"""      if (k && isOurKey(k)) data[k] = localStorage.getItem(k);
    }""",
"""      if (k && isOurKey(k)) data[k] = localStorage.getItem(k);
    }
    if (window.DocStore && DocStore.isReady()) data[K.docs] = DocStore.json();   // א-1: the files are in IndexedDB
    delete data[PREFIX + 'docs-index-v1']; delete data[PREFIX + 'docs-in-idb-v1'];""")

step('ייבוא: מיזוג מול הקבצים שבעורך',
"""      if (!isOurKey(k) || typeof v !== 'string') return;
      const cur = localStorage.getItem(k);""",
"""      if (!isOurKey(k) || typeof v !== 'string') return;
      if (k === PREFIX + 'docs-index-v1' || k === PREFIX + 'docs-in-idb-v1') return;   // א-1: bookkeeping of this copy
      const cur = (k === K.docs && window.DocStore) ? DocStore.json() : localStorage.getItem(k);""")

step('ייבוא: כתיבת הקבצים',
"""    const backup = {};
    keys.forEach(k => { backup[k] = localStorage.getItem(k); });
    try { keys.forEach(k => localStorage.setItem(k, p.writes[k])); }
    catch (e) {
      keys.forEach(k => { try { if (backup[k] == null) localStorage.removeItem(k); else localStorage.setItem(k, backup[k]); } catch (e2) { /* ignore */ } });
      setMsg('הייבוא נכשל (אין מספיק מקום בזיכרון של הדפדפן). לא שונה כלום.', 'err'); return;
    }""",
"""    if (window.DocStore && !DocStore.isReady()){ setMsg('טוען את "הקבצים שלי"… נסו שוב בעוד רגע.', 'err'); return; }
    const docsJson = window.DocStore ? p.writes[K.docs] : null;   // א-1: the files go to IndexedDB, the rest to localStorage
    const lsKeys = keys.filter(k => !(docsJson && k === K.docs));
    const backup = {};
    lsKeys.forEach(k => { backup[k] = localStorage.getItem(k); });
    try { lsKeys.forEach(k => localStorage.setItem(k, p.writes[k])); }
    catch (e) {
      lsKeys.forEach(k => { try { if (backup[k] == null) localStorage.removeItem(k); else localStorage.setItem(k, backup[k]); } catch (e2) { /* ignore */ } });
      setMsg('הייבוא נכשל (אין מספיק מקום בזיכרון של הדפדפן). לא שונה כלום.', 'err'); return;
    }
    if (docsJson){
      try { await DocStore.replaceAll(JSON.parse(docsJson)); await DocStore.flush(); }
      catch (e) { setMsg('הייבוא של הקבצים נכשל: ' + (e && e.message || e), 'err'); return; }
    }""")

step('מדריך',
"""      { n: '⬇ ייצא נתונים  ⬆ ייבא נתונים',""",
"""      { n: 'איפה נשמרים הקבצים', s: '#files-btn', d: '"הקבצים שלי" נשמרים בתוך הדפדפן, באחסון גדול שמספיק לאלפי מסמכים (כולל 10 גרסאות קודמות לכל אחד). לגיבוי או למעבר למחשב אחר: "⬇ ייצא נתונים".' },
      { n: '⬇ ייצא נתונים  ⬆ ייבא נתונים',""")

MARK = "// ---------- א-1: the files live in IndexedDB"
NEED = {'mark': "// ---------- ק-1: read aloud", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
