# -*- coding: utf-8 -*-
"""5-qadam. Buxoro shahridagi qurilish maydoni (§ 4.3).

a) ERA5-Land dan maydon nuqtasidagi soatlik qator va emissiya matritsasi
   (gil ulushi 5–20 %, sirt holati: quruq / ERA5-Land namligi / namlangan);
b) markaziy holat (gil 15 %, quruq grunt) uchun 20x20 km sohada tarqalish.
Ishga tushirish:  python ivbob_hisob/s05_qurilish.py [emissiya|tarqalish]
"""
import os, sys, json, pickle, time, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
from dustflow.emission import emissiya_maydoni

LAT, LON = 39.7682149, 64.4251505
MAYDON = 226915.0
A_EF, Z0 = 0.80, 1e-3
BORON = ("2025-04-28 16:00", "2025-04-29 23:00")
QATOR = os.path.join(U.NATIJA, "qurilish_soatlik.csv")


def _E(U10, w, gil, kU=1.0):
    a = lambda x: np.array([[x]])
    F, inf = emissiya_maydoni(a(kU * U10), a(Z0), a(w), a(gil), a(0.0), a(A_EF), None, U.CH, C_alpha=U.C_ALPHA)
    return float(inf["F_tot"][0, 0]) * MAYDON * 3600 / 1000          # t/soat


def emissiya():
    import rasterio
    from netCDF4 import Dataset, num2date
    from scipy.interpolate import RegularGridInterpolator
    def piksel(f):
        with rasterio.open(os.path.join(U.MALUMOT, "statik", f)) as s:
            r, c = s.index(LON, LAT); return float(s.read(1)[r, c])
    bd = piksel("bdod.tif"); sinf = int(piksel("sinf.tif"))
    ds = Dataset(U.ERA5); v = ds.variables
    lat = np.array(v["latitude"][:]); lon = np.array(v["longitude"][:]); o = np.argsort(lat)
    T = [dt.datetime(x.year, x.month, x.day, x.hour) for x in num2date(v["valid_time"][:], v["valid_time"].units)]
    def nuqta(nom):
        a = np.array(v[nom][:])[:, o, :]
        return np.array([RegularGridInterpolator((lat[o], lon), a[k])([LAT, LON])[0] for k in range(len(T))])
    q = pd.DataFrame(dict(u10=nuqta("u10"), v10=nuqta("v10"), swvl1=nuqta("swvl1")),
                     index=pd.DatetimeIndex(T)).sort_index().loc["2025-04-20":"2025-04-30 23:00"]
    q["U10"] = np.hypot(q.u10, q.v10); q["w"] = q.swvl1 * 1000 / (bd * 1000) * 100
    q["qayerdan"] = np.degrees(np.arctan2(-q.u10, -q.v10)) % 360
    b = q.loc[BORON[0]:BORON[1]]
    jad = {}
    for g in (0.05, 0.10, 0.15, 0.20):
        s = {"quruq": b.U10.apply(lambda u: _E(u, 1.0, g)),
             "era5": pd.Series([_E(r.U10, r.w, g) for _, r in b.iterrows()], index=b.index),
             "namlangan": b.U10.apply(lambda u: _E(u, 15.0, g))}
        jad[str(g)] = dict(boron={k: float(x.sum()) for k, x in s.items()},
                           maks={k: float(x.max()) for k, x in s.items()},
                           soat={k: int((x > 0).sum()) for k, x in s.items()})
    q["E_markaziy"] = q.U10.apply(lambda u: _E(u, 1.0, 0.15))
    q["E_markaziy_07"] = q.U10.apply(lambda u: _E(u, 1.0, 0.15, 0.7))
    q.to_csv(QATOR)
    m = q.loc[BORON[0]:BORON[1]]
    d29 = q.loc["2025-04-29 00:00":"2025-04-29 23:00"]
    natija = dict(sinf=sinf, bdod=bd, U10_maks=float(b.U10.max()), U10_maks_vaqt=str(b.U10.idxmax()),
                  w_min=float(b.w.min()), w_max=float(b.w.max()), jadval=jad,
                  markaziy=dict(boron=float(m.E_markaziy.sum()), maks=float(m.E_markaziy.max()),
                                maks_vaqt=str(m.E_markaziy.idxmax()), soat=int((m.E_markaziy > 0).sum()),
                                boron_07=float(m.E_markaziy_07.sum())),
                  yonalish_29=float(d29.qayerdan.median()), U10_29=float(d29.U10.mean()))
    json.dump(natija, open(os.path.join(U.NATIJA, "qurilish_emissiya.json"), "w"), indent=1)
    print(json.dumps({k: natija[k] for k in ("U10_maks", "U10_maks_vaqt", "w_min", "w_max", "markaziy",
                                             "yonalish_29", "U10_29")}, indent=1))
    for g, r in jad.items():
        print(f"  gil {g}: quruq {r['boron']['quruq']:7.1f} t, ERA5 {r['boron']['era5']:6.1f} t, "
              f"namlangan {r['boron']['namlangan']:5.1f} t")


def tarqalish(dt_=60.0):
    from dustflow.grid import Tor
    from dustflow.data import KirishMaydonlari
    from dustflow.model import Model
    q = pd.read_csv(QATOR, index_col=0, parse_dates=True).loc[BORON[0]:BORON[1]]
    L_, N = 20000.0, 64
    t = Tor(Lx=L_, Ly=L_, Hz=2000.0, N=N, M=N, L=24, beta_s=6.0)
    ic = int(np.argmin(abs(t.x - L_ / 2))); jc = int(np.argmin(abs(t.y - L_ / 2)))
    kat = [(ic, jc), (ic + 1, jc), (ic, jc + 1), (ic + 1, jc + 1)]
    cell = t.dx * t.dy

    def kirish(r):
        sh = (N + 1, N + 1); A = np.zeros(sh); z0 = np.full(sh, 0.3)
        for i, j in kat:
            A[i, j] = A_EF * MAYDON / (len(kat) * cell); z0[i, j] = Z0       # (4.11)
        return KirishMaydonlari(U10=np.full(sh, r.U10), yonalish=np.full(sh, np.degrees(np.arctan2(r.v10, r.u10))),
                                w=np.full(sh, 1.0), m_cl=np.full(sh, 0.15), lam=np.zeros(sh), z0=z0, A_ef=A,
                                eta=np.zeros(sh), z0_shamol=np.full(sh, 0.3))   # shahar foni
    # lokal soha (dx = 312 m) uchun gorizontal diffuziya koeffitsiyenti II bobdagi kabi kichik olinadi
    m = Model(t, kirish(q.iloc[0]), sxema="aniq", qarshilik="re", C_alpha=U.C_ALPHA, K_h=50.0)
    yig = dict(maks=np.zeros((N + 1, N + 1)), ort=np.zeros((N + 1, N + 1)), soat=[])
    t0 = time.time()
    for n in range(len(q)):
        r = q.iloc[n]; m.majburlash_yangila(kirish(r)); m.ishga_tushir(T=3600, dt=dt_, jim=True)
        pm10 = (m.C[0] + m.C[1])[:, :, 0] * 1e9
        yig["maks"] = np.maximum(yig["maks"], pm10); yig["ort"] += pm10 / len(q)
        yig["soat"].append(dict(t=str(q.index[n]), U10=float(r.U10), pm10_maks=float(pm10.max())))
        U.vaqt_belgisi(f"qurilish {q.index[n]:%d.%m %H:%M}  U {r.U10:4.1f}  PM10 maks {pm10.max():8.1f}")
    b = m.massa_balansi()
    X, Y = np.meshgrid(t.x - L_ / 2, t.y - L_ / 2, indexing="ij"); R = np.hypot(X, Y) / 1000
    S = t.yuza_ogirligi() / 1e6
    qal = m.chokindi_qalinligi() * 1e3                                      # mm -> mkm
    zona = lambda F, c: (float(np.sum(S[F > c])), float(R[F > c].max()) if np.any(F > c) else 0.0)
    st = U.STANSIYA["bukhara"]
    sx = (st[2] - LON) * 111320 * np.cos(np.deg2rad(LAT)) + L_ / 2; sy = (st[1] - LAT) * 110574 + L_ / 2
    si, sj = int(np.argmin(abs(t.x - sx))), int(np.argmin(abs(t.y - sy)))
    nat = dict(balans={k: float(v) for k, v in b.items()}, ort_maks=float(yig["ort"].max()),
               zona_ort75=zona(yig["ort"], 75), zona_soat75=zona(yig["maks"], 75), zona_soat25=zona(yig["maks"], 25),
               qal_maks=float(qal.max()), zona_qal01=zona(qal, 0.1), stansiya_ort=float(yig["ort"][si, sj]),
               stansiya_masofa=float(np.hypot(sx - L_ / 2, sy - L_ / 2)), dt=dt_, vaqt=time.time() - t0)
    json.dump(nat, open(os.path.join(U.NATIJA, "qurilish_tarqalish.json"), "w"), indent=1)
    pickle.dump(dict(yig=yig, x=t.x, y=t.y, qal=qal, stansiya=(si, sj)),
                open(os.path.join(U.NATIJA, "qurilish_tarqalish.pkl"), "wb"))
    print(json.dumps(nat, indent=1))


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "hammasi"
    if q in ("emissiya", "hammasi"):
        emissiya()
    if q in ("tarqalish", "hammasi"):
        tarqalish()
