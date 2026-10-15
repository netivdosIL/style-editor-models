# ה-4: offline dictation — a doubled letter from slow / drawn-out speech ("ספרדדים", "במרכזז") is fixed by the
# dictionary: a word that is not known, but is known with one of its doubled letters removed, gets that form.
# Real words with a double letter (ממש, הלל, ששון) are known and stay; doubled ו/י are left alone (שוויון, ביידא).
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('הפונקציה',
r"""// Puts a dictated chunk into text in place of [base, base+oldLen).""",
r"""// ---------- ה-4: doubled letters from slow speech in offline dictation ----------
function dictFixDoubles(text){
  if (!text || typeof spellIsKnown !== 'function' || spellDictState !== 'ready') return text;
  return text.replace(/[א-ת]{3,}/g, (w) => {
    if (!/([א-ת])\1/.test(w) || spellIsKnown(w)) return w;
    const pos = [];
    for (let i = 1; i < w.length; i++) if (w[i] === w[i - 1] && w[i] !== 'י' && w[i] !== 'ו') pos.push(i);
    if (!pos.length || pos.length > 4) return w;
    let best = null, bestScore = -1;
    for (let mask = 1; mask < (1 << pos.length); mask++){
      const drop = new Set(); pos.forEach((p, k) => { if (mask & (1 << k)) drop.add(p); });
      let v = ''; for (let i = 0; i < w.length; i++) if (!drop.has(i)) v += w[i];
      if (v.length < 2 || !spellIsKnown(v)) continue;
      const score = (spellFreqClass(v) || 3) * 10 - drop.size;
      if (score > bestScore){ bestScore = score; best = v; }
    }
    return best || w;
  });
}

// Puts a dictated chunk into text in place of [base, base+oldLen).""")

step('החלה בהכתבה אופליין',
r"""      case 'text': { const r = insertDictatedText(m.text + ' ');""",
r"""      case 'text': { const r = insertDictatedText(dictFixDoubles(m.text) + ' ');""")

MARK = "// ---------- ה-4: doubled letters from slow speech"
NEED = {'mark': "// ---------- ת-2: full screen (like F11)", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
