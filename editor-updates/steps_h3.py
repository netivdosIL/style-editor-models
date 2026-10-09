# ה-3: proofreading catches real-word slips and marks less by mistake.
#  • a correct-but-rare word that is one slip away from a much more common word (הלח/הלך, מאנין/מעניין) is checked
#    in its sentence like אם/עם — marked (or replaced) only when the sentence clearly wants the common word
#  • a rare word that the spell checker doubts (שיחקו) gets a blue mark only when the model clearly prefers another word
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

step('מילים נדירות שקרובות למילה נפוצה',
"""    if (confusionMap.has(w)) return 'confusion';
    if (spellOk() && !(typeof isHebrewNumeralWord === 'function' && isHebrewNumeralWord(w)) && !spellIsKnown(w)) return 'spell';
    return null;
  }""",
"""    if (confusionMap.has(w)) return 'confusion';
    if (spellOk() && !(typeof isHebrewNumeralWord === 'function' && isHebrewNumeralWord(w)) && !spellIsKnown(w))
      return (typeof spellBaseDict !== 'undefined' && spellBaseDict.has(w)) ? 'spell-rare' : 'spell';   // ה-3: a real but rare word
    if (spellOk() && typeof spellFreqClass === 'function' && w.length >= 3 && !(typeof isHebrewNumeralWord === 'function' && isHebrewNumeralWord(w))){
      const c = spellFreqClass(w);
      if (c > 0 && c <= NEAR_MAX_CLASS && nearAlts(w, c).length) return 'near';                           // ה-3: הלח → הלך
    }
    return null;
  }
  // ה-3: common words one slip away from a rarer one (at least NEAR_GAP frequency classes more common)
  const NEAR_MAX_CLASS = 5, NEAR_GAP = 2, nearCache = new Map();
  function nearAlts(w, c){
    if (nearCache.has(w)) return nearCache.get(w);
    let alts = [];
    try { alts = spellSuggest(w, 5).filter(a => a !== w && spellFreqClass(a) >= c + NEAR_GAP).slice(0, 3); } catch (e) { alts = []; }
    if (nearCache.size > 5000) nearCache.clear();
    nearCache.set(w, alts);
    return alts;
  }""")

step('חלופות לפי סוג',
"""      const alts = kind === 'confusion' ? Array.from(confusionMap.get(t.core)) : spellSuggest(t.core, 5);
      if (!alts.length) return;
      out.push({ tokenIndex: i, kind, start: t.coreStart, end: t.coreEnd, word: t.core, alts });""",
"""      const alts = kind === 'confusion' ? Array.from(confusionMap.get(t.core))
                 : kind === 'near' ? nearAlts(t.core, spellFreqClass(t.core)) : spellSuggest(t.core, 5);
      if (!alts.length) return;
      // ה-3: "near" behaves like a confusion pair; "spell-rare" is still a spelling item, but needs the model's support
      const shown = kind === 'near' ? 'confusion' : kind === 'spell-rare' ? 'spell' : kind;
      out.push({ tokenIndex: i, kind: shown, rule: kind, start: t.coreStart, end: t.coreEnd, word: t.core, alts });""")

step('החלטה',
"""    if (kind === 'confusion'){ if (delta >= th.replace) action = 'replace'; else if (delta >= th.mark) action = 'mark'; }
    else { if (delta >= th.mark && gap >= th.spellGap) action = 'replace'; else action = 'mark'; }   // a red word is marked anyway""",
"""    if (kind === 'confusion' || kind === 'near'){ if (delta >= th.replace) action = 'replace'; else if (delta >= th.mark) action = 'mark'; }
    else if (kind === 'spell-rare'){ if (delta >= th.mark && gap >= th.spellGap) action = 'replace'; else if (delta >= th.mark) action = 'mark'; }   // ה-3
    else { if (delta >= th.mark && gap >= th.spellGap) action = 'replace'; else action = 'mark'; }   // a red word is marked anyway""")

step('החלטה לפי הכלל',
"""        const d = decide(s.kind, ranked, thFor(level));""",
"""        const d = decide(s.rule || s.kind, ranked, thFor(level));""")
step('אישור לפי הכלל',
"""          const d2 = decide(s.kind, r2, thFor(confirmLevel));""",
"""          const d2 = decide(s.rule || s.kind, r2, thFor(confirmLevel));""")

MARK = "// ה-3: common words one slip away from a rarer one"
NEED = {'mark': "// ---- ה-2: load the model in the background", 'msg': 'קודם צריך להחיל את העדכון המאוחד (update-all.html).'}
