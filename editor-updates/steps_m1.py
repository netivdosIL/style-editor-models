# מ-1: permanent microphone permission — the offline settings window can download mic_allow.reg / mic_undo.reg
# (Chrome/Edge policy AudioCaptureAllowedUrls = file:///*), so customers get it from inside the editor.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('קטע בחלון ההגדרות',
"""      <button type="button" class="folder-install-btn" id="ov-measure-btn">⏱️ מדידת מהירות</button>""",
"""      <div class="ov-mic-perm">
        <div class="ov-mic-title">🎤 אישור קבוע למיקרופון</div>
        <div class="ov-mic-note">כדי שהדפדפן לא ישאל כל פעם על המיקרופון: מורידים את הקובץ, לוחצים עליו פעמיים ומאשרים, ואז סוגרים את הדפדפן לגמרי ופותחים מחדש. Windows ישאל אם לאשר שינוי ברישום — זה צפוי. מתאים לכרום ולאדג'.</div>
        <div class="ov-mic-btns"><button type="button" class="folder-install-btn" id="ov-mic-allow">⬇️ הורדת קובץ אישור</button><button type="button" class="folder-install-btn" id="ov-mic-undo">↩️ הורדת קובץ ביטול</button></div>
      </div>
      <button type="button" class="folder-install-btn" id="ov-measure-btn">⏱️ מדידת מהירות</button>""")

step('עיצוב הקטע',
"""  .ov-measure-tip{""",
"""  .ov-mic-perm{ margin-top:14px; padding-top:12px; border-top:1px solid var(--border, rgba(128,128,128,.3)); }
  .ov-mic-title{ font-size:14px; font-weight:600; color: var(--parchment); }
  .ov-mic-note{ font-size:12.5px; line-height:1.6; color: var(--parchment-dim); margin:4px 0 6px; }
  .ov-mic-btns{ display:flex; gap:8px; flex-wrap:wrap; }
  .ov-mic-btns .folder-install-btn{ margin-top:0; flex:1 1 140px; width:auto; }
  .ov-measure-tip{""")

step('הורדת הקבצים',
"""// ---------- Footer actions ----------""",
"""// ---------- מ-1: permanent microphone permission for the local editor file (Chrome / Edge policy) ----------
(function setupMicPermissionFiles(){
  const KEYS = ['HKEY_LOCAL_MACHINE\\\\SOFTWARE\\\\Policies\\\\Google\\\\Chrome', 'HKEY_LOCAL_MACHINE\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Edge',
                'HKEY_CURRENT_USER\\\\SOFTWARE\\\\Policies\\\\Google\\\\Chrome', 'HKEY_CURRENT_USER\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Edge'];
  const allow = ['Windows Registry Editor Version 5.00', '', '; Allow the microphone for local editor files (file:///) in Chrome and Edge', '']
    .concat(...KEYS.map(k => ['[' + k + '\\\\AudioCaptureAllowedUrls]', '"1"="file:///*"', ''])).join('\\r\\n') + '\\r\\n';
  const undo = ['Windows Registry Editor Version 5.00', '', '; Remove only the microphone permission added by mic_allow.reg', '']
    .concat(...KEYS.map(k => ['[-' + k + '\\\\AudioCaptureAllowedUrls]', ''])).join('\\r\\n') + '\\r\\n';
  const save = (name, text) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'application/octet-stream' }));
    a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 60000);
  };
  const b1 = document.getElementById('ov-mic-allow'), b2 = document.getElementById('ov-mic-undo');
  if (b1) b1.onclick = () => save('mic_allow.reg', allow);
  if (b2) b2.onclick = () => save('mic_undo.reg', undo);
})();

// ---------- Footer actions ----------""")

step('מדריך',
"""      { n: '⚙️ הגדרות אופליין', s: '#tb-offline-settings', d: 'התקנת המודל "עברית מדויק": "הורד והתקן" לפעם הראשונה, וכשההורדה מסתיימת "בחר את הקובץ שהורד". אם ההורדה לא התחילה, יש מתחת למודל קישור חלופי. כאן גם מפעילים ומכבים את פקודות הפיסוק בדיבור.' },""",
"""      { n: '⚙️ הגדרות אופליין', s: '#tb-offline-settings', d: 'התקנת המודל "עברית מדויק": "הורד והתקן" לפעם הראשונה, וכשההורדה מסתיימת "בחר את הקובץ שהורד". אם ההורדה לא התחילה, יש מתחת למודל קישור חלופי. כאן גם מפעילים ומכבים את פקודות הפיסוק בדיבור.' },
      { n: '🎤 אישור קבוע למיקרופון', s: '#tb-offline-settings', d: 'בחלון ⚙️: "הורדת קובץ אישור" מוריד קובץ קטן שמאשר לדפדפן (כרום או אדג\\') את המיקרופון לעורך באופן קבוע. לוחצים עליו פעמיים, מאשרים, וסוגרים ופותחים את הדפדפן. "הורדת קובץ ביטול" מחזיר את המצב הקודם.' },""")

MARK = "// ---------- מ-1: permanent microphone permission"
NEED = {'mark': "// ג-5: the only model now", 'msg': 'קודם צריך להחיל את העדכון "עברית מדויק" (update-he-all.html).'}
