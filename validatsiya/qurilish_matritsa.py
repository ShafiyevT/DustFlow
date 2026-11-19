import sys, json, numpy as np, pandas as pd
sys.path.insert(0,'.')
from dustflow.emission import emissiya_maydoni
P=json.load(open("qurilish_param.json")); q=pd.read_csv("qurilish_soatlik.csv",index_col=0,parse_dates=True)
CH=[0.2e-6,2.5e-6,10e-6,20e-6,50e-6,100e-6]; MAYDON=P["maydon"]
BORON=("2025-04-28 16:00","2025-04-29 23:00")
def E_qator(gil,w_rej,kU=1.0,A=0.8):
    out=[]
    for t,r in q.iterrows():
        w={"quruq":1.0,"era5":r.w,"namlangan":15.0}[w_rej]
        a=lambda x: np.array([[x]])
        F,inf=emissiya_maydoni(a(kU*r.U10),a(1e-3),a(w),a(gil),a(0.0),a(A),None,CH)
        out.append(inf["F_tot"][0,0]*MAYDON*3600/1000)
    return pd.Series(out,index=q.index)
jad={}
print(f"{'gil':>5} | {'quruq grunt':>22} | {'ERA5 namligi':>22} | {'namlangan (15 %)':>18}")
print(f"{'':>5} | {'boʻron, t':>10}{'maks t/s':>11}  | {'boʻron, t':>10}{'maks t/s':>11}  | {'boʻron, t':>10}")
for g in [0.05,0.10,0.15,0.20]:
    s={k:E_qator(g,k) for k in ["quruq","era5","namlangan"]}
    b={k:float(v.loc[BORON[0]:BORON[1]].sum()) for k,v in s.items()}
    jad[g]=dict(boron=b,maks={k:float(v.max()) for k,v in s.items()},soat={k:int((v.loc[BORON[0]:BORON[1]]>0).sum()) for k,v in s.items()})
    print(f"{g:5.2f} | {b['quruq']:10.1f}{s['quruq'].max():11.2f}  | {b['era5']:10.1f}{s['era5'].max():11.2f}  | {b['namlangan']:10.1f}")
# shahar ichida shamol pasayishi (×0,7), markaziy holat
s07=E_qator(0.15,"quruq",kU=0.7); print(f"\nmarkaziy holat (gil 0,15, quruq grunt) shamol ×0,7 bilan: boʻron {s07.loc[BORON[0]:BORON[1]].sum():.1f} t")
q["E_markaziy"]=E_qator(0.15,"quruq"); q.to_csv("qurilish_soatlik.csv")
m=q.E_markaziy; print(f"markaziy holat: eroziya soatlari {int((m.loc[BORON[0]:BORON[1]]>0).sum())} / 32, maks {m.max():.2f} t/soat ({m.idxmax():%d.%m %H:%M} UTC)")
json.dump(jad,open("qurilish_matritsa.json","w"),indent=1)
