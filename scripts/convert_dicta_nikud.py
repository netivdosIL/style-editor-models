#!/usr/bin/env python3
"""Converts Dicta's Hebrew nikud model (dicta-il/dictabert-large-char-menaked, CC BY 4.0) to ONNX for the
style editor, checks the conversion, and builds an evaluation set from vocalized Sefaria texts.

Outputs (in --out):
  hebrew-dicta-nikud.zip (+ .partNN and .parts.json when --split-mb is set)
      model.onnx (int8), tokenizer.json, vocab.txt, model_info.json, test_vectors.json, NOTICE.txt
  dicta-nikud-src.zip      the model's own Python code and config (to port the decoding exactly)
  nikud_eval.json          gold vocalized sentences + this model's predictions (int8 and fp32)
  convert_log.txt          everything printed
"""
import argparse, hashlib, io, json, os, re, shutil, subprocess, sys, time, zipfile, glob, random

LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)

NIQQUD = re.compile('[ְ-ׇּׁׂ]')
CANT = re.compile('[֑-ֽֿ֯׀׃-׆]')

def strip_all(s): return re.sub('[֑-ׇ]', '', s)

def clean_gold(s):
    s = re.sub(r'<[^>]+>', ' ', s)            # html tags in Sefaria texts
    s = re.sub(r'&[a-z]+;', ' ', s)
    s = re.sub(r'\{[^}]*\}|\[[^\]]*\]|\([^)]*\)', ' ', s)   # editorial notes / ktiv-qre brackets
    s = CANT.sub('', s).replace('־', ' ')   # cantillation, meteg, paseq, sof pasuq out; maqaf -> space
    s = s.replace('ׇ', 'ָ')            # qamatz qatan -> qamatz
    s = re.sub(r'[^ְ-ׇא-ת \.,;:?!\-"\']', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def sefaria_sentences(limit_per_book):
    """Vocalized gold text from Sefaria-Export (sparse clone, only the files we need)."""
    out = {}
    try:
        if not os.path.isdir('sefaria'):
            subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout',
                            'https://github.com/Sefaria/Sefaria-Export', 'sefaria'], check=True)
        names = subprocess.run(['git', '-C', 'sefaria', 'ls-tree', '-r', '--name-only', 'HEAD'],
                               check=True, capture_output=True, text=True).stdout.splitlines()
        log('files in export:', len(names), 'sample:', [n for n in names if '/Ruth/' in n][:10], [n for n in names if 'Berakhot' in n and 'Mishnah' in n][:10])
        want = {
            'tanakh_ruth':   r'/Ruth/Hebrew/[^/]*\.json$',
            'tanakh_genesis': r'/Torah/Genesis/Hebrew/[^/]*\.json$',
            'mishnah_berakhot': r'/Mishnah Berakhot/Hebrew/[^/]*\.json$',
            'mishnah_avot': r'/Pirkei Avot/Hebrew/[^/]*\.json$',
        }
        for key, rx in want.items():
            cands = [n for n in names if re.search(rx, n)]
            log(key, 'candidates:', cands[:12])
            best = None
            for n in cands:
                subprocess.run(['git', '-C', 'sefaria', 'checkout', 'HEAD', '--', n], check=True, capture_output=True)
                try: data = json.load(open(os.path.join('sefaria', n), encoding='utf-8'))
                except Exception as e: log('  cannot read', n, e); continue
                txt = data.get('text')
                flat = []
                def walk(x):
                    if isinstance(x, str): flat.append(x)
                    elif isinstance(x, list):
                        for y in x: walk(y)
                walk(txt)
                joined = ' '.join(flat)
                letters = len(re.findall('[א-ת]', joined)) or 1
                ratio = len(NIQQUD.findall(joined)) / letters
                log('  ', n, 'segments', len(flat), 'niqqud/letter %.2f' % ratio)
                if ratio > 0.6 and (best is None or ratio > best[0]): best = (ratio, n, flat)
            if best:
                sents = []
                for seg in best[2]:
                    seg = clean_gold(seg)
                    for part in re.split(r'(?<=[\.:;?!])\s+', seg):
                        part = part.strip(' -')
                        if 4 <= len(part.split()) <= 30 and len(NIQQUD.findall(part)) > len(part) * 0.25: sents.append(part)
                random.Random(7).shuffle(sents)
                out[key] = {'source': best[1], 'sentences': sents[:limit_per_book]}
                log(key, 'using', best[1], len(out[key]['sentences']), 'sentences')
    except Exception as e:
        log('sefaria eval set failed:', repr(e))
    return out

MODERN = [   # undiacritized modern sentences (no gold) — to see the output on everyday text
    'הילדים שיחקו בגינה עם החברים שלהם אחרי הצהריים',
    'אנחנו לומדים גמרא כל יום אחרי תפילת שחרית',
    'השיעור של הרב היה מאוד מעניין והתלמידים שאלו הרבה שאלות',
    'קניתי ספר חדש בחנות הספרים שליד הבית',
    'בבוקר השכם קמנו והלכנו לבית הכנסת',
    'אמר רבי יוחנן מאי טעמא דכתיב ויהי ערב ויהי בקר יום אחד',
    'וכתב רש״י שהפשט הוא העיקר בכל מקום',
    'שלום לכולם היום נלמד תורה',
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out')
    ap.add_argument('--repo', default='dicta-il/dictabert-large-char-menaked')
    ap.add_argument('--split-mb', type=int, default=50)
    ap.add_argument('--eval-per-book', type=int, default=150)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    try:
        run(a)
    except Exception as e:
        import traceback; log('FAILED:', repr(e)); log(traceback.format_exc())
    finally:
        log('total %.0fs' % (time.time() - t0))
        open(os.path.join(a.out, 'convert_log.txt'), 'w', encoding='utf-8').write('\n'.join(LOG))

def run(a):
    import numpy as np, torch
    from huggingface_hub import snapshot_download
    from transformers import AutoModel, AutoTokenizer
    path = snapshot_download(a.repo)
    log('downloaded', a.repo, '->', path, sorted(os.listdir(path)))
    # the model's own code and config, for porting the decoding to JavaScript
    with zipfile.ZipFile(os.path.join(a.out, 'dicta-nikud-src.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for f in os.listdir(path):
            if not f.endswith('.safetensors'): z.write(os.path.join(path, f), f)
    from transformers import BertTokenizerFast
    tok = BertTokenizerFast.from_pretrained(path)   # the fast tokenizer splits into letters (tokenizer.json)
    model = AutoModel.from_pretrained(path, trust_remote_code=True).eval()
    mod = sys.modules[type(model).__module__]
    NIKUD = getattr(mod, 'NIKUD_CLASSES', None); SHIN = getattr(mod, 'SHIN_CLASSES', None)
    log('model class', type(model).__name__, 'module', mod.__name__)
    log('NIKUD_CLASSES', NIKUD); log('SHIN_CLASSES', SHIN)
    log('tokenizer', type(tok).__name__, 'max_len', tok.model_max_length, 'vocab', len(tok))
    enc = tok(['שלום עולם'], return_tensors='pt')
    log('tokens', enc['input_ids'].tolist(), tok.convert_ids_to_tokens(enc['input_ids'][0]), 'offsets', tok(['שלום עולם'], return_offsets_mapping=True)['offset_mapping'])
    with torch.no_grad():
        o = model(**enc, return_dict=True)
    log('output type', type(o).__name__, 'fields', [k for k in dir(o) if not k.startswith('_')][:30])
    lg = o.logits
    log('logits type', type(lg).__name__, [k for k in dir(lg) if not k.startswith('_')][:30])
    def pick(lg):
        if isinstance(lg, (tuple, list)): return lg[0], lg[1]
        for x, y in (('nikud_logits', 'shin_logits'), ('nikud', 'shin')):
            if hasattr(lg, x): return getattr(lg, x), getattr(lg, y)
        raise RuntimeError('unknown logits structure')
    nl, sl = pick(lg)
    log('nikud logits', tuple(nl.shape), 'shin logits', tuple(sl.shape))
    ref_pred = model.predict(['שָׁלוֹם עוֹלָם', MODERN[0]], tok, mark_matres_lectionis='')
    log('torch predict sample:', ref_pred)

    class W(torch.nn.Module):
        def __init__(s, m): super().__init__(); s.m = m
        def forward(s, input_ids, attention_mask):
            out = s.m(input_ids=input_ids, attention_mask=attention_mask, return_dict=True)
            return pick(out.logits)
    w = W(model).eval()
    fp32 = os.path.join(a.out, 'model_fp32.onnx')
    ex = tok(MODERN[:2], padding=True, return_tensors='pt')
    torch.onnx.export(w, (ex['input_ids'], ex['attention_mask']), fp32, opset_version=17, dynamo=False,
                      input_names=['input_ids', 'attention_mask'], output_names=['nikud_logits', 'shin_logits'],
                      dynamic_axes={'input_ids': {0: 'b', 1: 't'}, 'attention_mask': {0: 'b', 1: 't'},
                                    'nikud_logits': {0: 'b', 1: 't'}, 'shin_logits': {0: 'b', 1: 't'}})
    log('exported fp32', os.path.getsize(fp32) // 2**20, 'MB')
    from onnxruntime.quantization import quantize_dynamic, QuantType
    int8 = os.path.join(a.out, 'model.onnx')
    quantize_dynamic(fp32, int8, weight_type=QuantType.QInt8, op_types_to_quantize=['MatMul', 'Gemm'])
    log('quantized int8', os.path.getsize(int8) // 2**20, 'MB')
    import onnxruntime as ort
    s32 = ort.InferenceSession(fp32, providers=['CPUExecutionProvider'])
    s8 = ort.InferenceSession(int8, providers=['CPUExecutionProvider'])

    # predict() with the forward pass replaced by an ONNX session — the decoding stays the model's own
    real_forward = model.forward
    def onnx_predict(sess, sents):
        def fwd(input_ids=None, attention_mask=None, **kw):
            n, s_ = sess.run(None, {'input_ids': input_ids.numpy().astype(np.int64), 'attention_mask': attention_mask.numpy().astype(np.int64)})
            n, s_ = torch.from_numpy(n), torch.from_numpy(s_)
            if isinstance(lg, (tuple, list)): new = type(lg)((n, s_)) if not isinstance(lg, tuple) else (n, s_)
            else:
                new = type(lg).__new__(type(lg)); new.__dict__.update(lg.__dict__)
                for x, y in (('nikud_logits', 'shin_logits'), ('nikud', 'shin')):
                    if hasattr(lg, x): setattr(new, x, n); setattr(new, y, s_); break
            res = type(o).__new__(type(o)); res.__dict__.update(o.__dict__); res.logits = new
            return res
        model.forward = fwd
        try: return model.predict(sents, tok, mark_matres_lectionis='')
        finally: model.forward = real_forward
    def mpredict(sents): return model.predict(sents, tok, mark_matres_lectionis='')

    gold = sefaria_sentences(a.eval_per_book)
    allsents = MODERN + [s for g in gold.values() for s in g['sentences']]
    plain = [strip_all(s) for s in allsents]
    B = 16
    pt, p32, p8 = [], [], []
    t = time.time()
    for i in range(0, len(plain), B): pt += mpredict(plain[i:i + B])
    log('torch predict %.1fs for %d sentences' % (time.time() - t, len(plain)))
    for i in range(0, len(plain), B): p32 += onnx_predict(s32, plain[i:i + B])
    t = time.time()
    for i in range(0, len(plain), B): p8 += onnx_predict(s8, plain[i:i + B])
    log('onnx int8 predict %.1fs' % (time.time() - t))
    same32 = sum(x == y for x, y in zip(pt, p32)); same8 = sum(x == y for x, y in zip(pt, p8))
    log('identical to torch: fp32 %d/%d, int8 %d/%d' % (same32, len(pt), same8, len(pt)))

    def words_acc(pred, ref):
        tot = ok = 0
        for p_, r_ in zip(pred, ref):
            pw, rw = p_.split(), clean_gold(r_).split()
            if len(pw) != len(rw): continue
            for x, y in zip(pw, rw):
                if not re.search('[א-ת]', y): continue
                tot += 1; ok += norm(x) == norm(y)
        return ok, tot
    def norm(w):
        w = w.replace('ֺ', 'ֹ').replace('ׇ', 'ָ')
        w = re.sub('[^ְ-ׇׂא-ת]', '', w)
        # marks on each letter, order-insensitive
        out, cur = [], ''
        for ch in w:
            if 'א' <= ch <= 'ת':
                if cur: out.append(cur[0] + ''.join(sorted(cur[1:])))
                cur = ch
            else: cur += ch
        if cur: out.append(cur[0] + ''.join(sorted(cur[1:])))
        return ''.join(out)
    k = len(MODERN)
    for key, g in gold.items():
        n = len(g['sentences'])
        okt, tot = words_acc(pt[k:k + n], g['sentences']); ok8, _ = words_acc(p8[k:k + n], g['sentences'])
        log('accuracy %-18s torch %.1f%%  int8 %.1f%%  (%d words)' % (key, 100 * okt / max(1, tot), 100 * ok8 / max(1, tot), tot))
        g['pred_int8'] = p8[k:k + n]; g['pred_fp32'] = pt[k:k + n]
        k += n
    for s, p_ in zip(MODERN, p8[:len(MODERN)]): log('modern:', p_)
    json.dump({'modern': {'sentences': MODERN, 'pred_int8': p8[:len(MODERN)]}, 'gold': gold},
              open(os.path.join(a.out, 'nikud_eval.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    # test vectors for the browser: ids, a few logits, expected text
    tv = []
    for s in plain[:6]:
        e = tok([s], return_tensors='np')
        n, s_ = s8.run(None, {'input_ids': e['input_ids'].astype(np.int64), 'attention_mask': e['attention_mask'].astype(np.int64)})
        tv.append({'text': s, 'ids': e['input_ids'][0].tolist(), 'nikud_argmax': n[0].argmax(-1).tolist(), 'shin_argmax': s_[0].argmax(-1).tolist(),
                   'expected': onnx_predict(s8, [s])[0]})
    info = {'format': 'heb-style-editor-dicta-nikud', 'version': 1, 'source': a.repo, 'license': 'CC BY 4.0',
            'nikud_classes': NIKUD, 'shin_classes': SHIN, 'max_len': int(min(tok.model_max_length, 2048)),
            'cls_id': tok.cls_token_id, 'sep_id': tok.sep_token_id, 'pad_id': tok.pad_token_id, 'unk_id': tok.unk_token_id,
            'size_bytes': os.path.getsize(int8), 'sha256': hashlib.sha256(open(int8, 'rb').read()).hexdigest()}
    json.dump(info, open(os.path.join(a.out, 'model_info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(tv, open(os.path.join(a.out, 'test_vectors.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(a.out, 'NOTICE.txt'), 'w', encoding='utf-8').write(
        'Hebrew nikud model: DictaBERT-large-char-menaked by DICTA (dicta.org.il), https://huggingface.co/dicta-il/dictabert-large-char-menaked\n'
        'License: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/\n'
        'Changes: converted to ONNX and quantized to int8 for use in the browser.\n')
    zp = os.path.join(a.out, 'hebrew-dicta-nikud.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_STORED) as z:
        z.write(int8, 'model.onnx')
        for f in ('tokenizer.json', 'vocab.txt'):
            if os.path.exists(os.path.join(path, f)): z.write(os.path.join(path, f), f)
        for f in ('model_info.json', 'test_vectors.json', 'NOTICE.txt'): z.write(os.path.join(a.out, f), f)
    os.remove(fp32)
    log('zip', os.path.getsize(zp) // 2**20, 'MB')
    if a.split_mb:
        data = open(zp, 'rb').read(); size = a.split_mb * 2**20; parts = []
        for i in range(0, len(data), size):
            pn = '%s.part%02d' % (os.path.basename(zp), i // size + 1)
            open(os.path.join(a.out, pn), 'wb').write(data[i:i + size])
            parts.append({'name': pn, 'size': len(data[i:i + size]), 'sha256': hashlib.sha256(data[i:i + size]).hexdigest()})
        json.dump({'file': os.path.basename(zp), 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'parts': parts},
                  open(zp + '.parts.json', 'w'), indent=1)
        log('parts', len(parts))
    os.remove(int8)

if __name__ == '__main__':
    main()
