# ג-2: the engine for the Hebrew model (GigaAM-He, character CTC) inside the existing offline dictation pipeline.
STEPS = []
def step(name, find, replace):
    STEPS.append((name, find, replace))

GIGA_CORE = r"""<script id="gigaam-offline-core">
/* ג-2: Hebrew speech model GigaAM-He (MIT; converted to ONNX int8) — log-mel front-end + greedy CTC.
   Same interface as WhisperOffline.createRecognizer, so the dictation engine can use either one.
   Feature settings (window, mel filterbank, hop...) come from model_info.json, exactly as in the original model. */
(function (root) {
  'use strict';
  const SR = 16000, MAX_SEG = 18 * SR;   // the model is trained on clips up to 20 s
  function f32(b64) { const s = atob(b64); const u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return new Float32Array(u.buffer); }

  function makeMel(F) {
    const nfft = F.n_fft, nf = F.n_freqs, nm = F.n_mels, wl = F.win_length, hop = F.hop_length;
    const win = f32(F.window_b64), fb = f32(F.mel_fb_b64);
    const w = new Float32Array(nfft), off = Math.floor((nfft - wl) / 2);
    for (let i = 0; i < wl; i++) w[off + i] = win[i];
    const cos = new Float32Array(nf * nfft), sin = new Float32Array(nf * nfft);
    for (let k = 0; k < nf; k++) for (let n = 0; n < nfft; n++) { const a = 2 * Math.PI * ((k * n) % nfft) / nfft; cos[k * nfft + n] = Math.cos(a); sin[k * nfft + n] = Math.sin(a); }
    const bands = [];
    for (let m = 0; m < nm; m++) { let lo = -1, hi = -1; for (let k = 0; k < nf; k++) if (fb[k * nm + m] !== 0) { if (lo < 0) lo = k; hi = k; } bands.push([Math.max(lo, 0), hi]); }
    const fr = new Float32Array(nfft), pw = new Float32Array(nf), lo = F.log_clamp_min, hi = F.log_clamp_max;
    return function logMel(x) {
      let sig = x;
      if (F.center) {
        const p = Math.floor(nfft / 2); sig = new Float32Array(x.length + 2 * p);
        for (let i = 0; i < sig.length; i++) { let j = i - p; if (j < 0) j = -j; if (j >= x.length) j = 2 * (x.length - 1) - j; sig[i] = x[Math.max(0, Math.min(x.length - 1, j))]; }
      }
      const T = Math.max(0, Math.floor((sig.length - nfft) / hop) + 1);
      const out = new Float32Array(nm * T);
      for (let t = 0; t < T; t++) {
        const b = t * hop;
        for (let n = 0; n < nfft; n++) fr[n] = sig[b + n] * w[n];
        for (let k = 0; k < nf; k++) {
          let re = 0, im = 0; const o = k * nfft;
          for (let n = 0; n < nfft; n++) { const v = fr[n]; re += v * cos[o + n]; im -= v * sin[o + n]; }
          pw[k] = re * re + im * im;
        }
        for (let m = 0; m < nm; m++) {
          let s = 0; const z = bands[m];
          for (let k = z[0]; k <= z[1]; k++) s += pw[k] * fb[k * nm + m];
          out[m * T + t] = Math.log(Math.min(Math.max(s, lo), hi));
        }
      }
      return { data: out, T, nm };
    };
  }

  // long speech: cut at the quietest point between 12 s and 18 s
  function cutPoints(x) {
    const cuts = [0];
    while (x.length - cuts[cuts.length - 1] > MAX_SEG) {
      const start = cuts[cuts.length - 1], a = start + 12 * SR, b = start + MAX_SEG;
      let best = b, bestE = Infinity;
      for (let p = a; p + 1600 <= b; p += 800) { let en = 0; for (let i = p; i < p + 1600; i++) en += x[i] * x[i]; if (en < bestE) { bestE = en; best = p + 800; } }
      cuts.push(best);
    }
    cuts.push(x.length);
    return cuts;
  }

  async function createRecognizer(ort, opts) {
    const info = opts.info, vocab = info.vocab, blank = info.blank_id;
    const sess = await ort.InferenceSession.create(opts.model, opts.sessionOptions || {});
    const logMel = makeMel(info.features);
    async function runFeatures(fe) {
      const r = await sess.run({
        features: new ort.Tensor('float32', fe.data, [1, fe.nm, fe.T]),
        feature_lengths: new ort.Tensor('int64', BigInt64Array.from([BigInt(fe.T)]), [1])
      });
      const lp = r.log_probs, O = lp.dims[1], V = lp.dims[2], d = lp.data;
      const ids = new Int32Array(O), best = new Float32Array(O);
      for (let t = 0; t < O; t++) { let bi = 0, bv = -Infinity; const o = t * V; for (let k = 0; k < V; k++) { const q = d[o + k]; if (q > bv) { bv = q; bi = k; } } ids[t] = bi; best[t] = bv; }
      return { ids, best };
    }
    function decode(ids, best, acc) {
      let prev = -1, s = '';
      for (let t = 0; t < ids.length; t++) {
        const i = ids[t];
        if (i !== prev && i !== blank) { s += vocab[i] || ''; acc.n++; acc.lp += best[t]; }
        prev = i;
      }
      return s;
    }
    async function transcribeDetailed(audio16k) {
      const tm0 = Date.now();
      let melMs = 0, encMs = 0, frames = 0; const acc = { n: 0, lp: 0 }; const parts = [];
      const cuts = cutPoints(audio16k);
      for (let c = 0; c + 1 < cuts.length; c++) {
        const seg = audio16k.subarray(cuts[c], cuts[c + 1]);
        if (seg.length < 1600) continue;
        const t0 = Date.now(); const fe = logMel(seg); const t1 = Date.now();
        const r = await runFeatures(fe); const t2 = Date.now();
        melMs += t1 - t0; encMs += t2 - t1; frames += fe.T;
        const s = decode(r.ids, r.best, acc); if (s.trim()) parts.push(s.trim());
      }
      const t3 = Date.now();
      let text = parts.join(' ').replace(/@/g, '').replace(/\s+/g, ' ').trim();
      const avg = acc.n ? acc.lp / acc.n : 0;
      let reason = '';
      if (!text) reason = 'empty';
      else if (text.replace(/\s/g, '').length <= 1 && avg < -0.7) { reason = 'low-confidence'; text = ''; }  // a stray letter from a noise
      return { text, reason, avgLogprob: avg, tokens: acc.n, melMs, encMs, decMs: Date.now() - t3, frames };
    }
    async function transcribe(audio16k) { return (await transcribeDetailed(audio16k)).text; }
    // checks the whole chain (features + model) against the conversion's own reference
    async function selfTest(tv) {
      const fe = logMel(f32(tv.audio_b64));
      const ref = f32(tv.features_b64), rt = tv.features_shape[1];
      let featDiff = Infinity;
      if (fe.T === rt) { featDiff = 0; for (let i = 0; i < ref.length; i++) { const dd = Math.abs(ref[i] - fe.data[i]); if (dd > featDiff) featDiff = dd; } }
      const r = await runFeatures(fe), exp = tv.expected_argmax;
      let same = 0; for (let i = 0; i < Math.min(r.ids.length, exp.length); i++) if (r.ids[i] === exp[i]) same++;
      return { featDiff, agree: exp.length ? same / exp.length : 0 };
    }
    function release() { try { sess.release && sess.release(); } catch (e) { /* ignore */ } }
    return { transcribe, transcribeDetailed, release, selfTest };
  }

  const api = { createRecognizer, cutPoints };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.GigaAMOffline = api;
})(typeof self !== 'undefined' ? self : this);
</script>
"""

# 1. the new block, right before the dictation engine
step('מנוע המודל העברי',
"""<script id="dictation-engine-core">""",
GIGA_CORE + """<script id="dictation-engine-core">""")

# 2. the dictation engine: start the Hebrew recognizer when asked to
step('הפעלת המנוע',
"""      this.rec = await W.createRecognizer(this.ort, { encoder: o.encoder, decoder: o.decoder, tokensText: o.tokensText, sessionOptions: so, encoderSessionOptions: o.encoderSessionOptions });
      this.gpu = !!o.gpu; this.warmMs = 0;""",
"""      this.selfTest = null;
      if (o.kind === 'ctc'){   // ג-2: the Hebrew model (GigaAM-He)
        const G = (typeof self !== 'undefined' ? self : root).GigaAMOffline;
        if (!G) throw new Error('missing GigaAM engine');
        this.rec = await G.createRecognizer(this.ort, { model: o.model, info: o.info, sessionOptions: so });
        if (o.tv){
          const t = await this.rec.selfTest(o.tv);
          this.selfTest = t;
          if (!(t.featDiff < 0.01) || t.agree < 0.9) throw new Error('model self-test failed (features ' + t.featDiff + ', agree ' + Math.round(t.agree * 100) + '%)');
        }
      } else
      this.rec = await W.createRecognizer(this.ort, { encoder: o.encoder, decoder: o.decoder, tokensText: o.tokensText, sessionOptions: so, encoderSessionOptions: o.encoderSessionOptions });
      this.gpu = !!o.gpu; this.warmMs = 0;""")

step('דיווח מוכן',
"""      this.emit({ type: 'ready', threads: (this.ort.env && this.ort.env.wasm && this.ort.env.wasm.numThreads) || 1, isolated: !!(typeof self !== 'undefined' && self.crossOriginIsolated), cores: (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) || 0, encoderDevice: this.gpu ? 'gpu' : 'cpu', warmMs: this.warmMs || 0 });""",
"""      this.emit({ type: 'ready', threads: (this.ort.env && this.ort.env.wasm && this.ort.env.wasm.numThreads) || 1, isolated: !!(typeof self !== 'undefined' && self.crossOriginIsolated), cores: (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) || 0, encoderDevice: this.gpu ? 'gpu' : 'cpu', warmMs: this.warmMs || 0, selfTest: this.selfTest || null });""")

# 3. the worker gets the new block too
step('קוד המנוע ברקע',
"""    const src = document.getElementById('whisper-offline-core').textContent + '\\n;\\n' +
                document.getElementById('dictation-engine-core').textContent + '\\n;\\n' + WORKER_GLUE;""",
"""    const src = document.getElementById('whisper-offline-core').textContent + '\\n;\\n' +
                document.getElementById('gigaam-offline-core').textContent + '\\n;\\n' +
                document.getElementById('dictation-engine-core').textContent + '\\n;\\n' + WORKER_GLUE;""")

# 4. loading: the Hebrew model has its own files and never uses the graphics-card path
step('טעינה: מעבד בלבד לעברית',
"""      if (gpuWanted() && !shortWanted()){   // ש-4ב: with the short window the CPU is already faster than the card""",
"""      const isCtc = MODELS[modelId] && MODELS[modelId].kind === 'ctc';   // ג-2
      let heInfo = null, heTv = null;
      if (isCtc){
        heInfo = JSON.parse(await st.files.info.text());
        const testedKey = 'heb-style-editor-offline-he-tested-v1';
        let tested = null; try { tested = localStorage.getItem(testedKey); } catch (e) { /* ignore */ }
        if (tested !== String(heInfo.sha256 || heInfo.size_bytes || '1')){   // the full check runs once per installed model
          try { const t = await dbGet('he/tv'); heTv = t ? JSON.parse(await t.text()) : null; } catch (e) { heTv = null; }
        }
      }
      if (!isCtc && gpuWanted() && !shortWanted()){   // ש-4ב: with the short window the CPU is already faster than the card""")

step('טעינה: הערת כרטיס מסך',
"""      } else if (window.OfflineVoiceMeasure) OfflineVoiceMeasure.gpuStatus(false, gpuWanted() ? 'לא בשימוש כש-✂️ חלון קצר דלוק' : '');""",
"""      } else if (window.OfflineVoiceMeasure) OfflineVoiceMeasure.gpuStatus(false, isCtc ? (gpuWanted() ? 'לא בשימוש עם עברית מדויק' : '') : gpuWanted() ? 'לא בשימוש כש-✂️ חלון קצר דלוק' : '');""")

step('טעינה: הודעת ההפעלה',
"""          const init = {
            type: 'init',
            encoder: new Uint8Array(await st.files.encoder.arrayBuffer()),
            decoder: new Uint8Array(await st.files.decoder.arrayBuffer()),
            tokensText: await st.files.tokens.text(),
            vad: getVadBytes(),""",
"""          const init = isCtc ? {
            type: 'init', kind: 'ctc',
            model: new Uint8Array(await st.files.model.arrayBuffer()),
            info: heInfo, tv: heTv,
            vad: getVadBytes(),
            ortBases: ORT_BASES,
            runtime: (rt && kind === 'worker') ? { js: rt.js, mjs: rt.mjs, wasm: await rt.wasm.arrayBuffer() } : null,
            language: LANGUAGE,
            sessionOptions: { executionProviders: ['wasm'], graphOptimizationLevel: 'all' }
          } : {
            type: 'init',
            encoder: new Uint8Array(await st.files.encoder.arrayBuffer()),
            decoder: new Uint8Array(await st.files.decoder.arrayBuffer()),
            tokensText: await st.files.tokens.text(),
            vad: getVadBytes(),""")

step('טעינה: העברת הקבצים לרקע',
"""          earLoadingText = 'טוען מודל…'; updateEar();
          pendingReady = deferred(); if (window.OfflineVoiceMeasure) OfflineVoiceMeasure.loadStart();
          transport = kind === 'worker' ? createWorkerTransport() : await createInlineTransport(rt);
          transport.post(init, kind === 'worker' ? [init.encoder.buffer, init.decoder.buffer, init.vad.buffer].concat(init.runtime ? [init.runtime.wasm] : []) : []);""",
"""          earLoadingText = heTv ? 'טוען ובודק את המודל (פעם אחת)…' : 'טוען מודל…'; updateEar();
          pendingReady = deferred(); if (window.OfflineVoiceMeasure) OfflineVoiceMeasure.loadStart();
          transport = kind === 'worker' ? createWorkerTransport() : await createInlineTransport(rt);
          transport.post(init, kind === 'worker' ? (isCtc ? [init.model.buffer] : [init.encoder.buffer, init.decoder.buffer]).concat([init.vad.buffer]).concat(init.runtime ? [init.runtime.wasm] : []) : []);""")

step('טעינה: סימון שהבדיקה עברה',
"""          loadedModel = modelId; loadedGpuWant = gpuWanted(); loadedShortWant = shortWanted(); lastErr = null;
          break;""",
"""          loadedModel = modelId; loadedGpuWant = gpuWanted(); loadedShortWant = shortWanted(); lastErr = null;
          if (isCtc && heTv){ try { localStorage.setItem('heb-style-editor-offline-he-tested-v1', String(heInfo.sha256 || heInfo.size_bytes || '1')); } catch (e) { /* ignore */ } }
          break;""")

# a failed self-test is a model problem: do not retry in the page thread
step('טעינה: שלב השגיאה',
"""    if (/protobuf|pars(e|ing)|load model|invalid model|unsupported model|tokens|encoder|decoder|missing/i.test(msg)) return 'model';""",
"""    if (/protobuf|pars(e|ing)|load model|invalid model|unsupported model|tokens|encoder|decoder|missing|self-test/i.test(msg)) return 'model';""")

# 5. after installing, the Hebrew model gets checked again on its next start
step('בדיקה מחדש אחרי התקנה',
"""    await dbPut('he/info', new Blob([JSON.stringify(info)], { type: 'application/json' }));
    report(1);""",
"""    await dbPut('he/info', new Blob([JSON.stringify(info)], { type: 'application/json' }));
    try { localStorage.removeItem('heb-style-editor-offline-he-tested-v1'); } catch (e) { /* ignore */ }
    report(1);""")

# 6. the ⏱️ panel: show the self-test result
step('מדידה: בדיקה עצמית',
"""               encoderDevice: (m && m.encoderDevice) || 'cpu', warmMs: (m && m.warmMs) || 0 };
      render();""",
"""               encoderDevice: (m && m.encoderDevice) || 'cpu', warmMs: (m && m.warmMs) || 0, selfTest: (m && m.selfTest) || null };
      render();""")
step('מדידה: שורת בדיקה',
"""      L.push('מקודד רץ על: ' + (head.encoderDevice === 'gpu' ? 'כרטיס מסך (הכנה ' + sec(head.warmMs) + ')' : 'מעבד') +""",
"""      if (head.selfTest) L.push('בדיקה עצמית של המודל: ✓ (' + Math.round(head.selfTest.agree * 100) + '% זהה)');
      L.push('מקודד רץ על: ' + (head.encoderDevice === 'gpu' ? 'כרטיס מסך (הכנה ' + sec(head.warmMs) + ')' : 'מעבד') +""")

MARK = '<script id="gigaam-offline-core">'
NEED = {'mark': "const GH_HE = 'https://github.com/netivdosIL/style-editor-models/releases/download/gigaam-he-v2/';",
        'msg': 'קודם צריך להחיל את העדכון "עברית מדויק ג-1", ורק אחריו את העדכון הזה.'}

# 7. ⏱️ rows: the Hebrew model has no separate decoder and no "short window"
step('מדידה: שם המודל בשורה',
"""      rows.push(Object.assign({}, i, { text: m && m.type === 'text' ? (m.text || '') : '', shownT: shownT || Date.now() }));""",
"""      rows.push(Object.assign({}, i, { text: m && m.type === 'text' ? (m.text || '') : '', shownT: shownT || Date.now(), model: head ? head.model : '' }));""")
step('מדידה: שורה לעברית',
"""    P.push('מקודד ' + sec((r.melMs || 0) + (r.encMs || 0)) + (r.device === 'gpu' ? ' (כרטיס מסך)' : '') + (r.frames && r.frames < 3000 ? ' (חלון קצר)' : ''));
    if (r.text){""",
"""    if (r.model === 'he'){   // ג-2
      P.push('מודל ' + sec((r.melMs || 0) + (r.encMs || 0)) + (r.text ? ' ל-' + words(r.text) + ' מילים' : ''));
      if (r.text) P.push('סה"כ ' + sec(totalMs(r))); else P.push('נדחה: ' + (REASONS[r.reason] || r.reason || 'לא ידוע'));
      return P.join(' · ');
    }
    P.push('מקודד ' + sec((r.melMs || 0) + (r.encMs || 0)) + (r.device === 'gpu' ? ' (כרטיס מסך)' : '') + (r.frames && r.frames < 3000 ? ' (חלון קצר)' : ''));
    if (r.text){""")
step('מדידה: ממוצע לעברית',
"""           ' · מקודד ' + sec(avg(r => (r.melMs || 0) + (r.encMs || 0))) + ' · מפענח ' + sec(avg(r => r.decMs || 0));""",
"""           (ok.every(r => r.model === 'he') ? ' · מודל ' + sec(avg(r => (r.melMs || 0) + (r.encMs || 0)))
             : ' · מקודד ' + sec(avg(r => (r.melMs || 0) + (r.encMs || 0))) + ' · מפענח ' + sec(avg(r => r.decMs || 0)));""")
step('מדידה: חלון קצר בכותרת',
"""        L.push('✂️ חלון קצר: ' + (sw ? 'דלוק' : 'כבוי')); }""",
"""        if (head.model !== 'he') L.push('✂️ חלון קצר: ' + (sw ? 'דלוק' : 'כבוי')); }""")
