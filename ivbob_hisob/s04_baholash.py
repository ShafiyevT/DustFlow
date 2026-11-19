# -*- coding: utf-8 -*-
"""4-qadam. Stansiyalar va CAMS bilan taqqoslash, C_alpha ni aniqlash (§ 4.2).

* bir xil asos: 3 soatlik vaqtlar, 28.04 00:00 – 30.04 21:00 UTC, fondan ortiqcha PM10 (4.6);
* FB, NMSE, FAC2, R, NMB (4.7)–(4.8), Chang–Hanna mezonlari;
* CAMS bilan fazoviy taqqoslash (29.04 09:00 UTC, CAMS ning 0,75° li to'ri);
* C_alpha: modelning chiziqliligi (4.9) asosida M(k) = k M_mahalliy + M_chegara, k = C_alpha / C_ALPHA.
"""
import os, sys, json, pickle, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
from netCDF4 import Dataset, num2date
from dustflow.validatsiya import baho

N_ = U.NATIJA
d = pd.read_csv(U.STANSIYA_CSV); d["t"] = pd.to_datetime(d.vaqt_utc)
ds = Dataset(U.CAMS); clon = np.array(ds["longitude"][:]); clat = np.array(ds["latitude"][:])
T = pd.DatetimeIndex([dt.datetime(x.year, x.month, x.day, x.hour)
                      for x in num2date(ds["valid_time"][:], ds["valid_time"].units)])
P10 = np.array(ds["pm10"][:]) * 1e9; P25 = np.array(ds["pm2p5"][:]) * 1e9
Q = {V: pd.DataFrame(json.load(open(f"{N_}/boron_{V}.json"))["qator"]).assign(
        t=lambda x: pd.to_datetime(x.vaqt)).set_index("t") for V in ("chegara", "mahalliy")}
vaqt = pd.date_range("2025-04-28 00:00", "2025-04-30 21:00", freq="3h")
kun_w = [t for t in vaqt if pd.Timestamp("2025-04-28 19:00") <= t <= pd.Timestamp("2025-04-29 18:00")]


def chang_hanna(n):
    return abs(n["FB"]) < 0.3 and n["NMSE"] < 1.5 and n["FAC2"] > 0.5


O_all, M_all = [], {k: [] for k in ("chegara", "mahalliy", "CAMS")}
stans, kun = {}, {}
for s, (nm, la, lo) in U.STANSIYA.items():
    ob = d[d.shahar == s].set_index("t").pm10
    fo = ob.loc[U.FON[0]:U.FON[1]].median()
    i = int(np.argmin(abs(clon - lo))); j = int(np.argmin(abs(clat - la)))
    c = pd.Series(P10[:, j, i], index=T); fc = c.loc[U.FON[0]:U.FON[1]].median()
    o = (ob - fo).reindex(vaqt); ce = (c - fc).reindex(vaqt)
    ok = o.notna()
    O_all.append(o[ok].values)
    stans[s] = dict(nom=nm, fon=float(fo), fon_cams=float(fc))
    for k, m in (("chegara", Q["chegara"][f"{s}_pm10"].reindex(vaqt)),
                 ("mahalliy", Q["mahalliy"][f"{s}_pm10"].reindex(vaqt)), ("CAMS", ce)):
        M_all[k].append(m[ok].values)
        stans[s][k] = baho(o[ok].values, m[ok].values)
    kun[s] = dict(obs=float(o.reindex(kun_w).mean()),
                  **{k: float(Q[k][f"{s}_pm10"].reindex(kun_w).mean()) for k in ("chegara", "mahalliy")},
                  CAMS=float(ce.reindex(kun_w).mean()))
O = np.concatenate(O_all)
pool = {k: baho(O, np.concatenate(v)) for k, v in M_all.items()}
for k in pool:
    pool[k]["chang_hanna"] = chang_hanna(pool[k])

# PM2.5/PM10, Buxoro, bo'ron kuni
b = d[d.shahar == "bukhara"].set_index("t").loc["2025-04-28 19:00":"2025-04-29 18:00"]; rr = b.pm25 / b.pm10
ib = int(np.argmin(abs(clon - 64.4197))); jb = int(np.argmin(abs(clat - 39.7762)))
cs = pd.Series(P25[:, jb, ib] / P10[:, jb, ib], index=T).loc["2025-04-28 19:00":"2025-04-29 18:00"]
nisbat = dict(obs_min=float(rr.min()), obs_max=float(rr.max()), obs_med=float(rr.median()),
              **{k: float(Q[k].loc["2025-04-28 19:00":"2025-04-29 18:00"].bukhara_pm25.sum() /
                          Q[k].loc["2025-04-28 19:00":"2025-04-29 18:00"].bukhara_pm10.sum())
                 for k in ("chegara", "mahalliy")}, CAMS=float(cs.mean()))

# CAMS bilan fazoviy taqqoslash, 29.04 09:00 UTC
kt = list(T).index(U.CAMS_VAQT); ks = list(T).index(dt.datetime(2025, 4, 23, 9))
cams_ex = np.maximum(P10[kt] - P10[ks], 0)                             # (lat, lon)
fazo = {}
for V in ("chegara", "mahalliy"):
    sn = pickle.load(open(f"{N_}/boron_{V}_maydon.pkl", "rb")); lon, lat = sn["lon"], sn["lat"]
    pm = sn["cams_vaqt"]["pm10"]
    Mo, Ob = [], []
    for jj, la in enumerate(clat):
        for ii, lo in enumerate(clon):
            mi = (abs(lon - lo) <= 0.375); mj = (abs(lat - la) <= 0.375)
            if mi.sum() < 3 or mj.sum() < 3:
                continue
            Mo.append(float(pm[np.ix_(mi, mj)].mean())); Ob.append(float(cams_ex[jj, ii]))
    Mo, Ob = np.array(Mo), np.array(Ob)
    fazo[V] = dict(n=len(Mo), NMB=float((Mo.sum() - Ob.sum()) / Ob.sum() * 100),
                   FAC2=float(np.mean((Mo / np.maximum(Ob, 1e-9) >= 0.5) & (Mo / np.maximum(Ob, 1e-9) <= 2))),
                   M_ort=float(Mo.mean()), O_ort=float(Ob.mean()), Mo=Mo.tolist(), Ob=Ob.tolist())
mah_ulush = fazo["mahalliy"]["M_ort"] / fazo["chegara"]["M_ort"]

# C_alpha: M(k) = k M_mahalliy + (M_chegara - M_mahalliy)   (4.9)
Ms_loc = np.concatenate(M_all["mahalliy"]); Ms_chg = np.concatenate(M_all["chegara"]) - Ms_loc
Mc_loc = np.array(fazo["mahalliy"]["Mo"]); Mc_chg = np.array(fazo["chegara"]["Mo"]) - Mc_loc
Oc = np.array(fazo["chegara"]["Ob"])
FB = lambda o, m: 2 * (o.mean() - m.mean()) / (o.mean() + m.mean())
kal = []
for C in (2.5e-3, 5e-3, 7.5e-3, 1e-2, 1.5e-2, 2e-2):
    k = C / U.C_ALPHA; ms = k * Ms_loc + Ms_chg; mc = k * Mc_loc + Mc_chg
    kal.append(dict(C=C, Rs=float(ms.mean() / O.mean()), FBs=float(FB(O, ms)), Rc=float(mc.mean() / Oc.mean()),
                    FBc=float(FB(Oc, mc)), maxFB=float(max(abs(FB(O, ms)), abs(FB(Oc, mc)))),
                    FAC2s=baho(O, ms)["FAC2"]))
ks_ = np.linspace(0.1, 4, 3901)
mm = [max(abs(FB(O, k * Ms_loc + Ms_chg)), abs(FB(Oc, k * Mc_loc + Mc_chg))) for k in ks_]
opt = dict(C=float(ks_[int(np.argmin(mm))] * U.C_ALPHA), maxFB=float(min(mm)))

# mahalliy variant bo'yicha (butun chang mahalliy deb qaralganda — C_alpha ning yuqori bahosi)
Mc_m = np.array(fazo["mahalliy"]["Mo"]); Oc_m = np.array(fazo["mahalliy"]["Ob"])
kal_m = []
for C in (5e-3, 6e-3, 7e-3, 7.5e-3, 8e-3, 1e-2, 1.25e-2):
    k = C / U.C_ALPHA; ms = k * Ms_loc; mc = k * Mc_m; bs = baho(O, ms)
    kal_m.append(dict(C=C, Rs=float(ms.mean() / O.mean()), FBs=float(FB(O, ms)), Rc=float(mc.mean() / Oc_m.mean()),
                      FBc=float(FB(Oc_m, mc)), maxFB=float(max(abs(FB(O, ms)), abs(FB(Oc_m, mc)))),
                      FAC2s=bs["FAC2"], NMSEs=bs["NMSE"], NMBs=bs["NMB"],
                      FAC2c=float(np.mean((mc / np.maximum(Oc_m, 1e-9) >= .5) & (mc / np.maximum(Oc_m, 1e-9) <= 2)))))
mm_m = [max(abs(FB(O, k * Ms_loc)), abs(FB(Oc_m, k * Mc_m))) for k in ks_]
opt_m = dict(C=float(ks_[int(np.argmin(mm_m))] * U.C_ALPHA), maxFB=float(min(mm_m)))
nat = dict(n=int(len(O)), pool=pool, kalibrlash_mahalliy=kal_m, optimum_mahalliy=opt_m, stansiya=stans, kun=kun, nisbat=nisbat,
           fazo={k: {kk: v for kk, v in x.items() if kk not in ("Mo", "Ob")} for k, x in fazo.items()},
           mahalliy_ulush=float(mah_ulush), kalibrlash=kal, optimum=opt)
json.dump(nat, open(f"{N_}/baholash.json", "w"), indent=1, default=float)
print(f"{len(O)} juftlik")
for k, n in pool.items():
    print(f"  {k:9}: R {n['r']:.2f}  NMB {n['NMB']:+.0f} %  FAC2 {n['FAC2']:.2f}  FB {n['FB']:+.2f}  "
          f"NMSE {n['NMSE']:.2f}  Chang-Hanna {'ha' if n['chang_hanna'] else 'yo`q'}")
for s, r in stans.items():
    print(f"  {r['nom']:7}: R chegara {r['chegara']['r']:+.2f}, mahalliy {r['mahalliy']['r']:+.2f}, CAMS {r['CAMS']['r']:+.2f}"
          f" | bo'ron kuni: kuzatuv {kun[s]['obs']:.0f}, chegara {kun[s]['chegara']:.0f}, "
          f"mahalliy {kun[s]['mahalliy']:.0f}, CAMS {kun[s]['CAMS']:.0f}")
print("  PM2.5/PM10:", {k: round(v, 3) for k, v in nisbat.items()})
print("  fazoviy:", {k: (round(v['NMB']), round(v['FAC2'], 2)) for k, v in nat["fazo"].items()},
      f"mahalliy ulush {mah_ulush:.2f}")
for r in kal:
    print(f"  C {r['C']:.4f}: Rs {r['Rs']:.2f} FBs {r['FBs']:+.2f} | Rc {r['Rc']:.2f} FBc {r['FBc']:+.2f} | max {r['maxFB']:.2f}")
print("  optimum:", opt)
for r in kal_m:
    print(f"  [mahalliy] C {r['C']:.4f}: Rs {r['Rs']:.2f} FBs {r['FBs']:+.2f} FAC2s {r['FAC2s']:.2f} NMSEs {r['NMSEs']:.2f} | Rc {r['Rc']:.2f} FBc {r['FBc']:+.2f} FAC2c {r['FAC2c']:.2f} | max {r['maxFB']:.2f}")
print("  optimum (mahalliy):", opt_m)
