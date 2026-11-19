# -*- coding: utf-8 -*-
"""Buxoro viloyati uchun 10 ta stsenariy ma'lumot to'plamini yaratish.

Har bir stsenariy uchun alohida katalogda quyidagi fayllar yaratiladi:
    meteo.nc      — NetCDF : u10, v10, t2m, swvl1     (0.25°,  ERA5 kabi)
    relyef.tif    — GeoTIFF: balandlik                (0.01°,  SRTM kabi)
    qoplam.tif    — GeoTIFF: o'simlik qoplami         (0.05°,  MODIS kabi)
    tuproq.tif    — GeoTIFF: gil ulushi               (0.05°,  SoilGrids)
    z0.tif        — GeoTIFF: g'adir-budurlik uzunligi (0.05°,  Land Cover)
    A_ef.tif      — GeoTIFF: eroziyaga beriluvchan yuza ulushi
    manbalar.json — maydonlar tavsifi va manbalari
"""
import os
import json
import numpy as np

LON0, LON1 = 61.5, 66.0
LAT0, LAT1 = 38.5, 42.0

STSENARIYLAR = [
    dict(id="01_yoz_kuchli_boron", nom="Yozgi kuchli chang boʻroni",
         sana="2025-07-18", mavsum="yoz", U=17.0, yon=42.0,
         quruqlik=1.00, t2m=311.0,
         tavsif="Shimoli-gʻarbdan kuchli shamol, tuproq maksimal quruq"),
    dict(id="02_yoz_ortacha", nom="Yozgi oʻrtacha shamol",
         sana="2025-07-05", mavsum="yoz", U=12.0, yon=40.0,
         quruqlik=0.95, t2m=308.0,
         tavsif="Odatiy yozgi sharoit, mezomasshtabli eroziya"),
    dict(id="03_bahor_boron", nom="Bahorgi chang boʻroni",
         sana="2025-04-12", mavsum="bahor", U=15.0, yon=25.0,
         quruqlik=0.55, t2m=291.0,
         tavsif="Bahorgi shamol, tuproq qisman nam"),
    dict(id="04_kuz_quruq", nom="Kuzgi quruq davr",
         sana="2025-10-08", mavsum="kuz", U=13.5, yon=55.0,
         quruqlik=0.85, t2m=297.0,
         tavsif="Vegetatsiya tugagan, oʻsimlik qoplami siyrak"),
    dict(id="05_qish_nam", nom="Qishki nam sharoit",
         sana="2026-01-22", mavsum="qish", U=16.0, yon=70.0,
         quruqlik=0.30, t2m=276.0,
         tavsif="Kuchli shamol, ammo tuproq nam — emissiya cheklangan"),
    dict(id="06_afgon_shamoli", nom="«Afgʻon» shamoli",
         sana="2025-06-14", mavsum="yoz", U=20.0, yon=200.0,
         quruqlik=1.00, t2m=313.0,
         tavsif="Janubi-gʻarbdan juda kuchli quruq shamol"),
    dict(id="07_sokin_kun", nom="Sokin kun",
         sana="2025-05-20", mavsum="bahor", U=5.5, yon=30.0,
         quruqlik=0.70, t2m=298.0,
         tavsif="Nazorat varianti: shamol chegaraviy qiymatdan past"),
    dict(id="08_sugorish_mavsumi", nom="Sugʻorish mavsumi",
         sana="2025-06-28", mavsum="yoz", U=13.0, yon=35.0,
         quruqlik=0.90, voha_nam=1.6, t2m=306.0,
         tavsif="Vohada namlik yuqori, choʻlda oʻzgarishsiz"),
    dict(id="09_qurgoqchilik", nom="Qurgʻoqchilik yili",
         sana="2025-08-11", mavsum="yoz", U=12.0, yon=45.0,
         quruqlik=1.00, voha_nam=0.45, qoplam_k=0.45, t2m=312.0,
         tavsif="Vohada ham namlik va oʻsimlik qoplami keskin kamaygan"),
    dict(id="10_ekstremal", nom="Ekstremal chang boʻroni",
         sana="2025-07-29", mavsum="yoz", U=22.0, yon=38.0,
         quruqlik=1.00, t2m=315.0,
         tavsif="Rekord shamol tezligi, maksimal emissiya"),
]


def _tor(dlon, dlat=None):
    dlat = dlat or dlon
    lon = np.arange(LON0 + dlon / 2, LON1, dlon)
    lat = np.arange(LAT0 + dlat / 2, LAT1, dlat)
    return lon, lat


def _voha(lon, lat):
    """Zarafshon vohasi ko'rsatkichi: janubi-sharqda 1 ga yaqin."""
    LO, LA = np.meshgrid(lon, lat, indexing="ij")
    xn = (LO - LON0) / (LON1 - LON0)
    yn = (LA - LAT0) / (LAT1 - LAT0)
    return 1.0 / (1.0 + np.exp(-12.0 * ((xn + 0.75 * (1 - yn)) - 1.05)))


def _relyef(lon, lat):
    LO, LA = np.meshgrid(lon, lat, indexing="ij")
    xn = (LO - LON0) / (LON1 - LON0)
    yn = (LA - LAT0) / (LAT1 - LAT0)
    e = (250 * np.exp(-(((xn - 0.30) / 0.22) ** 2 + ((yn - 0.70) / 0.28) ** 2))
         + 175 * np.exp(-(((xn - 0.62) / 0.18) ** 2 + ((yn - 0.45) / 0.20) ** 2))
         + 100 * np.exp(-(((xn - 0.85) / 0.15) ** 2 + ((yn - 0.80) / 0.22) ** 2)))
    rng = np.random.default_rng(7)
    e += 6.0 * rng.standard_normal(e.shape)
    return np.maximum(e, 0.0)


def nc_yoz(yol, lon, lat, maydonlar, sana):
    from netCDF4 import Dataset
    with Dataset(yol, "w", format="NETCDF4_CLASSIC") as ds:
        ds.createDimension("lon", len(lon))
        ds.createDimension("lat", len(lat))
        v = ds.createVariable("lon", "f8", ("lon",)); v[:] = lon
        v.units = "degrees_east"; v.long_name = "longitude"
        v = ds.createVariable("lat", "f8", ("lat",)); v[:] = lat
        v.units = "degrees_north"; v.long_name = "latitude"
        for nom, (a, birlik, tavsif) in maydonlar.items():
            v = ds.createVariable(nom, "f4", ("lat", "lon"), zlib=True)
            v[:] = a.T
            v.units = birlik; v.long_name = tavsif
        ds.title = "DustFlow stsenariy meteorologik maydonlari"
        ds.source = "ERA5 / ERA5-Land koʻrinishidagi namunaviy maʼlumot"
        ds.date = sana
        ds.Conventions = "CF-1.8"


def tif_yoz(yol, lon, lat, arr, birlik="", tavsif=""):
    import rasterio
    from rasterio.transform import from_origin
    dlon = float(lon[1] - lon[0]); dlat = float(lat[1] - lat[0])
    a = arr.T[::-1, :]
    tr = from_origin(lon[0] - dlon / 2, lat[-1] + dlat / 2, dlon, dlat)
    with rasterio.open(yol, "w", driver="GTiff",
                       height=a.shape[0], width=a.shape[1], count=1,
                       dtype="float32", crs="EPSG:4326", transform=tr,
                       compress="deflate", nodata=-9999.0) as dst:
        dst.write(a.astype("float32"), 1)
        dst.update_tags(units=birlik, description=tavsif)


def stsenariy_yarat(st, asosiy="stsenariylar"):
    kat = os.path.join(asosiy, st["id"])
    os.makedirs(kat, exist_ok=True)

    lon_m, lat_m = _tor(0.25)
    voha_m = _voha(lon_m, lat_m)
    U = st["U"] * (1.0 - 0.25 * voha_m)
    rng = np.random.default_rng(abs(hash(st["id"])) % 2 ** 31)
    U = U * (1.0 + 0.06 * rng.standard_normal(U.shape))
    ang = np.deg2rad(st["yon"])
    u10 = U * np.cos(ang); v10 = U * np.sin(ang)

    q = st["quruqlik"]
    w_chol = 0.5 + 4.5 * (1.0 - q)
    w_voha = st.get("voha_nam", 1.0) * (10.0 + 8.0 * (1.0 - q))
    namlik = w_chol + (w_voha - w_chol) * voha_m
    t2m = np.full_like(U, st["t2m"])

    nc_yoz(os.path.join(kat, "meteo.nc"), lon_m, lat_m, {
        "u10": (u10, "m s-1", "shamolning zonal tashkil etuvchisi, 10 m"),
        "v10": (v10, "m s-1", "shamolning meridional tashkil etuvchisi, 10 m"),
        "t2m": (t2m, "K", "havo harorati, 2 m"),
        "swvl1": (namlik, "percent", "tuproqning yuqori qatlamidagi namligi"),
    }, st["sana"])

    lon_r, lat_r = _tor(0.01)
    tif_yoz(os.path.join(kat, "relyef.tif"), lon_r, lat_r,
            _relyef(lon_r, lat_r), "m", "yer sirti balandligi")

    lon_q, lat_q = _tor(0.05)
    voha_q = _voha(lon_q, lat_q)
    kq = st.get("qoplam_k", 1.0)
    lam_chol = 0.004 + 0.006 * (1.0 - q)
    lam_voha = kq * (0.09 if st["mavsum"] in ("bahor", "yoz") else 0.05)
    tif_yoz(os.path.join(kat, "qoplam.tif"), lon_q, lat_q,
            lam_chol + (lam_voha - lam_chol) * voha_q,
            "-", "oʻsimlik qoplamining zichligi")
    tif_yoz(os.path.join(kat, "tuproq.tif"), lon_q, lat_q,
            0.04 + 0.12 * voha_q, "-", "gil zarrachalarining massa ulushi")
    tif_yoz(os.path.join(kat, "z0.tif"), lon_q, lat_q,
            1.0e-4 + (2.0e-2 - 1.0e-4) * voha_q, "m", "gʻadir-budurlik uzunligi")
    tif_yoz(os.path.join(kat, "A_ef.tif"), lon_q, lat_q,
            0.25 * (1.0 - voha_q) + 0.02, "-", "eroziyaga beriluvchan yuza ulushi")

    tavsif = {
        "id": st["id"], "nom": st["nom"], "tavsif": st["tavsif"],
        "sana": st["sana"], "mavsum": st["mavsum"],
        "soha": {"lon": [LON0, LON1], "lat": [LAT0, LAT1]},
        "maydonlar": {
            "u10":    {"fayl": "meteo.nc", "format": "netcdf", "ozgaruvchi": "u10",
                       "manba": "ERA5, 0.25°", "usul": "interp"},
            "v10":    {"fayl": "meteo.nc", "format": "netcdf", "ozgaruvchi": "v10",
                       "manba": "ERA5, 0.25°", "usul": "interp"},
            "namlik": {"fayl": "meteo.nc", "format": "netcdf", "ozgaruvchi": "swvl1",
                       "manba": "ERA5-Land / SMAP, 0.25°", "usul": "interp"},
            "relyef": {"fayl": "relyef.tif", "format": "geotiff",
                       "manba": "SRTM, 0.01°", "usul": "ortala"},
            "qoplam": {"fayl": "qoplam.tif", "format": "geotiff",
                       "manba": "MODIS LAI, 0.05°", "usul": "avto"},
            "gil":    {"fayl": "tuproq.tif", "format": "geotiff",
                       "manba": "SoilGrids, 0.05°", "usul": "avto"},
            "z0":     {"fayl": "z0.tif", "format": "geotiff",
                       "manba": "MODIS Land Cover, 0.05°", "usul": "avto"},
            "A_ef":   {"fayl": "A_ef.tif", "format": "geotiff",
                       "manba": "MODIS Land Cover, 0.05°", "usul": "avto"},
        },
        "tavsiya": {"T_soat": 12, "dt": 120.0, "N": 60, "M": 60, "L": 20},
    }
    with open(os.path.join(kat, "manbalar.json"), "w", encoding="utf-8") as f:
        json.dump(tavsif, f, ensure_ascii=False, indent=2)
    return kat


def hammasini_yarat(asosiy="stsenariylar", jim=False):
    os.makedirs(asosiy, exist_ok=True)
    katlar = []
    for st in STSENARIYLAR:
        k = stsenariy_yarat(st, asosiy)
        katlar.append(k)
        if not jim:
            hajm = sum(os.path.getsize(os.path.join(k, f))
                       for f in os.listdir(k)) / 1024
            print(f"  {st['id']:<22} {st['nom']:<30} {hajm:7.0f} KB")
    return katlar


if __name__ == "__main__":
    hammasini_yarat()
