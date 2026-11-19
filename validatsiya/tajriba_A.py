# -*- coding: utf-8 -*-
"""Oldindan qayd №2, tajriba A: vaqt boʻyicha oʻzgaruvchan majburlash, stansiyalar bilan."""
import sys, os, json, pickle, time, datetime as dt
import numpy as np, rasterio
sys.path.insert(0, '.')
from dustflow.grid import Tor
from dustflow.io_geo import stsenariy_yukla
from dustflow.model import Model
import malumot_yuklash as ml

BOSH = dt.datetime(2025, 4, 27, 0); SOAT = 96
BYUDJET = 230.0          # bitta ishga tushirishdagi vaqt, s
STANSIYA = {"bukhara": (39.77616584526309, 64.41972464564373),
            "navoi":   (40.082396, 65.375137),
            "qarshi":  (38.82394444, 65.76577778)}

def tor():
    t = Tor(Lx=380e3, Ly=390e3, Hz=5000.0, N=60, M=60, L=30, beta_s=8.0); return t

def tayyorla():
    # ekinzorlar A_ef = 0 (qayd №1 da muzlatilgan) — statik faylga bir marta
    ya = "haqiqiy_malumot/statik/A_ef.tif"
    if not os.path.exists(ya + ".asl"):
        os.rename(ya, ya + ".asl")
        with rasterio.open("haqiqiy_malumot/statik/sinf.tif") as s: sinf = s.read(1)
        with rasterio.open(ya + ".asl") as s: a = s.read(1); pr = s.profile
        with rasterio.open(ya, "w", **pr) as d: d.write(np.where(sinf == 40, 0.0, a).astype(pr["dtype"]), 1)
    os.makedirs("kesh", exist_ok=True); t_bosh = time.time()
    for h in range(SOAT):
        v = BOSH + dt.timedelta(hours=h); f = f"kesh/{v:%Y%m%d%H}.pkl"
        if os.path.exists(f): continue
        if time.time() - t_bosh > BYUDJET: print("BYUDJET TUGADI", flush=True); return
        ml.stsenariy(v.strftime("%Y-%m-%d %H:%M"), "soatlik")
        t = tor(); k, _ = stsenariy_yukla("haqiqiy_malumot/stsenariylar/soatlik", t)
        pickle.dump((v, k), open(f, "wb"))
        print(f"  majburlash {v:%d.%m %H:%M}  U10 maks {k.U10.max():.1f}", flush=True)
    print("TAYYOR", flush=True)

def kesh_oqi():
    return [pickle.load(open(f"kesh/{(BOSH + dt.timedelta(hours=h)):%Y%m%d%H}.pkl", "rb"))
            for h in range(SOAT)]

def cams_cb(t, H=1500.0):
    from netCDF4 import Dataset, num2date
    from scipy.interpolate import RegularGridInterpolator
    ds = Dataset('/mnt/user-data/uploads/cams_eac4_2025-03-01_2025-05-31.nc')
    clon = np.array(ds['longitude'][:]); clat = np.array(ds['latitude'][:]); o = np.argsort(clat)
    T = [dt.datetime(x.year, x.month, x.day, x.hour) for x in num2date(ds['valid_time'][:], ds['valid_time'].units)]
    p10 = np.array(ds['pm10'][:]) * 1e9; p25 = np.array(ds['pm2p5'][:]) * 1e9
    ks = T.index(dt.datetime(2025, 4, 23, 9))
    lon = 61.5 + t.x / (111320 * np.cos(np.deg2rad(40.25))); lat = 38.5 + t.y / 110574
    zagl = t.He[:, :, None] * t.s[None, None, :]
    def maydon(v):                                    # v: vaqt -> [Cb_frak0, Cb_frak1]
        tt = np.array([(x - T[0]).total_seconds() for x in T]); s = (v - T[0]).total_seconds()
        i = np.searchsorted(tt, s) - 1; w = (s - tt[i]) / (tt[i + 1] - tt[i])
        e10 = np.maximum((1 - w) * p10[i] + w * p10[i + 1] - p10[ks], 0)
        e25 = np.maximum((1 - w) * p25[i] + w * p25[i + 1] - p25[ks], 0)
        natija = []
        for f in (e25, np.maximum(e10 - e25, 0)):
            g = RegularGridInterpolator((clat[o], clon), f[o], bounds_error=False, fill_value=None)
            yuz = lambda lo, la, zz: np.where(zz <= H, g(np.c_[la, lo])[:, None], 0.0) * 1e-9
            natija.append(dict(x0=yuz(np.full(len(lat), lon[0]), lat, zagl[0]),
                               x1=yuz(np.full(len(lat), lon[-1]), lat, zagl[-1]),
                               y0=yuz(lon, np.full(len(lon), lat[0]), zagl[:, 0]),
                               y1=yuz(lon, np.full(len(lon), lat[-1]), zagl[:, -1])))
        return natija
    return maydon

def ishga(variant):
    kesh = kesh_oqi(); nuqta = f"nazorat_{variant}.pkl"; t_bosh = time.time()
    if os.path.exists(nuqta):
        m, ij, qator, maydonlar, boshlash = pickle.load(open(nuqta, "rb"))
        t = m.tor
    else:
        t = tor(); k0 = kesh[0][1]; t.eta = k0.eta; t.He = t.Hz - t.eta
        lon = 61.5 + t.x / (111320 * np.cos(np.deg2rad(40.25))); lat = 38.5 + t.y / 110574
        ij = {s: (int(np.argmin(abs(lon - lo))), int(np.argmin(abs(lat - la))))
              for s, (la, lo) in STANSIYA.items()}
        m = Model(t, k0); qator = []; maydonlar = {}; boshlash = 0
    cb = cams_cb(t) if variant == "A1" else None
    for n in range(boshlash, SOAT):
        if time.time() - t_bosh > BYUDJET:
            pickle.dump((m, ij, qator, maydonlar, n), open(nuqta, "wb"))
            print(f"BYUDJET TUGADI: {n}/{SOAT} soat", flush=True); return
        v, k = kesh[n]
        m.majburlash_yangila(k)
        m.Cb = ([*cb(v), 0.0, 0.0, 0.0] if cb else 0.0)
        m.ishga_tushir(T=3600, dt=120.0, jim=True)
        pm10 = (m.C[0] + m.C[1])[:, :, 0] * 1e9; pm25 = m.C[0][:, :, 0] * 1e9
        qator.append(dict(vaqt=v.strftime("%Y-%m-%d %H:%M"),
                          **{f"{s}_pm10": float(pm10[i, j]) for s, (i, j) in ij.items()},
                          **{f"{s}_pm25": float(pm25[i, j]) for s, (i, j) in ij.items()},
                          E_soat=float(m.F.sum() * t.dx * t.dy * 3600 / 1000)))
        if v.hour % 3 == 0: maydonlar[v.strftime("%Y%m%d%H")] = pm10.astype("float32")
        print(f"  {variant} {v:%d.%m %H:%M}  Buxoro {pm10[ij['bukhara']]:7.1f}", flush=True)
    b = m.massa_balansi()
    json.dump(dict(variant=variant, qator=qator, balans={k: float(x) for k, x in b.items()},
                   ij=ij), open(f"natija_{variant}.json", "w"), indent=1)
    np.savez_compressed(f"maydon_{variant}.npz", **maydonlar)
    if os.path.exists(nuqta): os.remove(nuqta)
    print(f"{variant} TUGADI: balans {b['nisbiy']:.4f} %, emissiya {b['Q_em']/1e6:.1f} ming t", flush=True)

if __name__ == "__main__":
    if sys.argv[1] == "tayyorla": tayyorla()
    else: ishga(sys.argv[1])
