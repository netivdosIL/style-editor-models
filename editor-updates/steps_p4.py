# פ-4: AI punctuation for online voice typing too (Chrome/Edge speech service). The sentence still being heard is
# shown as grey preview text — punctuation waits until it is final, so nothing moves under it.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('המתנה בזמן תצוגה מקדימה',
"""    if (st !== 'ready'){ queue = []; return; }""",
"""    if (st !== 'ready'){ queue = []; return; }
    if (holdFn && holdFn()){ setTimeout(() => run(all), 400); return; }   // פ-4: grey preview text on screen — wait""")

step('לא להחיל בזמן תצוגה מקדימה',
"""      if (p < e){ return; }                              // edited inside the sentences meanwhile: try again later""",
"""      if (p < e){ return; }                              // edited inside the sentences meanwhile: try again later
      if (holdFn && holdFn()){ again = again || all || 'one'; return; }   // פ-4: a preview appeared meanwhile""")

step('חשיפת ההמתנה',
"""  return { add, finish, isOn, pending: () => queue.length, busy: () => busy };""",
"""  let holdFn = null;   // פ-4: online dictation tells when its grey preview text is on screen
  return { add, finish, isOn, pending: () => queue.length, busy: () => busy, setHold: (f) => { holdFn = f; } };""")

step('הכתבה אונליין: פיסוק',
"""    const text = extractPlainText(editor);
    const { newText, caret } = spliceDictation(text, base, oldLen, chunk);
    remapManualStylesForNewText(newText);
    renderTextIntoEditor(newText, caret);
    interimStart = null;
    interimLen = 0;
    pushHistory(false); // debounced, like normal typing — a whole dictation run becomes one undo step
  }""",
"""    const text = extractPlainText(editor);
    const { newText, caret, start: at } = spliceDictation(text, base, oldLen, chunk);
    remapManualStylesForNewText(newText);
    renderTextIntoEditor(newText, caret);
    interimStart = null;
    interimLen = 0;
    pushHistory(false); // debounced, like normal typing — a whole dictation run becomes one undo step
    if (window.DictPunct){ DictPunct.setHold(() => interimStart !== null); DictPunct.add(at, caret); }   // פ-4
  }""")

step('הכתבה אונליין: בסוף',
"""    micBtn.classList.remove('recording');
    micBtn.title = 'הקלדה קולית';
    micBtn.setAttribute('aria-label', 'הקלדה קולית (דרך האינטרנט)');
    micNote.textContent = '';
  }""",
"""    micBtn.classList.remove('recording');
    micBtn.title = 'הקלדה קולית';
    micBtn.setAttribute('aria-label', 'הקלדה קולית (דרך האינטרנט)');
    micNote.textContent = '';
    if (window.DictPunct) DictPunct.finish();   // פ-4: the last sentence
  }""")

step('מדריך',
"""      { n: 'פיסוק AI בהכתבה', s: '#tb-offline-settings', d: 'בהכתבה אופליין, כשמודל""",
"""      { n: 'פיסוק AI בהכתבה', s: '#tb-offline-settings', d: 'בהכתבה (אופליין וגם דרך האינטרנט), כשמודל""")

MARK = "// פ-4: online dictation tells when its grey preview text is on screen"
NEED = {'mark': "// ---------- ו-1: real .docx export", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
