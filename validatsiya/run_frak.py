# CMES 1-maqola: 5 fraksiyali va bir modali hisob, haqiqiy ERA5-Land majburlashi (28–29.04.2025)
import sys, os, json, pickle, time, datetime as dt, numpy as np
sys.path.insert(0,'.')
from dustflow.grid import Tor
from dustflow.model import Model
V=sys.argv[1]; BOSH=dt.datetime(2025,4,28,0); SOAT=48; BYUDJET=235; NUQTA=f"nz_frak_{V}.pkl"
CH={"5":[0.2e-6,2.5e-6,10e-6,20e-6,50e-6,100e-6],"1":[0.2e-6,100e-6]}[V]
kesh=[pickle.load(open(f"kesh/{(BOSH+dt.timedelta(hours=h)):%Y%m%d%H}.pkl","rb")) for h in range(SOAT)]
ST={"bukhara":(39.7762,64.4197),"navoi":(40.0824,65.3751),"qarshi":(38.8239,65.7658)}
t0=time.time()
if os.path.exists(NUQTA): m,tar,snap,n0=pickle.load(open(NUQTA,"rb"))
else:
    t=Tor(Lx=380e3,Ly=390e3,Hz=5000.0,N=60,M=60,L=30,beta_s=8.0); k0=kesh[0][1]; t.eta=k0.eta; t.He=t.Hz-t.eta
    m=Model(t,k0,chegaralar=CH); tar=[]; snap={"ort":None,"n":0}; n0=0
t=m.tor; lon=61.5+t.x/(111320*np.cos(np.deg2rad(40.25))); lat=38.5+t.y/110574
ij={s:(int(np.argmin(abs(lon-lo))),int(np.argmin(abs(lat-la)))) for s,(la,lo) in ST.items()}
for n in range(n0,SOAT):
    if time.time()-t0>BYUDJET: pickle.dump((m,tar,snap,n),open(NUQTA,"wb")); print(f"BYUDJET {n}/{SOAT}"); sys.exit()
    v,k=kesh[n]; m.majburlash_yangila(k); m.ishga_tushir(T=3600,dt=120.0,jim=True)
    b=m.massa_balansi(); y=m.C[:,:,:,0]*1e9                       # (Nf,N,M) yer sirti, mkg/m3
    tot=y.sum(0); snap["ort"]=tot if snap["ort"] is None else snap["ort"]+tot; snap["n"]+=1
    if v==dt.datetime(2025,4,29,12): snap["choqqi"]=y.copy()
    tar.append(dict(t=str(v),Q=b["Q"],Q_em=b["Q_em"],Q_cho=b["Q_cho"],Q_chiq=b["Q_chiq"],Q_yut=b["Q_yut"],kes=b["kesilgan"],
                    y_ort=float(tot.mean()),y_max=float(tot.max()),**{f"{s}":float(tot[i,j]) for s,(i,j) in ij.items()}))
b=m.massa_balansi()
pickle.dump(dict(tar=tar,snap=snap,balans={k_:float(x) for k_,x in b.items()},vt=m.v_t.tolist(),d=m.d_ort.tolist(),
                 rho=m.rho_p.tolist(),ij=ij),open(f"frak_{V}.pkl","wb"))
if os.path.exists(NUQTA): os.remove(NUQTA)
print(f"{V} TUGADI: balans {b['nisbiy']:.4f} %, emissiya {b['Q_em']/1e6:.1f} kt, choʻkkan {b['Q_cho']/1e6:.1f}, chiqqan {b['Q_chiq']/1e6:.1f}, qolgan {b['Q']/1e6:.1f}")
