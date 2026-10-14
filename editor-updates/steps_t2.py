# ת-2: display size as a slider (70%–200%) instead of four fixed sizes, a full-screen button, and a fix for older
# Chrome/Edge (Windows 7 = version 109): before Chrome 128 the browser reported element positions without the page
# zoom, so menus opened in the wrong place and clicks missed. There, positions are now converted to screen pixels,
# the way new browsers report them, so the rest of the editor works the same in both.
import os
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))
D = os.path.dirname(os.path.abspath(__file__))
OLD = open(os.path.join(D, 'uisize_old.txt'), encoding='utf-8').read()

step('החלה מוקדמת + תיקון לדפדפן ישן',
r"""<script>try { var uz = parseFloat(localStorage.getItem('heb-style-editor-ui-size-v1')); if (uz > 1 && uz <= 2){ document.documentElement.style.zoom = uz; document.documentElement.style.setProperty('--uiz', uz); } } catch (e) { /* ת-1 */ }</script>""",
r"""<script>try { var uz = parseFloat(localStorage.getItem('heb-style-editor-ui-size-v1')); if (uz >= 0.7 && uz <= 2 && uz !== 1){ document.documentElement.style.zoom = uz; document.documentElement.style.setProperty('--uiz', uz); } } catch (e) { /* ת-1 */ }</script>
<script>
// ת-2: Chrome/Edge before 128 (Windows 7 stays on 109) report positions without the page zoom — convert them to
// screen pixels like new browsers do, so menus, the caret and clicks line up at every display size
(function(){
  try {
    var pr = document.createElement('div');
    pr.style.cssText = 'position:absolute;visibility:hidden;width:100px;height:1px;zoom:2;top:0;left:0';
    document.documentElement.appendChild(pr);
    var legacy = pr.getBoundingClientRect().width < 150;
    pr.remove();
    window.__legacyZoom = legacy;
    if (!legacy) return;
    var Z = function(){ var z = parseFloat(document.documentElement.style.zoom); return z > 0 ? z : 1; };
    var scale = function(r, z){ return new DOMRect(r.x * z, r.y * z, r.width * z, r.height * z); };
    [Element.prototype, Range.prototype].forEach(function(P){
      var gb = P.getBoundingClientRect, gc = P.getClientRects;
      P.getBoundingClientRect = function(){ var r = gb.call(this), z = Z(); return z === 1 ? r : scale(r, z); };
      P.getClientRects = function(){ var l = gc.call(this), z = Z(); if (z === 1) return l;
        var out = []; for (var i = 0; i < l.length; i++) out.push(scale(l[i], z)); out.item = function(k){ return this[k] || null; }; return out; };
    });
  } catch (e) { /* ignore */ }
})();
</script>""")

step('כפתור מסך מלא בשורה העליונה',
r"""    <button class="header-btn" id="ui-size-btn" type="button" title="גודל תצוגה — מגדיל את כל התוכנה" aria-haspopup="menu">🔍 גודל תצוגה</button>""",
r"""    <button class="header-btn" id="ui-size-btn" type="button" title="גודל תצוגה — מגדיל את כל התוכנה" aria-haspopup="dialog">🔍 גודל תצוגה</button>
    <button class="header-btn fs-btn" id="fullscreen-btn" type="button" title="מסך מלא (F11) — העורך ממלא את כל המסך" aria-label="מסך מלא"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 5.5v-4h4M10.5 1.5h4v4M14.5 10.5v4h-4M5.5 14.5h-4v-4"/></svg></button>""")

step('עיצוב הפס',
r"""  .ui-size-menu .pc{ margin-inline-start:auto; color: var(--parchment-dim); font-size:12px; }""",
r"""  .ui-size-menu .pc{ margin-inline-start:auto; color: var(--parchment-dim); font-size:12px; }
  /* ת-2: the slider panel and the full-screen button */
  .ui-size-menu.slider{ min-width:270px; padding:10px 12px 8px; }
  .uz-head{ display:flex; align-items:baseline; justify-content:space-between; font-size:13px; color: var(--parchment-dim); margin-bottom:6px; }
  .uz-val{ font-size:17px; font-weight:700; color: var(--brass-bright); min-width:52px; text-align:left; direction:ltr; }
  .uz-row{ display:flex; align-items:flex-start; gap:6px; direction:ltr; }
  .uz-track{ flex:1; min-width:0; position:relative; padding-bottom:16px; }
  .ui-size-menu .uz-row button{ width:30px; height:30px; padding:0; justify-content:center; font-size:18px; font-weight:700; border:1px solid var(--line); flex:none; }
  .uz-range{ width:100%; margin:7px 0 0; accent-color: var(--brass); cursor:pointer; }
  .uz-tick{ position:absolute; bottom:0; transform:translateX(-50%); font-size:10.5px; color: var(--parchment-dim); white-space:nowrap; }
  .uz-foot{ display:flex; gap:6px; margin-top:8px; border-top:1px solid var(--line); padding-top:8px; }
  .ui-size-menu .uz-foot button{ flex:1; justify-content:center; border:1px solid var(--line); font-size:13px; padding:6px 8px; }
  .ui-size-menu .uz-foot svg, .fs-btn svg{ width:14px; height:14px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; flex:none; }
  .fs-btn{ display:inline-flex; align-items:center; justify-content:center; padding-left:9px !important; padding-right:9px !important; }""")

NEW = r"""const UiSize = (function(){
  // ת-2: any size from 70% to 200% with a slider; the four old sizes are marks on it
  const KEY = 'heb-style-editor-ui-size-v1', MIN = 0.7, MAX = 2, STEP = 0.05;
  const SIZES = [{ v: 1, l: 'רגיל' }, { v: 1.15, l: 'גדול' }, { v: 1.3, l: 'גדול מאוד' }, { v: 1.5, l: 'ענק' }];
  const btn = document.getElementById('ui-size-btn');
  let menu = null;
  const clamp = (v) => Math.min(MAX, Math.max(MIN, Math.round((+v || 1) / STEP) * STEP));
  const pct = (v) => Math.round(v * 100) + '%';
  function set(v){
    v = clamp(v);
    const root = document.documentElement;
    if (Math.abs(v - 1) < 0.001){ v = 1; root.style.zoom = ''; root.style.removeProperty('--uiz'); }
    else { root.style.zoom = v; root.style.setProperty('--uiz', v); }
    try { localStorage.setItem(KEY, String(v)); } catch (e) { /* ignore */ }
    window.dispatchEvent(new Event('resize'));   // page-break lines and the like are drawn again
    if (menu) place();
    return v;
  }
  function close(){ if (menu){ menu.remove(); menu = null; btn.setAttribute('aria-expanded', 'false'); } }
  function place(){
    const r = btn.getBoundingClientRect(), Z = uiZoom(), w = menu.offsetWidth * Z;
    let left = r.right - w; if (left < 6) left = 6;
    if (left + w > window.innerWidth - 6) left = Math.max(6, window.innerWidth - 6 - w);
    menu.style.left = (left / Z) + 'px'; menu.style.top = ((r.bottom + 4) / Z) + 'px';
  }
  function open(){
    close();
    menu = document.createElement('div'); menu.className = 'ui-size-menu slider'; menu.setAttribute('role', 'dialog'); menu.setAttribute('aria-label', 'גודל תצוגה');
    menu.innerHTML = '<div class="uz-head"><span>גודל תצוגה של כל התוכנה</span><span class="uz-val"></span></div>'
      + '<div class="uz-row"><button type="button" class="uz-minus" title="הקטן" aria-label="הקטן">−</button>'
      + '<div class="uz-track"><input type="range" class="uz-range" min="' + MIN * 100 + '" max="' + MAX * 100 + '" step="' + STEP * 100 + '" aria-label="גודל תצוגה באחוזים">'
      + [70, 100, 150, 200].map(t => { const f = (t - MIN * 100) / ((MAX - MIN) * 100);   // under the thumb's centre at that value
          return '<span class="uz-tick" style="left:calc(' + (f * 100).toFixed(2) + '% + ' + (8 - 16 * f).toFixed(1) + 'px)">' + t + '%</span>'; }).join('')
      + '</div><button type="button" class="uz-plus" title="הגדל" aria-label="הגדל">+</button></div>'
      + '<div class="uz-foot"><button type="button" class="uz-reset">רגיל (100%)</button>'
      + '<button type="button" class="uz-fs"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 5.5v-4h4M10.5 1.5h4v4M14.5 10.5v4h-4M5.5 14.5h-4v-4"/></svg><span></span></button></div>';
    const range = menu.querySelector('.uz-range'), val = menu.querySelector('.uz-val');
    const show = (v) => { val.textContent = pct(v); range.value = Math.round(v * 100); };
    show(uiZoom());
    // while dragging only the number changes (a page that grows under the mouse would move the slider away);
    // the size is applied when the mouse is let go, or at once with the keyboard, − / +
    range.addEventListener('input', () => { val.textContent = range.value + '%'; });
    range.addEventListener('change', () => { show(set(range.value / 100)); });
    menu.querySelector('.uz-minus').onclick = () => show(set(uiZoom() - 0.1));
    menu.querySelector('.uz-plus').onclick = () => show(set(uiZoom() + 0.1));
    menu.querySelector('.uz-reset').onclick = () => show(set(1));
    const fsb = menu.querySelector('.uz-fs');
    const fsLabel = () => { fsb.querySelector('span').textContent = FullScreen.isOn() ? 'יציאה ממסך מלא' : 'מסך מלא'; };
    fsLabel();
    fsb.onclick = () => { FullScreen.toggle(); setTimeout(fsLabel, 300); };
    document.body.appendChild(menu);
    place();
    btn.setAttribute('aria-expanded', 'true');
    range.focus();
  }
  btn.onclick = (e) => { e.stopPropagation(); menu ? close() : open(); };
  document.addEventListener('mousedown', (e) => { if (menu && !menu.contains(e.target) && e.target !== btn && !btn.contains(e.target)) close(); }, true);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menu){ e.preventDefault(); close(); btn.focus(); } });
  return { set, get: uiZoom, SIZES, open, close, isOpen: () => !!menu };
})();

// ---------- ת-2: full screen (like F11) ----------
const FullScreen = (function(){
  const b = document.getElementById('fullscreen-btn');
  const el = document.documentElement;
  const isOn = () => !!(document.fullscreenElement || document.webkitFullscreenElement);
  function toggle(){
    try {
      if (isOn()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      else {
        const req = el.requestFullscreen || el.webkitRequestFullscreen;
        const p = req && req.call(el);
        if (p && p.catch) p.catch(() => flashStatus('הדפדפן לא אישר מסך מלא — אפשר ללחוץ F11'));
      }
    } catch (e) { flashStatus('הדפדפן לא אישר מסך מלא — אפשר ללחוץ F11'); }
  }
  function sync(){
    if (!b) return;
    const on = isOn();
    b.title = on ? 'יציאה ממסך מלא (Esc)' : 'מסך מלא (F11) — העורך ממלא את כל המסך';
    b.setAttribute('aria-label', on ? 'יציאה ממסך מלא' : 'מסך מלא');
    b.classList.toggle('on', on);
  }
  if (b) b.onclick = toggle;
  document.addEventListener('fullscreenchange', sync);
  document.addEventListener('webkitfullscreenchange', sync);
  return { toggle, isOn };
})();
window.FullScreen = FullScreen;
"""
step('מנוע גודל התצוגה: פס', OLD, NEW)

step('מדריך',
r"""      { n: '🔍 גודל תצוגה', s: '#ui-size-btn', d: 'מגדיל את כל התוכנה — כפתורים, סרגלים, חלונות וטקסט: רגיל, גדול (115%), גדול מאוד (130%) או ענק (150%). הבחירה נשמרת. ההדפסה לא משתנה. (הזום שליד מספר העמוד מגדיל רק את דף המסמך.)' },""",
r"""      { n: '🔍 גודל תצוגה', s: '#ui-size-btn', d: 'מגדיל או מקטין את כל התוכנה — כפתורים, סרגלים, חלונות וטקסט — בפס גרירה מ-70% עד 200% (או בכפתורי − ו-+). "רגיל (100%)" מחזיר לגודל הרגיל. הבחירה נשמרת. ההדפסה לא משתנה. (הזום שליד מספר העמוד מגדיל רק את דף המסמך.)' },
      { n: 'מסך מלא', s: '#fullscreen-btn', d: 'הכפתור עם ארבע הפינות שליד "🔍 גודל תצוגה" (וגם בתוך חלון גודל התצוגה): העורך ממלא את כל המסך, בלי שורת הכתובת והלשוניות של הדפדפן — כמו F11. יציאה: Esc או לחיצה נוספת.' },""")

MARK = "// ---------- ת-2: full screen (like F11)"
NEED = {'mark': "// ---------- ת-1: display size of the whole program", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
