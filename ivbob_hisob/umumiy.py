# -*- coding: utf-8 -*-
"""IV bob hisoblari uchun umumiy sozlamalar (DustFlow 2.0).

Barcha skriptlar DustFlow katalogidan ishga tushiriladi:
    python ivbob_hisob/hammasi.py
"""
import os, sys, pickle, datetime as dt
import numpy as np

ILDIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ILDIZ)
if ILDIZ not in sys.path:
    sys.path.insert(0, ILDIZ)

MALUMOT = os.path.join(ILDIZ, "haqiqiy_malumot")
KESH = os.path.join(ILDIZ, "ivbob_kesh")
NATIJA = os.path.join(ILDIZ, "ivbob_natija")
for p in (KESH, NATIJA):
    os.makedirs(p, exist_ok=True)

ERA5 = os.path.join(MALUMOT, "era5", "era5land_2025-04-20_2025-05-01.nc")
ERA5_QISH = os.path.join(MALUMOT, "era5", "era5land_2026-02-13_2026-02-17.nc")
CAMS = os.path.join(MALUMOT, "cams", "cams_eac4_2025-03-01_2025-05-31.nc")
STANSIYA_CSV = os.path.join(MALUMOT, "stansiyalar", "portal_soatlik.csv")

# Bo'ron hisobining davri: 28.04.2025 00:00 – 30.04.2025 23:00 UTC (72 soat)
BOSH = dt.datetime(2025, 4, 28, 0)
SOAT = 72
BORON_48 = (dt.datetime(2025, 4, 28, 0), dt.datetime(2025, 4, 30, 0))   # § 4.2 balansi
CHOQQI = dt.datetime(2025, 4, 29, 12)          # 4.5-, 4.6-rasm
CAMS_VAQT = dt.datetime(2025, 4, 29, 9)        # fazoviy taqqoslash
FON = ("2025-04-20 00:00", "2025-04-26 23:00")  # fon: sokin hafta medianasi

STANSIYA = {"bukhara": ("Buxoro", 39.7762, 64.4197),
            "navoi": ("Navoiy", 40.0824, 65.3751),
            "qarshi": ("Qarshi", 38.8239, 65.7658)}

LON0, LAT0 = 61.5, 38.5
COS = np.cos(np.deg2rad(40.25))
CH = [0.2e-6, 2.5e-6, 10e-6, 20e-6, 50e-6, 100e-6]

# Emissiya kalibrlash koeffitsiyenti (2.12). II–III boblardagi hisoblarda dastlabki qiymat 1e-2;
# § 4.2 dagi kalibrlash (s04_baholash.py, mahalliy variant) bo'yicha Buxoro hududi uchun 0.75e-2.
C_ALPHA = 0.75e-2


def tor():
    from dustflow.grid import Tor
    return Tor(Lx=380e3, Ly=390e3, Hz=5000.0, N=60, M=60, L=30, beta_s=8.0)


def lonlat(t):
    return LON0 + t.x / (111320 * COS), LAT0 + t.y / 110574


def ij(t, la, lo):
    lon, lat = lonlat(t)
    return int(np.argmin(abs(lon - lo))), int(np.argmin(abs(lat - la)))


def kesh_fayl(v):
    return os.path.join(KESH, f"{v:%Y%m%d%H}.pkl")


def kesh_oqi(bosh=BOSH, soat=SOAT):
    return [pickle.load(open(kesh_fayl(bosh + dt.timedelta(hours=h)), "rb")) for h in range(soat)]


def model(k0, **kw):
    """Asosiy sozlamalar: aniq rejim, f(Re) bilan cho'kish, kalibrlangan C_alpha."""
    from dustflow.model import Model
    t = tor(); t.eta = k0.eta; t.He = t.Hz - t.eta
    kw.setdefault("C_alpha", C_ALPHA)
    return Model(t, k0, sxema="aniq", qarshilik="re", **kw)


def vaqt_belgisi(matn):
    print(f"[{dt.datetime.now():%H:%M:%S}] {matn}", flush=True)
