# -*- coding: utf-8 -*-
"""1-qadam. Statik maydonlarni tayyorlash va soatlik majburlash keshini yaratish.

* tuproq.tif: SoilGrids 2.0 gil ulushi; cho'l sinflari uchun adabiyot qiymati
  (aralash yondashuv, § 4.1): yalang'och — 5 %, butazor va o'tloq — 8 %;
* A_ef.tif: sug'oriladigan ekinzorlar (sinf 40) vegetatsiya mavsumida 0;
* kesh: 28.04–30.04.2025 (72 soat), sokin kun 23.04.2025 09:00, qishki hodisa 15.02.2026 09:00.
"""
import os, sys, pickle, shutil, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
import rasterio
import malumot_yuklash as ml
from dustflow.io_geo import stsenariy_yukla

ST = os.path.join(U.MALUMOT, "statik")


def statik():
    with rasterio.open(os.path.join(ST, "sinf.tif")) as s:
        sinf = s.read(1).round().astype(int)
    with rasterio.open(os.path.join(ST, "tuproq_soilgrids.tif")) as s:
        gil = s.read(1).astype(float); pr = s.profile
    for k, v in ml.CHOL_GIL.items():
        gil[sinf == k] = v
    with rasterio.open(os.path.join(ST, "tuproq.tif"), "w", **pr) as d:
        d.write(np.clip(gil, 0.01, 0.8).astype(pr["dtype"]), 1)
    with rasterio.open(os.path.join(ST, "A_ef_jadval.tif")) as s:
        a = s.read(1); pr = s.profile
    with rasterio.open(os.path.join(ST, "A_ef.tif"), "w", **pr) as d:
        d.write(np.where(sinf == 40, 0.0, a).astype(pr["dtype"]), 1)
    print("  statik maydonlar tayyor: tuproq.tif (aralash yondashuv), A_ef.tif (ekinzorlar 0)")
    for k in (60, 30, 20, 40):
        print(f"    sinf {k:>3}: ulushi {np.mean(sinf == k) * 100:5.1f} %, gil {np.median(gil[sinf == k]):.3f}")


def kesh(vaqtlar, era5):
    for v in vaqtlar:
        f = U.kesh_fayl(v)
        if os.path.exists(f):
            continue
        ml.stsenariy(v.strftime("%Y-%m-%d %H:%M"), "soatlik", era5)
        t = U.tor(); k, _ = stsenariy_yukla(os.path.join(U.MALUMOT, "stsenariylar", "soatlik"), t)
        pickle.dump((v, k), open(f, "wb"))


if __name__ == "__main__":
    U.vaqt_belgisi("statik maydonlar")
    statik()
    U.vaqt_belgisi("soatlik kesh (72 + 2 soat)")
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        kesh([U.BOSH + dt.timedelta(hours=h) for h in range(U.SOAT)] + [dt.datetime(2025, 4, 23, 9)], U.ERA5)
        kesh([dt.datetime(2026, 2, 15, 9)], U.ERA5_QISH)
    v, k = pickle.load(open(U.kesh_fayl(U.CHOQQI), "rb"))
    print(f"  {U.CHOQQI:%d.%m %H:%M}: U10 {k.U10.min():.1f}–{k.U10.max():.1f} m/s, "
          f"namlik {k.w.min():.1f}–{k.w.max():.1f} %, relyef {k.eta.min():.0f}–{k.eta.max():.0f} m")
    U.vaqt_belgisi("tayyor")
