# ע-1: the two voice buttons become microphone icons (online: with waves; offline: plain). No text; the title tells.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

MIC = '<path d="M13 3.5a3 3 0 0 1 6 0v8a3 3 0 0 1-6 0z"/><path d="M9.5 11a6.5 6.5 0 0 0 13 0"/><path d="M16 17.5v3.5M12.5 21h7"/>'
WAVES = '<path class="mw" d="M6.5 6.5a8.5 8.5 0 0 0 0 9"/><path class="mw" d="M3 4a12.5 12.5 0 0 0 0 14"/><path class="mw" d="M25.5 6.5a8.5 8.5 0 0 1 0 9"/><path class="mw" d="M29 4a12.5 12.5 0 0 1 0 14"/>'
def icons(waves):
    return ('<svg class="mic-ico ico-idle" viewBox="0 0 32 23" aria-hidden="true">' + MIC + (WAVES if waves else '') + '</svg>'
            '<svg class="mic-ico ico-stop" viewBox="0 0 32 23" aria-hidden="true"><rect x="10.5" y="5" width="11" height="11" rx="2"/></svg>'
            '<svg class="mic-ico ico-load" viewBox="0 0 32 23" aria-hidden="true"><path d="M16 4a7 7 0 1 1-7 7"/></svg>')

step('עיצוב הסמלים',
"""  .mic-btn.offline{
    background: none;""",
"""  /* ע-1: microphone icons instead of text */
  .mic-btn .mic-ico{ width:26px; height:19px; fill:none; stroke:currentColor; stroke-width:1.9; stroke-linecap:round; stroke-linejoin:round; flex:none; }
  .mic-btn .mic-ico .mw{ stroke-width:1.6; opacity:.85; }
  .mic-btn .ico-stop{ fill:currentColor; stroke:none; }
  .mic-btn .ico-stop, .mic-btn .ico-load{ display:none; }
  .mic-btn.recording .ico-idle, .mic-btn.loading .ico-idle{ display:none; }
  .mic-btn.recording .ico-stop{ display:block; }
  .mic-btn.loading:not(.recording) .ico-load{ display:block; animation: mic-spin 0.9s linear infinite; }
  @keyframes mic-spin{ to{ transform: rotate(360deg); } }
  @media (prefers-reduced-motion: reduce){ .mic-btn.loading .ico-load{ animation:none; } }
  .mic-btn.offline{
    background: none;""")

step('גודל בסרגל',
"""  #toolbar .mic-btn{ height:30px; padding:0 12px; border-radius:5px; }""",
"""  #toolbar .mic-btn{ height:30px; padding:0 8px; border-radius:5px; justify-content:center; min-width:42px; }""")

step('כפתור אונליין',
"""    <button class="mic-btn" id="tb-mic" title="הקלדה קולית">🎤 הקלדה קולית</button>""",
"""    <button class="mic-btn" id="tb-mic" title="הקלדה קולית" aria-label="הקלדה קולית (דרך האינטרנט)">""" + icons(True) + """</button>""")

step('כפתור אופליין',
"""    <button class="mic-btn offline" id="tb-mic-offline" title="הקלדה קולית אופליין (פועלת בתוך המחשב, בלי אינטרנט)">🌐 אופליין</button>""",
"""    <button class="mic-btn offline" id="tb-mic-offline" title="הקלדה קולית אופליין (פועלת בתוך המחשב, בלי אינטרנט)" aria-label="הקלדה קולית אופליין">""" + icons(False) + """</button>""")

step('אונליין: כיתוב בזמן הקלטה',
"""    micBtn.title = 'ההקלטה פעילה — לחץ לעצירה';""",
"""    micBtn.title = 'ההקלטה פעילה — לחץ לעצירה';
    micBtn.setAttribute('aria-label', 'עצירת ההקלטה');""")
step('אונליין: כיתוב אחרי עצירה',
"""    micBtn.classList.remove('recording');
    micBtn.title = 'הקלדה קולית';""",
"""    micBtn.classList.remove('recording');
    micBtn.title = 'הקלדה קולית';
    micBtn.setAttribute('aria-label', 'הקלדה קולית (דרך האינטרנט)');""")

step('אופליין: מצב רגיל',
"""    btn.textContent = '🌐 אופליין';""",
"""    btn.title = 'הקלדה קולית אופליין (פועלת בתוך המחשב, בלי אינטרנט)'; btn.setAttribute('aria-label', 'הקלדה קולית אופליין');   // ע-1: the icon comes from CSS""")
step('אופליין: בזמן הקלטה',
"""    btn.textContent = '⏹️ עצור';""",
"""    btn.title = 'ההקלטה האופליין פעילה — לחץ לעצירה'; btn.setAttribute('aria-label', 'עצירת ההקלטה האופליין');""")

step('מדידה: טקסט',
"""      L.push('המנוע עוד לא נטען. סוגרים את החלון, לוחצים 🌐 אופליין ומכתיבים כמה משפטים.');""",
"""      L.push('המנוע עוד לא נטען. סוגרים את החלון, לוחצים על כפתור המיקרופון של האופליין ומכתיבים כמה משפטים.');""")

step('פתיחה: כפתורי הדוגמה',
"""<span class="wl-chip mic-btn">🎤 הקלדה קולית</span><span class="wl-chip mic-btn offline">🌐 אופליין</span>""",
"""<span class="wl-chip mic-btn">""" + icons(True) + """</span><span class="wl-chip mic-btn offline">""" + icons(False) + """</span>""")

step('מדריך: הקלדה קולית',
"""      { n: '🎤 הקלדה קולית', s: '#tb-mic', d: 'מדברים והטקסט נכתב. משתמשת במנוע ההכתבה של הדפדפן ודורשת אינטרנט.' },""",
"""      { n: 'הקלדה קולית באינטרנט (מיקרופון עם גלים)', s: '#tb-mic', d: 'מדברים והטקסט נכתב. משתמשת במנוע ההכתבה של הדפדפן ודורשת אינטרנט. בזמן ההקלטה הכפתור אדום עם ריבוע, ולחיצה עליו עוצרת.' },""")
step('מדריך: אופליין',
"""      { n: '🌐 אופליין', s: '#tb-mic-offline', d: 'הקלדה קולית שפועלת בתוך המחשב, בלי אינטרנט. סמל האוזן מראה מתי העורך מקשיב ומתי הוא מפענח. "⏹️ עצור" מסיים.' },""",
"""      { n: 'הקלדה קולית אופליין (מיקרופון בלי גלים)', s: '#tb-mic-offline', d: 'הקלדה קולית שפועלת בתוך המחשב, בלי אינטרנט. סמל האוזן מראה מתי העורך מקשיב ומתי הוא מפענח. בזמן ההקלטה הכפתור אדום עם ריבוע, ולחיצה עליו מסיימת. בזמן טעינת המודל מסתובב בו עיגול קטן.' },""")

MARK = '/* ע-1: microphone icons instead of text */'
NEED = {'mark': 'id="tb-mic-offline" title="הקלדה קולית אופליין (פועלת בתוך המחשב, בלי אינטרנט)"', 'msg': 'קודם צריך להחיל את העדכון "עברית מדויק" (update-he-all.html).'}
