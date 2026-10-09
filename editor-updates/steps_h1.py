# ה-1: fast typing in long documents. The editor used to replace its whole HTML on every keystroke, so the browser
# laid out the whole document again. Now each line is its own span(s), and only the lines that changed are replaced
# (unchanged nodes at the start and the end are kept), so typing costs about the same in a long document as in a short one.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('שורה = יחידה נפרדת',
"""    } else if (!ltrStarts){
      html += `<span style="${styleAttrForRun(seg.style)}">${escapeHtml(chunk).replace(/\\n/g, '<br>')}</span>`;
    } else {""",
"""    } else if (!ltrStarts){
      // ה-1: one span per line piece (the <br> between them), so a change in one line leaves the others' nodes alone
      const style = styleAttrForRun(seg.style);
      const parts = chunk.split('\\n');
      for (let k = 0; k < parts.length; k++){
        if (k > 0) html += '<br>';
        if (parts[k]) html += `<span style="${style}">${escapeHtml(parts[k])}</span>`;
      }
    } else {""")

step('עדכון חלקי של העורך',
"""function renderTextIntoEditor(text, caretPos){
  const html = buildStyledHtml(text);
  editor.innerHTML = html || '';""",
"""// ה-1: replaces only the part of the editor that differs — the nodes that are equal at the start and at the end stay
const patchTpl = document.createElement('template');
function patchEditorHtml(html){
  patchTpl.innerHTML = html;
  const fresh = patchTpl.content, nk = fresh.childNodes, ok = editor.childNodes;
  if (!ok.length || !nk.length){ editor.innerHTML = html; return; }
  let a = 0;
  const max = Math.min(nk.length, ok.length);
  while (a < max && ok[a].isEqualNode(nk[a])) a++;
  let b = 0;
  while (b < max - a && ok[ok.length - 1 - b].isEqualNode(nk[nk.length - 1 - b])) b++;
  if (a === ok.length && a === nk.length) return;      // nothing changed
  const oldEnd = ok.length - b;
  for (let i = oldEnd - 1; i >= a; i--) editor.removeChild(ok[i]);
  const ref = editor.childNodes[a] || null;
  const mid = document.createDocumentFragment();
  while (fresh.childNodes.length > a + b) mid.appendChild(fresh.childNodes[a]);
  editor.insertBefore(mid, ref);
}
function renderTextIntoEditor(text, caretPos){
  const html = buildStyledHtml(text);
  patchEditorHtml(html || '');""")

step('טקסט העורך נשמר עד שמשהו משתנה',
"""function extractPlainText(root){
  let text = '';""",
"""// ה-1: the editor's text is reused until its DOM changes — takeRecords() tells synchronously whether anything changed
let ptCache = null, ptObserver = null;
function extractPlainText(root){
  if (root && root.id === 'editor' && typeof MutationObserver === 'function'){
    if (!ptObserver){
      ptObserver = new MutationObserver(() => { ptCache = null; });
      ptObserver.observe(root, { childList: true, subtree: true, characterData: true, attributes: true });
    }
    if (ptObserver.takeRecords().length) ptCache = null;
    if (ptCache === null) ptCache = extractPlainTextRaw(root);
    return ptCache;
  }
  return extractPlainTextRaw(root);
}
function extractPlainTextRaw(root){
  let text = '';""")

step('ספירת מילים אחרי הפסקה קצרה',
"""function updateWordCount(){
  const el = document.getElementById('word-count');
  if (!el) return;
  const n = documentWordCount();""",
"""let wordCountTimer = null;
function updateWordCount(){   // ה-1: counted once typing pauses for a moment, not on every key
  clearTimeout(wordCountTimer);
  wordCountTimer = setTimeout(updateWordCountNow, 250);
}
function updateWordCountNow(){
  const el = document.getElementById('word-count');
  if (!el) return;
  const n = documentWordCount();""")

step('בדיקת איות: רק השורה שהשתנתה',
"""function spellFindErrors(text){
  const out = [];
  SPELL_WORD_RE.lastIndex = 0;""",
"""// ה-1: results are remembered per line, so a keystroke rechecks only its own line. The memory is cleared when the
// dictionary, the level, "המילון שלי" or "התעלם" change.
var spellLineCache = new Map(), spellLineSalt = '';
function spellFindErrors(text){
  const salt = spellDictState + '|' + spellStrictCache + '|' + spellUserDict.size + '|' + spellIgnored.size + '|' + spellBaseDict.size;
  if (salt !== spellLineSalt || spellLineCache.size > 20000){ spellLineCache.clear(); spellLineSalt = salt; }
  const out = [];
  let pos = 0;
  for (const line of text.split('\\n')){
    let found = spellLineCache.get(line);
    if (!found){ found = spellFindErrorsIn(line); spellLineCache.set(line, found); }
    for (const er of found) out.push({ start: er.start + pos, end: er.end + pos, word: er.word });
    pos += line.length + 1;
  }
  return out;
}
function spellFindErrorsIn(text){
  const out = [];
  SPELL_WORD_RE.lastIndex = 0;""")

MARK = "// ה-1: replaces only the part of the editor that differs"
NEED = {'mark': "// ---------- א-1: the files live in IndexedDB", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
