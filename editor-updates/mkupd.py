import sys, json, importlib.util
spec=importlib.util.spec_from_file_location('st',sys.argv[1]); st=importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
title, sub, out, fnname = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
groups=getattr(st,'GROUPS',None)
if groups: steps=[{'skipIf':gm,'steps':[{'name':n,'find':f,'repl':r} for n,f,r in gs]} for gm,gs in groups]
else: steps=[{'skipIf':None,'steps':[{'name':n,'find':f,'repl':r} for n,f,r in st.STEPS]}]
need=getattr(st,'NEED',None)
html='''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TITLE</title>
<style>
  body{ margin:0; background:#f4f1ea; color:#2a2620; font-family:'Segoe UI', Arial, sans-serif; font-size:16px; line-height:1.6; }
  .box{ max-width:560px; margin:40px auto; background:#fff; border:1px solid #d8d1c2; border-radius:10px; padding:26px 28px; }
  h1{ font-size:22px; margin:0 0 6px; }
  .sub{ color:#6b6357; margin:0 0 18px; font-size:14.5px; }
  ol{ padding-inline-start:20px; margin:0 0 18px; }
  li{ margin-bottom:6px; }
  button{ font:inherit; font-weight:700; font-size:17px; padding:12px 18px; width:100%; border:0; border-radius:8px; background:#8a5a3b; color:#fff; cursor:pointer; }
  button:hover{ background:#744a30; }
  #msg{ margin-top:16px; min-height:24px; font-weight:600; }
  #msg.ok{ color:#2f6b4f; } #msg.err{ color:#a4453a; }
  @media (prefers-color-scheme:dark){ body{ background:#1d1b18; color:#ece6da; } .box{ background:#2a2723; border-color:#47413a; } .sub{ color:#b3aa9b; } #msg.ok{ color:#7ccfa0; } #msg.err{ color:#f0907f; } }
</style>
</head>
<body>
<div class="box">
  <h1>TITLE</h1>
  <p class="sub">SUB</p>
  <ol>
    <li>לוחצים על הכפתור ובוחרים את הקובץ <b>עורך סגנונות.html</b> הנוכחי שלכם.</li>
    <li>הקובץ המעודכן יורד לתיקיית ההורדות, באותו שם.</li>
    <li>מחליפים בו את הקובץ הישן (אם הדפדפן הוסיף לשם "(1)" – מוחקים את התוספת).</li>
  </ol>
  <button type="button" id="pick">בחירת הקובץ ועדכון</button>
  <input type="file" id="file" accept=".html,.htm" hidden>
  <div id="msg" role="status"></div>
</div>
<script>
(function(){
  var MARK = MARKJSON;
  var NEED = NEEDJSON;
  var STEPS = STEPSJSON;
  function count(s, sub){ var n = 0, i = 0; while((i = s.indexOf(sub, i)) !== -1){ n++; i += sub.length; } return n; }
  function say(t, cls){ var m = document.getElementById('msg'); m.textContent = t; m.className = cls || ''; }
  function apply(text){
    var crlf = text.indexOf('\\r\\n') !== -1;
    var s = crlf ? text.replace(/\\r\\n/g, '\\n') : text;
    if(s.indexOf(MARK) !== -1) return { already:true };
    if(s.indexOf('id="offline-modal"') === -1 || s.indexOf('id="whisper-offline-core"') === -1)
      return { error:'זה לא נראה כמו קובץ העורך. בחרו את "עורך סגנונות.html".' };
    if(NEED && s.indexOf(NEED.mark) === -1) return { error: NEED.msg };
    for(var g = 0; g < STEPS.length; g++){
      var grp = STEPS[g];
      if(grp.skipIf && [].concat(grp.skipIf).some(m => s.indexOf(m) !== -1)) continue;   // this part is already in the file
      for(var k = 0; k < grp.steps.length; k++){
        var st = grp.steps[k], n = count(s, st.find);
        if(n !== 1) return { error:'לא נמצא המקום לעדכון: ' + st.name + ' (' + n + '). כנראה זו גרסה אחרת של העורך – שלחו אותה ל-Claude.' };
        s = s.replace(st.find, function(){ return st.repl; });
      }
    }
    return { text: crlf ? s.replace(/\\n/g, '\\r\\n') : s };
  }
  window.FNNAME = apply; // for automated tests
  document.getElementById('pick').onclick = function(){ document.getElementById('file').click(); };
  document.getElementById('file').onchange = function(e){
    var f = e.target.files && e.target.files[0];
    if(!f) return;
    say('קורא את הקובץ...');
    var r = new FileReader();
    r.onerror = function(){ say('לא הצלחתי לקרוא את הקובץ.', 'err'); };
    r.onload = function(){
      var res = apply(String(r.result));
      e.target.value = '';
      if(res.already){ say('הקובץ הזה כבר מעודכן. אין צורך לעשות כלום.', 'ok'); return; }
      if(res.error){ say(res.error, 'err'); return; }
      var blob = new Blob([res.text], { type:'text/html;charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'עורך סגנונות.html';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function(){ URL.revokeObjectURL(a.href); }, 60000);
      say('העדכון הצליח. הקובץ "עורך סגנונות.html" ירד לתיקיית ההורדות – מחליפים בו את הקובץ הישן.', 'ok');
    };
    r.readAsText(f, 'utf-8');
  };
})();
</script>
</body>
</html>
'''
j=lambda o: json.dumps(o, ensure_ascii=False).replace('</','<\\/')
html=html.replace('TITLE',title).replace('SUB',sub).replace('MARKJSON',j(st.MARK)).replace('NEEDJSON',j(need)).replace('STEPSJSON',j(steps)).replace('FNNAME',fnname)
open(out,'w',encoding='utf8').write(html); print('written',out,len(html))
