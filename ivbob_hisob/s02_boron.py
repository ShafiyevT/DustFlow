# -*- coding: utf-8 -*-
"""2-qadam. 2025-yil 28–30-aprel chang bo'roni: 72 soatlik hisob.

Variantlar:
    mahalliy — faqat hudud ichidagi emissiya, yon chegaralarda theta_E = 0;
    chegara  — yon chegaralarda CAMS EAC4 dan olingan fon konsentratsiyasi (PM2.5 va PM10-PM2.5,
               1500 m gacha, sokin kun 23.04.2025 09:00 qiymati ayirilgan).
Ishga tushirish:  python ivbob_hisob/s02_boron.py mahalliy   (yoki chegara)
"""
import os, sys, json, pickle, time, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U


def cams_chegara(t, H=1500.0):
    from netCDF4 import Dataset, num2date
    from scipy.interpolate import RegularGridInterpolator
    ds = Dataset(U.CAMS)
    clon = np.array(ds["longitude"][:]); clat = np.array(ds["latitude"][:]); o = np.argsort(clat)
    T = [dt.datetime(x.year, x.month, x.day, x.hour)
         for x in num2date(ds["valid_time"][:], ds["valid_time"].units)]
    p10 = np.array(ds["pm10"][:]) * 1e9; p25 = np.array(ds["pm2p5"][:]) * 1e9
    ks = T.index(dt.datetime(2025, 4, 23, 9))
    lon, lat = U.lonlat(t)
    zagl = t.He[:, :, None] * t.s[None, None, :]
    tt = np.array([(x - T[0]).total_seconds() for x in T])

    def maydon(v):
        s = (v - T[0]).total_seconds(); i = np.searchsorted(tt, s) - 1; w = (s - tt[i]) / (tt[i + 1] - tt[i])
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
    kesh = U.kesh_oqi()
    m = U.model(kesh[0][1]); t = m.tor
    IJ = {s: U.ij(t, la, lo) for s, (_, la, lo) in U.STANSIYA.items()}
    cb = cams_chegara(t) if variant == "chegara" else None
    qator, snap, b48, qoshni = [], {}, None, []
    t0 = time.time()
    for n, (v, k) in enumerate(kesh):
        m.majburlash_yangila(k)
        m.Cb = [*cb(v), 0.0, 0.0, 0.0] if cb else 0.0
        F = m.emis_info["F_tot"]
        ts = time.time(); m.ishga_tushir(T=3600, dt=120.0, jim=True); sarf = time.time() - ts
        b = m.massa_balansi(); y = m.C[:, :, :, 0] * 1e9
        pm10 = y[0] + y[1]; pm25 = y[0]
        # stansiya atrofidagi 5x5 hujayra (vakillik tahlili uchun)
        qoshni.append({s_: dict(pm10=pm10[max(i-2,0):i+3, max(j-2,0):j+3].copy(),
                                pm25=pm25[max(i-2,0):i+3, max(j-2,0):j+3].copy()) for s_, (i, j) in IJ.items()})
        qator.append(dict(vaqt=v.strftime("%Y-%m-%d %H:%M"),
                          **{f"{s}_pm10": float(pm10[i, j]) for s, (i, j) in IJ.items()},
                          **{f"{s}_pm25": float(pm25[i, j]) for s, (i, j) in IJ.items()},
                          E_soat=float(np.sum(F * t.yuza_ogirligi()) * 3600 / 1000),
                          eroziya=float(np.mean(F[1:-1, 1:-1] > 0) * 100), U10_maks=float(k.U10.max()),
                          **{kk: float(b[kk]) for kk in ("Q", "Q_em", "Q_cho", "Q_chiq", "Q_yut", "kesilgan", "nisbiy")},
                          yuza_ort=float(y.sum(0).mean()), yuza_maks=float(y.sum(0).max()), s=sarf))
        if v == U.CHOQQI:
            snap["choqqi"] = dict(F=F.copy(), us=m.emis_info["u_star"].copy(), ut=m.emis_info["u_star_t"].copy(),
                                  yuza=y.sum(0).copy(), pm10=pm10.copy(), U=m.U[:, :, 3].copy(), V=m.V[:, :, 3].copy())
        if v == U.CAMS_VAQT:
            snap["cams_vaqt"] = dict(pm10=pm10.copy(), pm25=pm25.copy())
        if v + dt.timedelta(hours=1) == U.BORON_48[1]:
            b48 = {kk: float(b[kk]) for kk in b}
            b48["frak"] = [float(m.balans[i].Q_em) for i in range(m.Nf)]
        U.vaqt_belgisi(f"{variant} {v:%d.%m %H:%M}  E {qator[-1]['E_soat']:8.0f} t/soat  "
                       f"Buxoro PM10 {pm10[IJ['bukhara']]:7.1f}  balans {b['nisbiy']:.2f} %")
    b = m.massa_balansi()
    lon, lat = U.lonlat(t)
    json.dump(dict(variant=variant, qator=qator, balans={k_: float(x) for k_, x in b.items()}, b48=b48,
                   ij=IJ, vaqt=time.time() - t0, it_ort=float(np.mean(m.iteratsiyalar)),
                   it_maks=int(max(m.iteratsiyalar)), w_s=m.v_t.tolist()),
              open(os.path.join(U.NATIJA, f"boron_{variant}.json"), "w"), indent=1)
    snap.update(lon=lon, lat=lat, eta=t.eta.copy())
    pickle.dump(dict(vaqt=[q["vaqt"] for q in qator], ij=IJ, maydon=qoshni),
                open(os.path.join(U.NATIJA, f"boron_{variant}_qoshni.pkl"), "wb"))
    pickle.dump(snap, open(os.path.join(U.NATIJA, f"boron_{variant}_maydon.pkl"), "wb"))
    U.vaqt_belgisi(f"{variant} tugadi: balans {b['nisbiy']:.2f} %, {time.time() - t0:.0f} s")


if __name__ == "__main__":
    ishga(sys.argv[1] if len(sys.argv) > 1 else "mahalliy")
