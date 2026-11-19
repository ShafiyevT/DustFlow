# § 4.2 uchun haqiqiy maʼlumotlar bilan hisob (28–29.04.2025), DustFlow 2.0: sxema="aniq", qarshilik="re"
import sys, os, json, pickle, time, datetime as dt, numpy as np
sys.path.insert(0,'.')
from dustflow.model import Model
BOSH=dt.datetime(2025,4,28,0); SOAT=48; CHOQQI=dt.datetime(2025,4,29,12); BYUDJET=230
NUQTA="nazorat_42h.pkl"
def ll(t): return 61.5+t.x/(111320*np.cos(np.deg2rad(40.25))), 38.5+t.y/110574
def ij(t,la,lo):
    lon,lat=ll(t); return int(np.argmin(abs(lon-lo))), int(np.argmin(abs(lat-la)))
kesh=[pickle.load(open(f"kesh/{(BOSH+dt.timedelta(hours=h)):%Y%m%d%H}.pkl","rb")) for h in range(SOAT)]
t0=time.time()
if os.path.exists(NUQTA): m,tarix,snap,n0,sarf=pickle.load(open(NUQTA,"rb"))
else:
    from dustflow.grid import Tor
    t=Tor(Lx=380e3,Ly=390e3,Hz=5000.0,N=60,M=60,L=30,beta_s=8.0); k0=kesh[0][1]; t.eta=k0.eta; t.He=t.Hz-t.eta
    m=Model(t,k0); tarix=[]; snap={}; n0=0; sarf=0.0
for n in range(n0,SOAT):
    if time.time()-t0>BYUDJET:
        pickle.dump((m,tarix,snap,n,sarf+time.time()-t0),open(NUQTA,"wb")); print(f"BYUDJET: {n}/{SOAT}"); sys.exit()
    v,k=kesh[n]; m.majburlash_yangila(k); ts=time.time(); m.ishga_tushir(T=3600,dt=120.0,jim=True); sarf_soat=time.time()-ts
    b=m.massa_balansi(); y=m.yuza_konsentratsiya()*1e9; pm10=(m.C[0]+m.C[1])[:,:,0]*1e9
    tarix.append(dict(t=(v+dt.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),Q=b["Q"],Q_em=b["Q_em"],Q_cho=b["Q_cho"],
        Q_chiq=b["Q_chiq"],Q_yut=b["Q_yut"],kes=b["kesilgan"],qol=b["qoldiq"],y_ort=float(y.mean()),y_max=float(y.max()),
        pm10_ort=float(pm10.mean()),s=sarf_soat))
    if v==CHOQQI:
        t=m.tor; z=t.balandlik()
        cho=ij(t,40.80,63.50); voh=ij(t,39.7762,64.4197)
        snap=dict(F=m.emis_info["F_tot"].copy(),us=m.emis_info["u_star"].copy(),ut=m.emis_info["u_star_t"].copy(),
                  Q=m.emis_info["Q"].copy(),yuza=y.copy(),pm10=pm10.copy(),U=m.U[:,:,1].copy(),V=m.V[:,:,1].copy(),
                  prof_chol=(m.C[:,cho[0],cho[1],:].sum(0)*1e9, z[cho[0],cho[1],:]-t.eta[cho]),
                  prof_voha=(m.C[:,voh[0],voh[1],:].sum(0)*1e9, z[voh[0],voh[1],:]-t.eta[voh]),
                  frak=[float(m.balans[i].massa(m.C[i])) for i in range(m.Nf)], cho=cho, voh=voh,
                  eta=t.eta.copy(), x=t.x.copy(), y=t.y.copy())
    print(f"  {v:%d.%m %H:%M}  massa {b['Q']/1e6:8.2f} kt  yuza ort {y.mean():7.1f}  maks {y.max():8.1f}",flush=True)
b=m.massa_balansi(); jami=sarf+time.time()-t0
json.dump(dict(tarix=tarix,balans={k:float(x) for k,x in b.items()},vaqt=jami),open("res42h.json","w"),indent=1)
pickle.dump(snap,open("snap42h.pkl","wb"))
if os.path.exists(NUQTA): os.remove(NUQTA)
print(f"TUGADI: balans {b['nisbiy']:.4f} %, hisoblash {jami:.0f} s")
