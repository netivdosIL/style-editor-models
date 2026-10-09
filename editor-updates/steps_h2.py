# ה-2: offline dictation is ready the moment the button is pressed. The model is loaded in the background — when the
# editor opens (if offline dictation was used in the last 30 days), or as soon as the mouse moves over the button.
# A click while it is still loading starts the recording as soon as it is ready.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('בזמן טעינה מראש הכפתור נשאר פעיל',
"""    isLoading = true; btn.disabled = true; btn.classList.add('loading');""",
"""    isLoading = true; btn.disabled = !preloading; btn.classList.add('loading');   // ה-2: a click during a background load waits for it""")

step('טעינה מראש',
"""  btn.onclick = () => {
    if (isLoading || stopping) return;
    isRecording ? stopRecording() : startRecording();
  };

  refreshIdleNote();
})();""",
"""  // ---- ה-2: load the model in the background, so the first click starts listening at once ----
  const USED_KEY = 'heb-style-editor-offline-used-v1';
  let preloading = false, startAfterLoad = false;
  async function preload(why){
    if (preloading || isLoading || isRecording || (transport && engineReady)) return;
    if (!isActivated() && !isTrialActive()) return;
    try { const st = await getStatus(getActiveModel()); if (!st.complete) return; } catch (e) { return; }
    preloading = true;
    try { await ensureEngine(); setIdle(); }
    catch (e) { console.warn('offline voice typing — background load (' + why + ') failed:', e); try { disposeEngine(); } catch (e2) { /* ignore */ } setIdle(); }
    finally {
      preloading = false; isLoading = false; btn.classList.remove('loading'); btn.disabled = false; updateEar();
      if (startAfterLoad){ startAfterLoad = false; setNote(''); startRecording(); }
    }
  }
  window.OfflineVoicePreload = preload;
  btn.addEventListener('pointerenter', () => { setTimeout(() => preload('hover'), 0); });
  setTimeout(() => {
    let used = 0; try { used = parseInt(localStorage.getItem(USED_KEY) || '0', 10) || 0; } catch (e) { /* ignore */ }
    if (used && Date.now() - used < 30 * 86400000) preload('startup');
  }, 3000);

  btn.onclick = () => {
    if (preloading && !isRecording){ startAfterLoad = true; setNote('מכין את ההכתבה…'); return; }   // ה-2
    if (isLoading || stopping) return;
    if (!isRecording){ try { localStorage.setItem(USED_KEY, String(Date.now())); } catch (e) { /* ignore */ } }
    isRecording ? stopRecording() : startRecording();
  };

  refreshIdleNote();
})();""")

MARK = "// ---- ה-2: load the model in the background"
NEED = {'mark': "// ה-1: replaces only the part of the editor that differs", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
