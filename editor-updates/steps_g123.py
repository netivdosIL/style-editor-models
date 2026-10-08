import importlib.util, os
D=os.path.dirname(os.path.abspath(__file__))
def load(n):
    spec=importlib.util.spec_from_file_location(n,os.path.join(D,n+'.py')); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
g1,g2,g3=load('steps_g1'),load('steps_g2'),load('steps_g3')
# apply in order on the original: later steps may target text added by earlier ones, so fold them sequentially
STEPS=[]
_seq=g1.STEPS+g2.STEPS+g3.STEPS
MARK=g3.MARK
NEED=None
SEQUENTIAL=True
STEPS=_seq

g4=load("steps_g4")
GROUPS=[(g1.MARK,g1.STEPS),(g2.MARK,g2.STEPS),(g3.MARK,g3.STEPS),(g4.MARK,g4.STEPS)]
MARK=g4.MARK
