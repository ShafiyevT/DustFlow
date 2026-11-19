import sys, json, numpy as np, pandas as pd, datetime as dt
sys.path.insert(0,'.')
from netCDF4 import Dataset, num2date
from dustflow.validatsiya import baho
ST={"bukhara":("Buxoro",39.7762,64.4197),"navoi":("Navoiy",40.0824,65.3751),"qarshi":("Qarshi",38.8239,65.7658)}
d=pd.read_csv("/home/claude/obs/portal_soatlik.csv"); d["t"]=pd.to_datetime(d.vaqt_utc)
ds=Dataset('/mnt/user-data/uploads/cams_eac4_2025-03-01_2025-05-31.nc'); clon=np.array(ds['longitude'][:]); clat=np.array(ds['latitude'][:])
T=pd.DatetimeIndex([dt.datetime(x.year,x.month,x.day,x.hour) for x in num2date(ds['valid_time'][:],ds['valid_time'].units)])
P10=np.array(ds['pm10'][:])*1e9; P25=np.array(ds['pm2p5'][:])*1e9
Q={V:pd.DataFrame(json.load(open(f"natija_{V}.json"))["qator"]).assign(t=lambda x:pd.to_datetime(x.vaqt)).set_index("t") for V in ["A1","A2"]}
vaqt=pd.date_range("2025-04-28 00:00","2025-04-30 21:00",freq="3h")
FON=("2025-04-20 00:00","2025-04-26 23:00")
rows={}; juft={k:([],[]) for k in ["A1","A2","CAMS"]}; kun={}
for s,(nm,la,lo) in ST.items():
    ob=d[d.shahar==s].set_index("t").pm10; ob25=d[d.shahar==s].set_index("t").pm25
    fo=ob.loc[FON[0]:FON[1]].median()
    i=int(np.argmin(abs(clon-lo))); j=int(np.argmin(abs(clat-la)))
    c=pd.Series(P10[:,j,i],index=T); c25=pd.Series(P25[:,j,i],index=T); fc=c.loc[FON[0]:FON[1]].median()
    o=(ob-fo).reindex(vaqt); ce=(c-fc).reindex(vaqt)
    rows[s]=dict(nom=nm,fon_obs=float(fo),fon_cams=float(fc))
    for k,m in [("A1",Q["A1"][f"{s}_pm10"].reindex(vaqt)),("A2",Q["A2"][f"{s}_pm10"].reindex(vaqt)),("CAMS",ce)]:
        ok=o.notna()&m.notna(); juft[k][0].extend(o[ok]); juft[k][1].extend(m[ok])
        rows[s][k]=baho(o[ok].values,m[ok].values)
    # boʻron kuni: 29.04 mahalliy = 28.04 19 UTC … 29.04 18 UTC
    w=[t for t in vaqt if pd.Timestamp("2025-04-28 19:00")<=t<=pd.Timestamp("2025-04-29 18:00")]
    kun[s]=dict(obs=float(o.reindex(w).mean()),A1=float(Q["A1"][f"{s}_pm10"].reindex(w).mean()),
               A2=float(Q["A2"][f"{s}_pm10"].reindex(w).mean()),CAMS=float(ce.reindex(w).mean()))
pool={k:baho(np.array(a),np.array(b)) for k,(a,b) in juft.items()}
print(f"Bir xil asos: 3 soatlik vaqtlar, 28.04 00 – 30.04 21 UTC, {len(juft['CAMS'][0])} juftlik (3 stansiya)\n")
print(f"{'':14}{'r':>7}{'NMB,%':>9}{'FAC2':>7}{'FB':>7}{'NMSE':>7}")
for k,nm in [("A1","DustFlow A1"),("A2","DustFlow A2"),("CAMS","CAMS")]:
    n=pool[k]; print(f"{nm:14}{n['r']:7.2f}{n['NMB']:9.0f}{n['FAC2']:7.2f}{n['FB']:7.2f}{n['NMSE']:7.2f}")
print("\nStansiyalar boʻyicha (r / NMB %):")
for s in ST:
    r=rows[s]; print(f"  {r['nom']:7}: fon kuzatuv {r['fon_obs']:.0f}, CAMS {r['fon_cams']:.0f} | "+
        "  ".join(f"{k} {r[k]['r']:+.2f}/{r[k]['NMB']:+.0f}" for k in ["A1","A2","CAMS"]))
print("\nBoʻron kuni (29.04 mahalliy) fondan ortiqcha PM10, oʻrtacha:")
for s in ST: print(f"  {ST[s][0]:7}: kuzatuv {kun[s]['obs']:6.0f} | A1 {kun[s]['A1']:6.0f} | A2 {kun[s]['A2']:6.0f} | CAMS {kun[s]['CAMS']:6.0f}")
# PM2.5/PM10 Buxoro, boʻron kuni
b=d[d.shahar=="bukhara"].set_index("t").loc["2025-04-28 19:00":"2025-04-29 18:00"]; rr=b.pm25/b.pm10
q1=Q["A1"].loc["2025-04-28 19:00":"2025-04-29 18:00"]; q2=Q["A2"].loc["2025-04-28 19:00":"2025-04-29 18:00"]
i=int(np.argmin(abs(clon-64.4197))); j=int(np.argmin(abs(clat-39.7762)))
cs=pd.Series(P25[:,j,i]/P10[:,j,i],index=T).loc["2025-04-28 19:00":"2025-04-29 18:00"]
rat=dict(obs_med=float(rr.median()),obs_min=float(rr.min()),obs_max=float(rr.max()),obs_q25=float(rr.quantile(.25)),obs_q75=float(rr.quantile(.75)),
         A1=float(q1.bukhara_pm25.sum()/q1.bukhara_pm10.sum()),A2=float(q2.bukhara_pm25.sum()/q2.bukhara_pm10.sum()),CAMS=float(cs.mean()))
print(f"\nPM2.5/PM10 Buxoro, boʻron kuni: kuzatuv {rat['obs_med']:.3f} ({rat['obs_min']:.3f}–{rat['obs_max']:.3f}), A1 {rat['A1']:.3f}, A2 {rat['A2']:.3f}, CAMS {rat['CAMS']:.3f}")
json.dump(dict(pool=pool,stansiya=rows,kun=kun,nisbat=rat),open("uch_tomon.json","w"),indent=1,default=float)
