# ת-1: "🔍 גודל תצוגה" in the top row enlarges the whole program (buttons, bars, windows and text) — like the
# display size in the timesheet system. Four sizes; the choice is remembered. Print is not affected.
import os
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))
D = os.path.dirname(os.path.abspath(__file__))
SPM = open(os.path.join(D, 'spm_block.txt'), encoding='utf-8').read()

step('החלה מוקדמת (בלי הבהוב)',
"""<body>

<header>""",
"""<body>
<script>try { var uz = parseFloat(localStorage.getItem('heb-style-editor-ui-size-v1')); if (uz > 1 && uz <= 2){ document.documentElement.style.zoom = uz; document.documentElement.style.setProperty('--uiz', uz); } } catch (e) { /* ת-1 */ }</script>

<header>""")

step('כפתור בשורה העליונה',
"""    <button class="header-btn" id="theme-toggle">🌙 מצב כהה</button>""",
"""    <button class="header-btn" id="ui-size-btn" type="button" title="גודל תצוגה — מגדיל את כל התוכנה" aria-haspopup="menu">🔍 גודל תצוגה</button>
    <button class="header-btn" id="theme-toggle">🌙 מצב כהה</button>""")

# with the whole page enlarged, heights in vh/vw would grow too — divide them back
step('גובה הדף', """    min-height:100vh;
  }""", """    min-height:calc(100vh / var(--uiz, 1));
  }""")
step('גובה חלונות', """    max-width: 460px;
    max-height: 80vh;""", """    max-width: 460px;
    max-height: calc(80vh / var(--uiz, 1));""")
step('לוח העיצוב', """main.panel-open aside{ position:fixed; inset:0 0 0 auto; width:80vw; z-index:10; height:100vh; }""",
     """main.panel-open aside{ position:fixed; inset:0 0 0 auto; width:calc(80vw / var(--uiz, 1)); z-index:10; height:calc(100vh / var(--uiz, 1)); }""")
step('המילון שלי', """max-height:min(300px, 40vh);""", """max-height:min(300px, calc(40vh / var(--uiz, 1)));""")
step('קרדיט מילון', """.spell-credits-body{ max-height: 60vh;""", """.spell-credits-body{ max-height: calc(60vh / var(--uiz, 1));""")
step('המדריך', """.guide-box{ width:calc(100% - 24px); max-width:640px; height:min(80vh, 760px); max-height:80vh; }""",
     """.guide-box{ width:calc(100% - 24px); max-width:640px; height:min(calc(80vh / var(--uiz, 1)), 760px); max-height:calc(80vh / var(--uiz, 1)); }""")
step('הדפסה ועיצוב התפריט', """  /* ---- Print ---- */
  @media print{""", """  /* ת-1: display size menu */
  .ui-size-menu{ position:fixed; z-index:3000; background: var(--panel); border:1px solid var(--line); border-radius:6px; padding:4px; box-shadow:0 8px 24px rgba(0,0,0,.35); min-width:150px; }
  .ui-size-menu button{ display:flex; gap:8px; align-items:center; width:100%; background:none; border:none; color: var(--parchment); padding:7px 10px; border-radius:4px; cursor:pointer; font: inherit; font-size:14px; text-align:right; }
  .ui-size-menu button:hover, .ui-size-menu button:focus{ background: var(--panel-2, rgba(128,128,128,.15)); outline:none; }
  .ui-size-menu .mk{ width:14px; color: var(--brass); }
  .ui-size-menu .pc{ margin-inline-start:auto; color: var(--parchment-dim); font-size:12px; }
  /* ---- Print ---- */
  @media print{
    html{ zoom:1 !important; }""")

# popups placed by screen position: the browser multiplies their position by the zoom, so it is divided back
spm = SPM.replace("  const vh = window.innerHeight, vw = window.innerWidth;", "  const vh = window.innerHeight, vw = window.innerWidth, Z = uiZoom();   // ת-1")
spm = spm.replace("  const h = menu.offsetHeight;", "  const h = menu.offsetHeight * Z;")
spm = spm.replace("menu.style.maxHeight = room + 'px';", "menu.style.maxHeight = (room / Z) + 'px';")
spm = spm.replace("const hh = menu.offsetHeight;", "const hh = menu.offsetHeight * Z;")
spm = spm.replace("vh - menu.offsetHeight - EDGE", "vh - menu.offsetHeight * Z - EDGE")
spm = spm.replace("  const w = menu.offsetWidth;", "  const w = menu.offsetWidth * Z;")
spm = spm.replace("menu.style.left = Math.max(EDGE, Math.min(x - w, vw - w - EDGE)) + 'px';", "menu.style.left = (Math.max(EDGE, Math.min(x - w, vw - w - EDGE)) / Z) + 'px';")
spm = spm.replace("  menu.style.top = top + 'px';\n}", "  menu.style.top = (top / Z) + 'px';\n}")
assert spm.count('Z') >= 9, spm
step('תפריט איות', SPM, spm)
step('תפריט רמת איות: מידות', """const w = menu.offsetWidth, h = menu.offsetHeight;
    let left = r.right - w, top = r.bottom + 4;""", """const Z = uiZoom(), w = menu.offsetWidth * Z, h = menu.offsetHeight * Z;   // ת-1
    let left = r.right - w, top = r.bottom + 4;""")
step('תפריט רמת איות: מיקום', """    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
    b.setAttribute('aria-expanded', 'true');""", """    menu.style.left = (left / Z) + 'px';
    menu.style.top = (top / Z) + 'px';
    b.setAttribute('aria-expanded', 'true');""")
step('תפריט "/"', """if (top + pr.height > window.innerHeight - 8) top = rect.top - pr.height - 6;
  popup.style.left = left + 'px';
  popup.style.top = top + 'px';""", """if (top + pr.height > window.innerHeight - 8) top = rect.top - pr.height - 6;
  popup.style.left = (left / uiZoom()) + 'px';   // ת-1
  popup.style.top = (top / uiZoom()) + 'px';""")
step('חלון עיגולי ההדבקה', """popup.style.left = left + 'px';
  popup.style.top = top + 'px';

  activePastePopup""", """popup.style.left = (left / uiZoom()) + 'px';   // ת-1
  popup.style.top = (top / uiZoom()) + 'px';

  activePastePopup""")

step('מנוע גודל התצוגה', """// ---------- Footer actions ----------""", """// ---------- ת-1: display size of the whole program ----------
function uiZoom(){ const z = parseFloat(document.documentElement.style.zoom); return z > 0 ? z : 1; }
const UiSize = (function(){
  const KEY = 'heb-style-editor-ui-size-v1';
  const SIZES = [{ v: 1, l: 'רגיל' }, { v: 1.15, l: 'גדול' }, { v: 1.3, l: 'גדול מאוד' }, { v: 1.5, l: 'ענק' }];
  const btn = document.getElementById('ui-size-btn');
  let menu = null;
  function set(v){
    v = SIZES.some(s => s.v === v) ? v : 1;
    const root = document.documentElement;
    if (v === 1){ root.style.zoom = ''; root.style.removeProperty('--uiz'); }
    else { root.style.zoom = v; root.style.setProperty('--uiz', v); }
    try { localStorage.setItem(KEY, String(v)); } catch (e) { /* ignore */ }
    window.dispatchEvent(new Event('resize'));   // page-break lines and the like are drawn again
  }
  function close(){ if (menu){ menu.remove(); menu = null; btn.setAttribute('aria-expanded', 'false'); } }
  function open(){
    close();
    const cur = uiZoom();
    menu = document.createElement('div'); menu.className = 'ui-size-menu'; menu.setAttribute('role', 'menu');
    SIZES.forEach(s => {
      const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'menuitemradio');
      b.setAttribute('aria-checked', String(Math.abs(s.v - cur) < 0.01));
      b.innerHTML = '<span class="mk">' + (Math.abs(s.v - cur) < 0.01 ? '✓' : '') + '</span><span></span><span class="pc"></span>';
      b.children[1].textContent = s.l; b.children[2].textContent = Math.round(s.v * 100) + '%';
      b.onclick = () => { close(); set(s.v); flashStatus('גודל תצוגה: ' + s.l); };
      menu.appendChild(b);
    });
    document.body.appendChild(menu);
    const r = btn.getBoundingClientRect(), Z = uiZoom(), w = menu.offsetWidth * Z;
    let left = r.right - w; if (left < 6) left = 6;
    menu.style.left = (left / Z) + 'px'; menu.style.top = ((r.bottom + 4) / Z) + 'px';
    btn.setAttribute('aria-expanded', 'true');
    const first = menu.querySelector('[aria-checked="true"]') || menu.firstChild; first.focus();
  }
  btn.onclick = (e) => { e.stopPropagation(); menu ? close() : open(); };
  document.addEventListener('click', (e) => { if (menu && !menu.contains(e.target)) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menu){ e.preventDefault(); close(); btn.focus(); } });
  return { set, get: uiZoom, SIZES };
})();
window.UiSize = UiSize;

// ---------- Footer actions ----------""")

step('מדריך', """      { n: '🌙 מצב כהה / בהיר'""", """      { n: '🔍 גודל תצוגה', s: '#ui-size-btn', d: 'מגדיל את כל התוכנה — כפתורים, סרגלים, חלונות וטקסט: רגיל, גדול (115%), גדול מאוד (130%) או ענק (150%). הבחירה נשמרת. ההדפסה לא משתנה. (הזום שליד מספר העמוד מגדיל רק את דף המסמך.)' },
      { n: '🌙 מצב כהה / בהיר'""")

MARK = "// ---------- ת-1: display size of the whole program"
NEED = {'mark': "// פ-4: online dictation tells when its grey preview text is on screen", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
