# ג-5: only "עברית מדויק" stays. Tiny/Base and the two experimental switches leave the UI;
# their stored files are removed once the Hebrew model is installed.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('רשימת המודלים: רק עברית',
"""    tiny: { label: 'Tiny', desc: 'מהיר', archive: 'sherpa-onnx-whisper-tiny.tar.bz2', size: '116MB' },
    base: { label: 'Base', desc: 'מדויק יותר, איטי יותר', archive: 'sherpa-onnx-whisper-base.tar.bz2', size: '208MB' },
    // ג-1: Hebrew speech model GigaAM-He (MIT) — 5 parts + a list of their checksums, from our own GitHub release
    he: { label: 'עברית מדויק', desc: 'מודל עברי, מדויק ומהיר · מומלץ', kind: 'ctc', size: '236MB',""",
"""    // ג-5: the only model now — Hebrew speech model GigaAM-He (MIT), 5 parts + a list of their checksums, from our own GitHub release
    he: { label: 'עברית מדויק', desc: 'מודל זיהוי דיבור שאומן על עברית', kind: 'ctc', size: '236MB',""")

step('מודל ברירת מחדל',
"""    try { const m = localStorage.getItem(MODEL_KEY); if (MODELS[m]) return m; } catch (e) { /* ignore */ }
    return 'tiny';""",
"""    try { const m = localStorage.getItem(MODEL_KEY); if (MODELS[m]) return m; } catch (e) { /* ignore */ }
    return 'he';""")

step('אחרי מחיקה',
"""      if (getActiveModel() === id) setActiveModel('tiny');""",
"""      if (getActiveModel() === id) setActiveModel('he');""")

step('ניקוי Tiny/Base',
"""  // ---- listening indicator: an ear with sound waves flowing in; bouncing dots while it "thinks" ----""",
"""  // ג-5: Tiny/Base are gone from the editor; once "עברית מדויק" is installed, their old files are removed to free space
  setTimeout(async () => {
    try {
      if (!(await getStatus('he')).complete) return;
      for (const id of ['tiny', 'base']) for (const k of KINDS.concat(['encoderF'])) await dbDel(id + '/' + k);
    } catch (e) { /* storage not available: nothing to clean */ }
  }, 4000);

  // ---- listening indicator: an ear with sound waves flowing in; bouncing dots while it "thinks" ----""")

step('חלון: בלי האפשרויות הניסיוניות',
"""      <label class="spoken-punct-row ov-gpu-row"><input type="checkbox" id="ov-gpu-toggle"> ⚡ האצה בכרטיס מסך (ניסיוני)</label>
      <div id="ov-gpu-info" hidden></div>
      <label class="spoken-punct-row ov-gpu-row"><input type="checkbox" id="ov-short-toggle"> ✂️ חלון קצר (ניסיוני)</label>
      <div id="ov-short-info" hidden></div>
""",
"""""")

step('כיתוב כפתור ההגדרות',
"""id="tb-offline-settings" title="הגדרות הקלדה קולית אופליין — בחירת מודל וקבצים" type="button">""",
"""id="tb-offline-settings" title="הגדרות הקלדה קולית אופליין — התקנת המודל והגדרות" type="button">""")

step('התקנה מתיקייה: רק עברית',
"""    { id: 'tiny',    label: 'הקלדה קולית — Tiny', file: 'sherpa-onnx-whisper-tiny.tar.bz2' },
    { id: 'base',    label: 'הקלדה קולית — Base', file: 'sherpa-onnx-whisper-base.tar.bz2' },
    { id: 'he',      label: 'הקלדה קולית — עברית מדויק', file: 'hebrew-gigaam-int8.zip.part01–05 + parts.json' }""",
"""    { id: 'he',      label: 'הקלדה קולית — עברית מדויק', file: 'hebrew-gigaam-int8.zip.part01–05 + parts.json' }""")

step('מדריך: הגדרות אופליין',
"""      { n: '⚙️ הגדרות אופליין', s: '#tb-offline-settings', d: 'בחירת המודל: "עברית מדויק" (מומלץ — מודל עברי, מדויק ומהיר), Tiny (מהיר) או Base. "הורד והתקן" לפעם הראשונה. כשההורדה מסתיימת לוחצים "בחר את הקובץ שהורד". אם ההורדה לא התחילה, יש מתחת למודל קישור חלופי.' },""",
"""      { n: '⚙️ הגדרות אופליין', s: '#tb-offline-settings', d: 'התקנת המודל "עברית מדויק": "הורד והתקן" לפעם הראשונה, וכשההורדה מסתיימת "בחר את הקובץ שהורד". אם ההורדה לא התחילה, יש מתחת למודל קישור חלופי. כאן גם מפעילים ומכבים את פקודות הפיסוק בדיבור.' },""")

step('מדריך: בלי כרטיס מסך',
"""      { n: '⚡ האצה בכרטיס מסך', s: '#tb-offline-settings', d: 'בחלון ⚙️ (ניסיוני): מריץ את החלק הכבד של הזיהוי על כרטיס המסך. בפעם הראשונה בוחרים שוב את קובץ המודל שהורד, ויורד רכיב הרצה נוסף. אם זה לא מצליח, ההקלדה ממשיכה על המעבד. רק ל-Tiny ול-Base; "עברית מדויק" מהיר גם בלי זה.' },
""",
"""""")

step('מדריך: בלי חלון קצר',
"""      { n: '✂️ חלון קצר (ניסיוני)', s: '#tb-offline-settings', d: 'בחלון ⚙️: כל משפט מעובד לפי האורך שלו במקום בחלון קבוע של 30 שניות, ולכן ההקלדה האופליין מהירה בהרבה. אם הזיהוי נעשה פחות מדויק, מכבים. רק ל-Tiny ול-Base.' },
""",
"""""")

step('מדריך: התקנה מחדש',
"""בפעם הראשונה מתקינים שוב את המודלים (📂 התקן מתיקייה)""",
"""בפעם הראשונה מתקינים שוב את המודל (📂 התקן מתיקייה)""")

MARK = "// ג-5: the only model now"
NEED = {'mark': "const GH_HE = 'https://github.com/netivdosIL/style-editor-models/releases/download/gigaam-he-v2/';",
        'msg': 'קודם צריך להחיל את העדכון "עברית מדויק" (update-he-all.html).'}
