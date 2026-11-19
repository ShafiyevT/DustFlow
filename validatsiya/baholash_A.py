import sys, json, numpy as np, pandas as pd
sys.path.insert(0,'.')
from dustflow.validatsiya import baho, qoniqarlimi
d=pd.read_csv("/home/claude/obs/portal_soatlik.csv"); d["t"]=pd.to_datetime(d["vaqt_utc"])
ST=["bukhara","navoi","qarshi"]; NOM={"bukhara":"Buxoro","navoi":"Navoiy","qarshi":"Qarshi"}
fon={s:d[(d.shahar==s)&(d.t>="2025-04-20 00:00")&(d.t<="2025-04-26 23:00")].pm10.median() for s in ST}
print("Stansiya foni (20–26.04 medianasi):", {NOM[s]:round(v,1) for s,v in fon.items()})
A,B=pd.Timestamp("2025-04-28 00:00"),pd.Timestamp("2025-04-30 23:00")
natija={}
for V in ["A1","A2"]:
    q=pd.DataFrame(json.load(open(f"natija_{V}.json"))["qator"]); q["t"]=pd.to_datetime(q["vaqt"])
    q=q[(q.t>=A)&(q.t<=B)].set_index("t")
    O,M,kun=[],[],[]
    for s in ST:
        ob=d[d.shahar==s].set_index("t").pm10.reindex(q.index)-fon[s]
        ok=ob.notna(); O+=list(ob[ok]); M+=list(q[f"{s}_pm10"][ok])
        dO=ob.resample("D").mean(); dM=q[f"{s}_pm10"].resample("D").mean(); kun.append((dO,dM))
    O,M=np.array(O),np.array(M)
    print(f"\n================ {V}: soatlik, 3 stansiya, {len(O)} juftlik ================")
    n=baho(O,M,jim=False); ok=qoniqarlimi(n)
    print("Chang–Hanna:", "OʻTDI" if ok else "OʻTMADI")
    per={}
    for s in ST:
        ob=d[d.shahar==s].set_index("t").pm10.reindex(q.index)-fon[s]; k=ob.notna()
        per[s]=baho(ob[k].values,q[f"{s}_pm10"][k].values)
        print(f"  {NOM[s]:7s}: FB={per[s]['FB']:+.2f} NMSE={per[s]['NMSE']:.2f} FAC2={per[s]['FAC2']:.2f} r={per[s]['r']:+.2f} NMB={per[s]['NMB']:+.0f}%  "
              f"(kuzatuv ort. {ob[k].mean():.0f}, model ort. {q[f'{s}_pm10'][k].mean():.0f})")
    kO=np.concatenate([x[0].values for x in kun]); kM=np.concatenate([x[1].values for x in kun])
    nk=baho(kO,kM)
    bq=q.bukhara_pm10.loc["2025-04-28":"2025-04-30"]; tp=bq.idxmax()
    b29=q.loc["2025-04-29"]; r25=b29.bukhara_pm25.sum()/b29.bukhara_pm10.sum()
    natija[V]=dict(soatlik=n,otdi=bool(ok),stansiya=per,kunlik=nk,choqqi=str(tp),choqqi_qiymat=float(bq.max()),
                   nisbat=float(r25),kunlik_juft=[[float(a),float(b)] for a,b in zip(kO,kM)])
    print(f"  kunlik (9 juftlik): FAC2={nk['FAC2']:.2f}  FB={nk['FB']:+.2f}  r={nk['r']:+.2f}")
    print(f"  Buxoro model choʻqqisi: {tp:%d.%m %H:%M} UTC, {bq.max():.0f} mkg/m³  (kuzatuv: 29.04 15:00 UTC)")
    print(f"  Buxoro model PM2.5/PM10 (29.04): {r25:.3f}  (kuzatuv 0.16)")
json.dump(natija,open("baho_A.json","w"),indent=1,default=float)
a1=natija["A1"]; h=abs((pd.Timestamp(a1["choqqi"])-pd.Timestamp("2025-04-29 15:00")).total_seconds())/3600
print("\n================ BASHORATLAR (A1) ================")
chiz=[("1. Choʻqqi ±3 soat ichida", h<=3, f"farq {h:.0f} soat"),
      ("2a. Soatlik: Chang–Hanna dan oʻtmaydi", not a1["otdi"], "oʻtmadi" if not a1["otdi"] else "OʻTDI"),
      ("2b. Soatlik FAC2 0,25–0,5", 0.25<=a1["soatlik"]["FAC2"]<=0.5, f"{a1['soatlik']['FAC2']:.2f}"),
      ("2c. Soatlik r 0,2–0,6", 0.2<=a1["soatlik"]["r"]<=0.6, f"{a1['soatlik']['r']:.2f}"),
      ("3. Kunlik FAC2 ≥ 0,5", a1["kunlik"]["FAC2"]>=0.5, f"{a1['kunlik']['FAC2']:.2f}"),
      ("4. Buxoro PM2.5/PM10 0,10–0,20", 0.10<=a1["nisbat"]<=0.20, f"{a1['nisbat']:.3f}"),
      ("5. NMB(A2) < NMB(A1)", natija["A2"]["soatlik"]["NMB"]<a1["soatlik"]["NMB"],
       f"A1 {a1['soatlik']['NMB']:+.0f}%, A2 {natija['A2']['soatlik']['NMB']:+.0f}%")]
for t_,ok,x in chiz: print(f"  {'BAJARILDI ' if ok else 'BAJARILMADI'}  {t_:40s} {x}")
