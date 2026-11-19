# -*- coding: utf-8 -*-
"""Geofazoviy ma'lumotlarni o'qish va hisoblash to'riga keltirish moduli.

Qo'llab-quvvatlanadigan formatlar:
  NetCDF  (.nc)  — meteorologik maydonlar, tuproq namligi (ERA5, ERA5-Land, SMAP)
  GeoTIFF (.tif) — relyef (SRTM), o'simlik qoplami (MODIS), tuproq (SoilGrids)

Barcha maydonlar geografik koordinatalarda (lon, lat) beriladi va
ekvitoreal proyeksiya orqali hisoblash to'riga (x, y, metr) keltiriladi.
"""
import os
import json
import numpy as np

DEG_LAT = 110574.0          # 1 gradus kenglik, m


def deg_lon(lat_ref: float) -> float:
    """1 gradus uzunlikning metrdagi qiymati berilgan kenglikda."""
    return 111320.0 * np.cos(np.deg2rad(lat_ref))


def geo_to_xy(lon, lat, lon0, lat0):
    """Geografik koordinatalardan metrik koordinatalarga."""
    lat_ref = 0.5 * (np.min(lat) + np.max(lat))
    x = (np.asarray(lon) - lon0) * deg_lon(lat_ref)
    y = (np.asarray(lat) - lat0) * DEG_LAT
    return x, y


# ---------------------------------------------------------------
# O'qish
# ---------------------------------------------------------------
def nc_oqish(yol, ozgaruvchi):
    """NetCDF faylidan maydonni o'qiydi -> (lon, lat, qiymat(nlon,nlat), birlik)."""
    from netCDF4 import Dataset
    with Dataset(yol) as ds:
        lon = np.array(ds.variables["lon"][:], dtype=float)
        lat = np.array(ds.variables["lat"][:], dtype=float)
        v = ds.variables[ozgaruvchi]
        a = np.array(v[:], dtype=float)
        birlik = getattr(v, "units", "")
        if a.shape == (len(lat), len(lon)):
            a = a.T
    return lon, lat, a, birlik


def tif_oqish(yol, kanal=1):
    """GeoTIFF faylidan maydonni o'qiydi -> (lon, lat, qiymat(nlon,nlat), birlik)."""
    import rasterio
    with rasterio.open(yol) as src:
        a = src.read(kanal).astype(float)
        if src.nodata is not None:
            a = np.where(a == src.nodata, np.nan, a)
        tr = src.transform
        nrow, ncol = a.shape
        lon = tr.c + tr.a * (np.arange(ncol) + 0.5)
        lat = tr.f + tr.e * (np.arange(nrow) + 0.5)
        tags = src.tags() or {}
        birlik = tags.get("units", "")
    a = a.T
    if lat[0] > lat[-1]:
        lat = lat[::-1]
        a = a[:, ::-1]
    return lon, lat, a, birlik


# ---------------------------------------------------------------
# Hisoblash to'riga keltirish
# ---------------------------------------------------------------
def torga_keltir(lon, lat, qiymat, tor, lon0, lat0, usul="avto"):
    """Manba to'ridan hisoblash to'riga keltiradi.

    usul = "interp"  — ikki chiziqli interpolyatsiya (manba qo'polroq)
    usul = "ortala"  — yacheyka bo'yicha o'rtalash (manba aniqroq)
    usul = "avto"    — qadamlarni solishtirib avtomatik tanlanadi
    """
    xs, ys = geo_to_xy(lon, lat, lon0, lat0)
    if usul == "avto":
        usul = "ortala" if float(np.mean(np.diff(xs))) < 0.5 * tor.dx else "interp"

    if usul == "ortala":
        xk = np.concatenate(([tor.x[0] - tor.dx / 2],
                             tor.x[:-1] + tor.dx / 2,
                             [tor.x[-1] + tor.dx / 2]))
        yk = np.concatenate(([tor.y[0] - tor.dy / 2],
                             tor.y[:-1] + tor.dy / 2,
                             [tor.y[-1] + tor.dy / 2]))
        ix = np.clip(np.digitize(xs, xk) - 1, 0, tor.N)
        iy = np.clip(np.digitize(ys, yk) - 1, 0, tor.M)
        yig = np.zeros((tor.N + 1, tor.M + 1))
        son = np.zeros((tor.N + 1, tor.M + 1))
        for a_i, i in enumerate(ix):
            np.add.at(yig[i], iy, np.nan_to_num(qiymat[a_i]))
            np.add.at(son[i], iy, (~np.isnan(qiymat[a_i])).astype(float))
        natija = np.where(son == 0, np.nan, yig / np.maximum(son, 1))
        if np.any(np.isnan(natija)):
            natija = _bosh_toldir(natija)
        return natija

    ort = np.nanmean(qiymat)
    oraliq = np.empty((tor.N + 1, len(ys)))
    for j in range(len(ys)):
        oraliq[:, j] = np.interp(tor.x, xs, np.nan_to_num(qiymat[:, j], nan=ort))
    natija = np.empty((tor.N + 1, tor.M + 1))
    for i in range(tor.N + 1):
        natija[i] = np.interp(tor.y, ys, oraliq[i])
    return natija


def _bosh_toldir(a):
    """NaN qiymatlarni eng yaqin qiymat bilan to'ldiradi."""
    from scipy.ndimage import distance_transform_edt
    bosh = np.isnan(a)
    if not np.any(bosh):
        return a
    ind = distance_transform_edt(bosh, return_distances=False, return_indices=True)
    return a[tuple(ind)]


# ---------------------------------------------------------------
# Stsenariy ma'lumotlarini yuklash
# ---------------------------------------------------------------
def stsenariy_yukla(katalog, tor, lon0=61.5, lat0=38.5, jim=True):
    """Stsenariy katalogidagi barcha maydonlarni o'qiydi va to'riga keltiradi."""
    from .data import KirishMaydonlari

    with open(os.path.join(katalog, "manbalar.json"), encoding="utf-8") as f:
        tavsif = json.load(f)

    maydonlar, manbalar = {}, {}
    for nom, m in tavsif["maydonlar"].items():
        yol = os.path.join(katalog, m["fayl"])
        if m["format"] == "netcdf":
            lon, lat, a, _ = nc_oqish(yol, m["ozgaruvchi"])
        elif m["format"] == "geotiff":
            lon, lat, a, _ = tif_oqish(yol, m.get("kanal", 1))
        else:
            raise ValueError(f"noma'lum format: {m['format']}")
        maydonlar[nom] = torga_keltir(lon, lat, a, tor, lon0, lat0,
                                      m.get("usul", "avto"))
        manbalar[nom] = m.get("manba", "")
        if not jim:
            print(f"  {nom:10s} {m['fayl']:<14} {str(a.shape):>12} -> "
                  f"{maydonlar[nom].shape}  "
                  f"[{np.nanmin(a):.4g} .. {np.nanmax(a):.4g}]")

    U10 = np.sqrt(maydonlar["u10"] ** 2 + maydonlar["v10"] ** 2)
    yonalish = np.rad2deg(np.arctan2(maydonlar["v10"], maydonlar["u10"]))

    k = KirishMaydonlari(
        U10=U10, yonalish=yonalish,
        w=maydonlar["namlik"], m_cl=maydonlar["gil"],
        lam=maydonlar["qoplam"], z0=maydonlar["z0"],
        A_ef=maydonlar["A_ef"], eta=maydonlar["relyef"],
        manba=manbalar)
    return k, tavsif


def stsenariylar_royxati(asosiy_katalog):
    """Katalogdagi barcha stsenariylarni ro'yxatlaydi."""
    r = []
    if not os.path.isdir(asosiy_katalog):
        return r
    for nom in sorted(os.listdir(asosiy_katalog)):
        yol = os.path.join(asosiy_katalog, nom)
        man = os.path.join(yol, "manbalar.json")
        if os.path.isfile(man):
            with open(man, encoding="utf-8") as f:
                t = json.load(f)
            r.append(dict(id=nom, yol=yol, nom=t.get("nom", nom),
                          tavsif=t.get("tavsif", ""),
                          sana=t.get("sana", ""),
                          mavsum=t.get("mavsum", ""),
                          tavsiya=t.get("tavsiya", {})))
    return r
