import sys, importlib.util
spec=importlib.util.spec_from_file_location('st',sys.argv[1]); st=importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
s=open(sys.argv[2],encoding='utf8').read()
crlf='\r\n' in s; s=s.replace('\r\n','\n')
ok=True
for name,f,r in st.STEPS:
    n=s.count(f)
    if n!=1: print('STEP FAIL',name,n); ok=False; continue
    s=s.replace(f,r)
if ok:
    open(sys.argv[3],'w',encoding='utf8',newline='').write(s.replace('\n','\r\n') if crlf else s)
    print('applied',len(st.STEPS),'steps; crlf',crlf)
else: sys.exit(1)
