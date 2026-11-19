import sys, os, json, pickle, time, numpy as np, pandas as pd
sys.path.insert(0,'.')
from dustflow.grid import Tor
from dustflow.data import KirishMaydonlari
from dustflow.model import Model
q=pd.read_csv("qurilish_soatlik.csv",index_col=0,parse_dates=True).loc["2025-04-28 16:00":"2025-04-29 23:00"]
L_=20000.0; N=64; GIL=0.15; W=1.0; MAYDON=226915.0; BYUDJET=240; NUQTA="nazorat_qur.pkl"
def tor():
    t=Tor(Lx=L_,Ly=L_,Hz=2000.0,N=N,M=N,L=24,beta_s=6.0); t.eta=np.zeros_like(t.eta); t.He=t.Hz-t.eta; return t
def maydonlar(t,U,yon):
    X,Y=np.meshgrid(t.x,t.y,indexing="ij"); sh=X.shape
    ic=int(np.argmin(abs(t.x-L_/2))); jc=int(np.argmin(abs(t.y-L_/2)))
    A=np.zeros(sh); z0=np.full(sh,0.3)
    cell=(t.x[1]-t.x[0])*(t.y[1]-t.y[0]); kat=[(ic,jc),(ic+1,jc),(ic,jc+1),(ic+1,jc+1)]
    for i,j in kat: A[i,j]=0.8*MAYDON/(len(kat)*cell); z0[i,j]=1e-3
    return KirishMaydonlari(U10=np.full(sh,U),yonalish=np.full(sh,yon),w=np.full(sh,W),m_cl=np.full(sh,GIL),
                            lam=np.zeros(sh),z0=z0,A_ef=A,eta=np.zeros(sh)), kat
t0=time.time()
if os.path.exists(NUQTA): m,n0,yig=pickle.load(open(NUQTA,"rb"))
else:
    t=tor(); r=q.iloc[0]; k,_=maydonlar(t,r.U10,np.degrees(np.arctan2(r.v10,r.u10)))
    m=Model(t,k); n0=0; yig=dict(maks=np.zeros((N+1,N+1)),ort=np.zeros((N+1,N+1)),soat=[],kat=None)
for n in range(n0,len(q)):
    if time.time()-t0>BYUDJET:
        pickle.dump((m,n,yig),open(NUQTA,"wb")); print(f"BYUDJET: {n}/{len(q)}"); sys.exit()
    r=q.iloc[n]; k,kat=maydonlar(m.tor,r.U10,np.degrees(np.arctan2(r.v10,r.u10))); yig["kat"]=kat
    m.majburlash_yangila(k); m.ishga_tushir(T=3600,dt=25.0,jim=True)
    pm10=(m.C[0]+m.C[1])[:,:,0]*1e9
    yig["maks"]=np.maximum(yig["maks"],pm10); yig["ort"]+=pm10/len(q)
    yig["soat"].append(dict(t=str(q.index[n]),E=float(m.F.sum()*(m.tor.x[1]-m.tor.x[0])*(m.tor.y[1]-m.tor.y[0])*3600/1000),pm10_maks=float(pm10.max())))
    print(f"  {q.index[n]:%d.%m %H:%M}  U {r.U10:4.1f}  E {yig['soat'][-1]['E']:5.2f} t/s  PM10 maks {pm10.max():8.1f}",flush=True)
b=m.massa_balansi(); t=m.tor
pickle.dump(dict(yig=yig,x=t.x,y=t.y,chok=m.chokindi.sum(axis=0),qal=m.chokindi_qalinligi(),balans={k_:float(v) for k_,v in b.items()}),open("qurilish_natija.pkl","wb"))
if os.path.exists(NUQTA): os.remove(NUQTA)
print(f"TUGADI: balans {b['nisbiy']:.4f} %, emissiya {b['Q_em']/1e3:.1f} t")
