# -*- coding: utf-8 -*-
"""DustFlow uchun haqiqiy geofazoviy maʼlumotlarni yuklab olish.

Manbalar:
  ERA5-Land      shamol, harorat, tuproq namligi      Copernicus CDS   (kalit kerak)
  CAMS EAC4      chang, PM10, PM2.5 — validatsiya     Copernicus ADS   (kalit kerak)
  SoilGrids 2.0  gil ulushi, hajmiy zichlik           ISRIC WCS        (kalitsiz)
  Copernicus DEM relyef, 90 m                         AWS ochiq ombor  (kalitsiz)
  ESA WorldCover yer qoplami, 10 m -> z0, lambda, A_ef AWS ochiq ombor (kalitsiz)

Foydalanish:
  python malumot_yuklash.py tekshir
  python malumot_yuklash.py statik
  python malumot_yuklash.py era5  --dan 2025-07-28 --gacha 2025-07-30
  python malumot_yuklash.py cams  --dan 2025-07-28 --gacha 2025-07-30
  python malumot_yuklash.py stsenariy --vaqt "2025-07-29 12:00" --nom bo'ron_20250729

Batafsil yoʻriqnoma: YORIQNOMA_malumot.md
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import numpy as np

# Windows: chiqish yoʻnaltirilganda cp1251 da «ʻ» belgisi xatoga olib keladi
for _oqim in (sys.stdout, sys.stderr):
    try:
        _oqim.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------
# Hudud: Buxoro viloyati (kichik zaxira bilan)
# ---------------------------------------------------------------
LON0, LON1 = 61.5, 66.0
LAT0, LAT1 = 38.5, 42.0
QADAM = 0.01                 # statik maydonlar toʻri, gradus (~1 km)

KATALOG = "haqiqiy_malumot"
RHO_SUV = 1000.0             # suv zichligi, kg/m3

# SoilGrids 2.0 Markaziy Osiyo choʻllarida sinflarni ajrata olmaydi —
# Buxoro viloyati boʻyicha tekshiruvda barcha yer qoplami sinflari uchun
# gil ulushi ~0.29–0.30 chiqdi (profil maʼlumotlari siyrak, model mintaqaviy
# oʻrtachaga tortiladi). Shu sababli choʻl sinflari uchun Qizilqum qumli
# tuproqlari boʻyicha adabiyotdagi oraliq (2–10 %) qiymatlari olinadi;
# voha va qurilgan hududlar uchun SoilGrids saqlanadi.
CHOL_GIL = {60: 0.05, 20: 0.08, 30: 0.08, 100: 0.05}

# ---------------------------------------------------------------
# ESA WorldCover sinflari -> sirt parametrlari
#   z0     — gʻadir-budurlik uzunligi, m
#   lam    — oʻsimlik qoplamining frontal maydon indeksi
#   A_ef   — eroziyaga beriluvchan yuza ulushi
# Qiymatlar adabiyotdagi tipik baholar (Raupach 1993, Marticorena 1995)
# ---------------------------------------------------------------
QOPLAM_JADVAL = {
    10:  ("daraxtzor",              0.50,  0.30,  0.00),
    20:  ("butazor",                0.05,  0.05,  0.10),
    30:  ("oʻtloq",                 0.03,  0.03,  0.10),
    40:  ("ekinzor",                0.05,  0.05,  0.05),
    50:  ("qurilgan hudud",         1.00,  0.30,  0.00),
    60:  ("yalangʻoch / siyrak",    1e-3,  0.004, 0.25),
    70:  ("qor va muz",             1e-3,  0.00,  0.00),
    80:  ("doimiy suv",             1e-4,  0.00,  0.00),
    90:  ("botqoqlik",              0.03,  0.03,  0.00),
    95:  ("mangrov",                0.50,  0.30,  0.00),
    100: ("mox va lishaynik",       0.01,  0.01,  0.05),
}


# ===============================================================
# Umumiy yordamchi funksiyalar
# ===============================================================
def katalog(*qism):
    yol = os.path.join(KATALOG, *qism)
    os.makedirs(os.path.dirname(yol) if os.path.splitext(yol)[1] else yol,
                exist_ok=True)
    return yol


def maqsad_tor(qadam=QADAM):
    """Statik maydonlar uchun yagona geografik toʻr."""
    lon = np.arange(LON0 + qadam / 2, LON1, qadam)
    lat = np.arange(LAT0 + qadam / 2, LAT1, qadam)
    return lon, lat


def tif_yoz(yol, lon, lat, arr, birlik="", tavsif=""):
    """(nlon, nlat) massivni EPSG:4326 GeoTIFF ga yozadi."""
    import rasterio
    from rasterio.transform import from_origin
    dlon = float(lon[1] - lon[0]); dlat = float(lat[1] - lat[0])
    a = np.asarray(arr, dtype="float32").T[::-1, :]
    tr = from_origin(lon[0] - dlon / 2, lat[-1] + dlat / 2, dlon, dlat)
    with rasterio.open(yol, "w", driver="GTiff", height=a.shape[0],
                       width=a.shape[1], count=1, dtype="float32",
                       crs="EPSG:4326", transform=tr, compress="deflate",
                       nodata=-9999.0) as dst:
        dst.write(np.where(np.isfinite(a), a, -9999.0).astype("float32"), 1)
        dst.update_tags(units=birlik, description=tavsif)


def rastrdan_oqish(url, resampling="average", nodata=None):
    """Masofaviy yoki mahalliy rastrdan maqsad toʻriga kesib oʻqiydi.

    COG fayllarda obzorlardan foydalaniladi, shu sababli butun fayl
    yuklanmaydi — faqat kerakli hudud kerakli aniqlikda oʻqiladi.
    """
    import rasterio
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_origin

    lon, lat = maqsad_tor()
    dst = np.full((len(lat), len(lon)), np.nan, dtype="float32")
    tr = from_origin(LON0, LAT1, QADAM, QADAM)
    # faqat internet manzillari /vsicurl/ orqali ochiladi; mahalliy fayl —
    # Windows yoki Linux yoʻli boʻlishidan qatʼi nazar — toʻgʻridan-toʻgʻri
    manba = ("/vsicurl/" + url) if url.lower().startswith(("http://", "https://")) \
        else url
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.vrt",
                      GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="3"):
        # --- mos obzor darajasini tanlash ---
        # Manba maqsad toʻridan ancha aniq boʻlsa (masalan, WorldCover 10 m,
        # maqsad ~1 km), toʻliq aniqlikni oʻqish behuda. COG fayldagi tayyor
        # kichraytirilgan qatlamlardan maqsadga eng yaqini olinadi.
        daraja = None
        with rasterio.open(manba) as src:
            nisbat = QADAM / abs(src.res[0]) if src.crs and src.crs.is_geographic \
                else 1.0
            obzorlar = src.overviews(1)
            for i, f in enumerate(obzorlar):
                if f <= nisbat / 2:            # maqsaddan kamida 2 barobar aniqroq
                    daraja = i
        ochish = {"overview_level": daraja} if daraja is not None else {}
        with rasterio.open(manba, **ochish) as src:
            reproject(source=rasterio.band(src, 1), destination=dst,
                      src_nodata=nodata if nodata is not None else src.nodata,
                      dst_transform=tr, dst_crs="EPSG:4326", dst_nodata=np.nan,
                      resampling=getattr(Resampling, resampling))
    # (nlat, nlon) shimoldan janubga -> (nlon, nlat) janubdan shimolga
    return dst[::-1, :].T


def birlashtir(qatlamlar):
    """Bir nechta plitkani bitta maydonga yigʻadi (NaN boʻlmaganini oladi)."""
    natija = None
    for q in qatlamlar:
        if q is None:
            continue
        natija = q if natija is None else np.where(np.isfinite(natija), natija, q)
    return natija


# ===============================================================
# 1. RELYEF — Copernicus DEM GLO-90
# ===============================================================
def relyef():
    print("\n[relyef] Copernicus DEM GLO-90 yuklanmoqda...")
    qatlamlar = []
    for la in range(int(np.floor(LAT0)), int(np.ceil(LAT1))):
        for lo in range(int(np.floor(LON0)), int(np.ceil(LON1))):
            nom = f"Copernicus_DSM_COG_30_N{la:02d}_00_E{lo:03d}_00_DEM"
            url = f"https://copernicus-dem-90m.s3.amazonaws.com/{nom}/{nom}.tif"
            try:
                qatlamlar.append(rastrdan_oqish(url, "average"))
                print(f"    N{la} E{lo:03d}  ok")
            except Exception as e:
                print(f"    N{la} E{lo:03d}  oʻtkazildi ({type(e).__name__})")
    eta = birlashtir(qatlamlar)
    if eta is None:
        sys.exit("  [xato] relyef maʼlumoti olinmadi")
    # plitka chegarasidagi artefaktlar: juda past qiymatlar qoʻshnidan toʻldiriladi
    from scipy.ndimage import distance_transform_edt
    yomon = ~np.isfinite(eta) | (eta < 50.0)
    if yomon.any():
        idx = distance_transform_edt(yomon, return_distances=False, return_indices=True)
        eta = eta[tuple(idx)]
        print(f"  tuzatildi: {yomon.sum()} ta chegaraviy piksel")
    lon, lat = maqsad_tor()
    tif_yoz(katalog("statik", "relyef.tif"), lon, lat, eta, "m",
            "Copernicus DEM GLO-90, yer sirti balandligi")
    print(f"  saqlandi: relyef.tif   [{np.nanmin(eta):.0f} .. {np.nanmax(eta):.0f} m]")


# ===============================================================
# 2. TUPROQ — SoilGrids 2.0 (gil ulushi, hajmiy zichlik)
# ===============================================================
def soilgrids(xususiyat, qatlam="0-5cm", statistika="mean"):
    """SoilGrids WCS xizmatidan EPSG:4326 da kesib oladi."""
    cov = f"{xususiyat}_{qatlam}_{statistika}"
    p = {"map": f"/map/{xususiyat}.map", "SERVICE": "WCS", "VERSION": "2.0.1",
         "REQUEST": "GetCoverage", "COVERAGEID": cov, "FORMAT": "GEOTIFF_INT16",
         "SUBSETTINGCRS": "http://www.opengis.net/def/crs/EPSG/0/4326",
         "OUTPUTCRS": "http://www.opengis.net/def/crs/EPSG/0/4326"}
    url = ("https://maps.isric.org/mapserv?" + urllib.parse.urlencode(p) +
           f"&SUBSET=long({LON0},{LON1})&SUBSET=lat({LAT0},{LAT1})")
    vaqt = katalog("vaqtincha", f"{cov}.tif")
    for urinish in range(4):
        try:
            urllib.request.urlretrieve(url, vaqt)
            with open(vaqt, "rb") as f:
                bosh = f.read(4)
            if bosh[:2] in (b"II", b"MM"):          # haqiqiy GeoTIFF
                print(f"    {cov}  ok")
                break
            # server rasm oʻrniga XML xato qaytargan
            with open(vaqt, encoding="utf-8", errors="replace") as f:
                xabar = f.read(600)
            print(f"    urinish {urinish + 1}: server GeoTIFF emas, javob qaytardi:")
            print("      " + xabar.replace(chr(10), chr(10) + "      "))
        except Exception as e:
            print(f"    urinish {urinish + 1}: {e}")
        time.sleep(5)
    else:
        sys.exit(f"  [xato] SoilGrids dan {cov} olinmadi. Soʻrov manzili:\n  {url}")
    # SoilGrids faylida nodata belgilanmagan, maskalangan piksellar 0 ga teng.
    # Gil va zichlik uchun 0 fizik jihatdan mumkin emas — nodata deb olinadi.
    return rastrdan_oqish(vaqt, "average", nodata=0)


def tuproq():
    print("\n[tuproq] SoilGrids 2.0 yuklanmoqda...")
    # gil: xaritada ‰ (g/kg) butun son; /1000 -> massa ulushi
    gil = soilgrids("clay") / 1000.0
    # hajmiy zichlik: xaritada cg/cm3; /100 -> g/cm3
    bdod = soilgrids("bdod") / 100.0
    def taqsimot(a, nom, birlik):
        v = a[np.isfinite(a)]
        p = np.percentile(v, [1, 5, 50, 95, 99])
        print(f"    {nom}: 1%={p[0]:.3f}  5%={p[1]:.3f}  mediana={p[2]:.3f}  "
              f"95%={p[3]:.3f}  99%={p[4]:.3f} {birlik}")

    print("  xom taqsimot:")
    taqsimot(gil, "gil   ", "")
    taqsimot(bdod, "bdod  ", "g/cm3")

    # --- gil: NaN va aniq nol (suv, shahar maskasi) -> mediana ---
    gil_med = float(np.nanmedian(gil[gil > 0])) if np.any(gil > 0) else 0.10
    yomon_gil = ~np.isfinite(gil) | (gil <= 0.0)
    gil = np.clip(np.where(yomon_gil, gil_med, gil), 0.0, 0.8)

    # --- zichlik: mineral tuproqlar uchun fizik oraliq 1.0–2.0 g/cm3 ---
    # Bu oraliqdan tashqari qiymatlar (organik tuproq, maska chekkasi yoki
    # qayta toʻrlash artefakti) namlikni notoʻgʻri hisoblashga olib keladi.
    yaxshi = np.isfinite(bdod) & (bdod >= 1.0) & (bdod <= 2.0)
    bd_med = float(np.median(bdod[yaxshi])) if np.any(yaxshi) else 1.45
    bdod = np.where(yaxshi, bdod, bd_med)

    print(f"  almashtirildi: gil {np.mean(yomon_gil)*100:.1f} % nuqta "
          f"(mediana {gil_med:.3f} bilan), zichlik {np.mean(~yaxshi)*100:.1f} % "
          f"nuqta (mediana {bd_med:.2f} bilan)")

    # --- aralash yondashuv: choʻl sinflari uchun adabiyot qiymati ---
    sinf_yol = os.path.join(KATALOG, "statik", "sinf.tif")
    if os.path.exists(sinf_yol):
        sinf = _tif_torga(sinf_yol, *maqsad_tor()).round().astype(int)
        print("  aralash yondashuv (sinf boʻyicha mediana):")
        for k, v in CHOL_GIL.items():
            m = sinf == k
            if m.any():
                print(f"    sinf {k:>3}: SoilGrids {np.median(gil[m]):.3f} -> {v:.3f}")
                gil[m] = v
    else:
        print("  [eslatma] sinf.tif topilmadi — avval 'qoplam' ni bajaring, "
              "aks holda choʻl uchun SoilGrids qiymati qoladi")
    gil = np.clip(gil, 0.01, 0.8)

    lon, lat = maqsad_tor()
    tif_yoz(katalog("statik", "tuproq.tif"), lon, lat, gil, "-",
            "gil ulushi: choʻl — adabiyot, voha — SoilGrids 2.0")
    tif_yoz(katalog("statik", "bdod.tif"), lon, lat, bdod, "g/cm3",
            "SoilGrids 2.0, hajmiy zichlik 0-5 sm")
    print(f"  saqlandi: tuproq.tif  gil [{gil.min():.3f} .. {gil.max():.3f}]")
    print(f"  saqlandi: bdod.tif    zichlik [{bdod.min():.2f} .. {bdod.max():.2f}] g/cm3")


# ===============================================================
# 3. YER QOPLAMI — ESA WorldCover 2021 -> z0, lambda, A_ef
# ===============================================================
def qoplam():
    print("\n[qoplam] ESA WorldCover 2021 yuklanmoqda...")
    qatlamlar = []
    for la in range(int(np.floor(LAT0 / 3) * 3), int(np.ceil(LAT1 / 3) * 3), 3):
        for lo in range(int(np.floor(LON0 / 3) * 3), int(np.ceil(LON1 / 3) * 3), 3):
            tile = f"N{la:02d}E{lo:03d}"
            url = ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/"
                   f"v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif")
            try:
                # kategoriyali maydon — eng koʻp uchraydigan sinf olinadi
                qatlamlar.append(rastrdan_oqish(url, "mode", nodata=0))
                print(f"    {tile}  ok")
            except Exception as e:
                print(f"    {tile}  oʻtkazildi ({type(e).__name__})")
    sinf = birlashtir(qatlamlar)
    if sinf is None:
        sys.exit("  [xato] yer qoplami olinmadi")
    sinf = np.where(np.isfinite(sinf), sinf, 60).astype(int)

    z0 = np.full(sinf.shape, 1e-3); lam = np.zeros(sinf.shape); aef = np.zeros(sinf.shape)
    for k, (nom, z, l, a) in QOPLAM_JADVAL.items():
        m = sinf == k
        z0[m], lam[m], aef[m] = z, l, a

    lon, lat = maqsad_tor()
    tif_yoz(katalog("statik", "sinf.tif"), lon, lat, sinf, "-", "ESA WorldCover sinfi")
    tif_yoz(katalog("statik", "z0.tif"), lon, lat, z0, "m", "gʻadir-budurlik uzunligi")
    tif_yoz(katalog("statik", "qoplam.tif"), lon, lat, lam, "-",
            "oʻsimlik qoplami frontal maydon indeksi")
    tif_yoz(katalog("statik", "A_ef.tif"), lon, lat, aef, "-",
            "eroziyaga beriluvchan yuza ulushi")

    print("  sinflar taqsimoti:")
    for k, (nom, *_ ) in QOPLAM_JADVAL.items():
        ulush = float(np.mean(sinf == k)) * 100
        if ulush > 0.1:
            print(f"    {k:>3}  {nom:<22}{ulush:6.1f} %")


# ===============================================================
# 4. ERA5-Land — meteorologiya va tuproq namligi
# ===============================================================
def era5(dan, gacha):
    """ERA5-Land ni har bir oy uchun alohida, faqat kerakli kunlar bilan soʻraydi.

    CDS da yil/oy/kun roʻyxatlari oʻzaro kesishadi: bitta soʻrovda ikki oy
    berilsa, ikkala oyning barcha koʻrsatilgan kunlari yuklanib ketadi.
    Shuning uchun oralik oylarga boʻlinadi.
    """
    import cdsapi
    d0 = datetime.strptime(dan, "%Y-%m-%d"); d1 = datetime.strptime(gacha, "%Y-%m-%d")
    kunlar = [d0 + timedelta(days=i) for i in range((d1 - d0).days + 1)]
    oylar = {}
    for k in kunlar:
        oylar.setdefault((k.year, k.month), []).append(k.day)
    c = cdsapi.Client()
    for (y, m), kk in sorted(oylar.items()):
        yol = katalog("era5", f"era5land_{y}-{m:02d}-{kk[0]:02d}_{y}-{m:02d}-{kk[-1]:02d}.nc")
        print(f"\n[era5] ERA5-Land soʻrovi: {y}-{m:02d}, kunlar {kk[0]}–{kk[-1]}")
        c.retrieve("reanalysis-era5-land", {
            "variable": ["10m_u_component_of_wind", "10m_v_component_of_wind",
                         "2m_temperature", "volumetric_soil_water_layer_1"],
            "year": [str(y)], "month": [f"{m:02d}"], "day": [f"{d:02d}" for d in kk],
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": [LAT1, LON0, LAT0, LON1],          # shimol, gʻarb, janub, sharq
            "data_format": "netcdf",
            "download_format": "unarchived",
        }, yol)
        print(f"  saqlandi: {yol}")


# ===============================================================
# 5. CAMS EAC4 — validatsiya uchun chang maydoni
# ===============================================================
def _cdsapirc_kalit():
    """~/.cdsapirc dagi shaxsiy tokenni oʻqiydi (CDS va ADS uchun bir xil)."""
    rc = os.path.join(os.path.expanduser("~"), ".cdsapirc")
    if not os.path.exists(rc):
        return None
    with open(rc, encoding="utf-8") as f:
        for q in f:
            if q.strip().lower().startswith("key:"):
                return q.split(":", 1)[1].strip()
    return None


def cams(dan, gacha, ads_url, ads_kalit):
    import cdsapi
    ads_kalit = ads_kalit or _cdsapirc_kalit()
    if not ads_kalit:
        sys.exit("  [xato] kalit topilmadi: avval .cdsapirc faylini yarating")
    print(f"\n[cams] CAMS EAC4 soʻrovi: {dan} … {gacha}")
    c = cdsapi.Client(url=ads_url, key=ads_kalit)
    yol = katalog("cams", f"cams_eac4_{dan}_{gacha}.nc")
    c.retrieve("cams-global-reanalysis-eac4", {
        "variable": ["dust_aerosol_optical_depth_550nm",
                     "particulate_matter_10um", "particulate_matter_2.5um"],
        "date": f"{dan}/{gacha}",
        "time": ["00:00", "03:00", "06:00", "09:00",
                 "12:00", "15:00", "18:00", "21:00"],
        "area": [LAT1, LON0, LAT0, LON1],
        "data_format": "netcdf",
    }, yol)
    print(f"  saqlandi: {yol}")


# ===============================================================
# 6. STSENARIY — tanlangan soat uchun DustFlow katalogini yigʻish
# ===============================================================
def _nc_oqi(yol):
    """ERA5 NetCDF ni oʻqiydi (eski va yangi CDS formatlarini qoʻllab)."""
    from netCDF4 import Dataset, num2date
    ds = Dataset(yol)
    v = ds.variables
    lon = np.array(v["longitude" if "longitude" in v else "lon"][:], float)
    lat = np.array(v["latitude" if "latitude" in v else "lat"][:], float)
    tn = "valid_time" if "valid_time" in v else "time"
    vaqtlar = num2date(v[tn][:], v[tn].units,
                       getattr(v[tn], "calendar", "standard"))
    vaqtlar = [datetime(t.year, t.month, t.day, t.hour) for t in vaqtlar]
    return ds, lon, lat, vaqtlar


def _tif_torga(yol, lon, lat):
    """GeoTIFF ni berilgan (lon, lat) toʻriga ikki chiziqli interpolyatsiya qiladi."""
    import rasterio
    with rasterio.open(yol) as src:
        a = src.read(1).astype(float)
        if src.nodata is not None:
            a = np.where(a == src.nodata, np.nan, a)
        tr = src.transform
        slon = tr.c + tr.a * (np.arange(src.width) + 0.5)
        slat = tr.f + tr.e * (np.arange(src.height) + 0.5)
    a = a.T                                   # (nlon, nlat)
    if slat[0] > slat[-1]:
        slat = slat[::-1]; a = a[:, ::-1]
    ort = np.nanmean(a)
    a = np.where(np.isfinite(a), a, ort)
    oraliq = np.array([np.interp(lat, slat, a[i]) for i in range(a.shape[0])])
    return np.array([np.interp(lon, slon, oraliq[:, j]) for j in range(len(lat))]).T


def stsenariy(vaqt_str, nom, era5_fayl=None):
    from netCDF4 import Dataset
    print(f"\n[stsenariy] {nom}: {vaqt_str}")
    kerak = ["relyef.tif", "tuproq.tif", "bdod.tif", "z0.tif", "qoplam.tif", "A_ef.tif"]
    for f in kerak:
        if not os.path.exists(os.path.join(KATALOG, "statik", f)):
            sys.exit(f"  [xato] {f} topilmadi — avval: python {sys.argv[0]} statik")

    maqsad = datetime.strptime(vaqt_str, "%Y-%m-%d %H:%M")
    if era5_fayl is None:
        papka = os.path.join(KATALOG, "era5")
        fayllar = sorted(f for f in os.listdir(papka) if f.endswith(".nc")) \
            if os.path.isdir(papka) else []
        if not fayllar:
            sys.exit(f"  [xato] ERA5 fayli yoʻq — avval: python {sys.argv[0]} era5 ...")
        # kerakli soat qaysi faylda boʻlsa, oʻshani olamiz
        for f in fayllar:
            ds, lon, lat, vaqtlar = _nc_oqi(os.path.join(papka, f))
            if maqsad in vaqtlar:
                era5_fayl = os.path.join(papka, f)
                break
            ds.close()
        else:
            sys.exit(f"  [xato] {maqsad} hech bir ERA5 faylida yoʻq ({papka})")
    else:
        ds, lon, lat, vaqtlar = _nc_oqi(era5_fayl)
        if maqsad not in vaqtlar:
            sys.exit(f"  [xato] {maqsad} faylda yoʻq. Mavjud: {vaqtlar[0]} … {vaqtlar[-1]}")
    print(f"  ERA5 fayli: {os.path.basename(era5_fayl)}")
    it = vaqtlar.index(maqsad)

    def ol(nom_):
        a = np.array(ds.variables[nom_][it], float)
        return a.T if a.shape == (len(lat), len(lon)) else a

    u10, v10 = ol("u10"), ol("v10")
    t2m = ol("t2m")
    swvl1 = ol("swvl1")                                   # m3/m3
    ds.close()                  # ochiq qoldirilsa, koʻp soatli ishlatishda HDF5 qulaydi

    # kenglik kamayib borsa, oʻsish tartibiga keltiramiz
    if lat[0] > lat[-1]:
        lat = lat[::-1]
        u10, v10, t2m, swvl1 = (x[:, ::-1] for x in (u10, v10, t2m, swvl1))

    # --- hajmiy namlikdan ogʻirlik namligiga oʻtkazish ---
    #   w[%] = theta * rho_suv / rho_tuproq * 100
    bdod = _tif_torga(os.path.join(KATALOG, "statik", "bdod.tif"), lon, lat)
    w = swvl1 * RHO_SUV / (bdod * 1000.0) * 100.0
    w = np.where(np.isfinite(w), w, np.nanmean(w))

    kat = katalog("stsenariylar", nom)
    os.makedirs(kat, exist_ok=True)
    with Dataset(os.path.join(kat, "meteo.nc"), "w", format="NETCDF4_CLASSIC") as o:
        o.createDimension("lon", len(lon)); o.createDimension("lat", len(lat))
        x = o.createVariable("lon", "f8", ("lon",)); x[:] = lon; x.units = "degrees_east"
        y = o.createVariable("lat", "f8", ("lat",)); y[:] = lat; y.units = "degrees_north"
        for vn, arr, un, ln in [("u10", u10, "m s-1", "ERA5-Land 10m u"),
                                ("v10", v10, "m s-1", "ERA5-Land 10m v"),
                                ("t2m", t2m, "K", "ERA5-Land 2m harorat"),
                                ("swvl1", w, "percent", "ogʻirlik namligi (swvl1 dan)")]:
            vv = o.createVariable(vn, "f4", ("lat", "lon"), zlib=True)
            vv[:] = np.asarray(arr).T; vv.units = un; vv.long_name = ln
        o.source = f"ERA5-Land, {maqsad:%Y-%m-%d %H:%M} UTC"

    import shutil
    for f in kerak:
        if f != "bdod.tif":
            shutil.copy(os.path.join(KATALOG, "statik", f), os.path.join(kat, f))

    tavsif = {
        "id": nom, "nom": f"Haqiqiy maʼlumot: {maqsad:%Y-%m-%d %H:%M} UTC",
        "tavsif": "ERA5-Land, SoilGrids 2.0, Copernicus DEM, ESA WorldCover",
        "sana": f"{maqsad:%Y-%m-%d}", "mavsum": "",
        "soha": {"lon": [LON0, LON1], "lat": [LAT0, LAT1]},
        "maydonlar": {
            "u10":    {"fayl": "meteo.nc", "format": "netcdf", "ozgaruvchi": "u10",
                       "manba": "ERA5-Land, 0.1°", "usul": "interp"},
            "v10":    {"fayl": "meteo.nc", "format": "netcdf", "ozgaruvchi": "v10",
                       "manba": "ERA5-Land, 0.1°", "usul": "interp"},
            "namlik": {"fayl": "meteo.nc", "format": "netcdf", "ozgaruvchi": "swvl1",
                       "manba": "ERA5-Land swvl1 + SoilGrids bdod", "usul": "interp"},
            "relyef": {"fayl": "relyef.tif", "format": "geotiff",
                       "manba": "Copernicus DEM GLO-90", "usul": "ortala"},
            "qoplam": {"fayl": "qoplam.tif", "format": "geotiff",
                       "manba": "ESA WorldCover 2021", "usul": "avto"},
            "gil":    {"fayl": "tuproq.tif", "format": "geotiff",
                       "manba": "SoilGrids 2.0", "usul": "avto"},
            "z0":     {"fayl": "z0.tif", "format": "geotiff",
                       "manba": "ESA WorldCover 2021", "usul": "avto"},
            "A_ef":   {"fayl": "A_ef.tif", "format": "geotiff",
                       "manba": "ESA WorldCover 2021", "usul": "avto"},
        },
        "tavsiya": {"T_soat": 12, "dt": 120.0, "N": 60, "M": 60, "L": 20},
    }
    with open(os.path.join(kat, "manbalar.json"), "w", encoding="utf-8") as f:
        json.dump(tavsif, f, ensure_ascii=False, indent=2)

    U = np.sqrt(u10 ** 2 + v10 ** 2)
    print(f"  shamol U10  : {np.nanmin(U):.1f} .. {np.nanmax(U):.1f} m/s")
    print(f"  harorat     : {np.nanmin(t2m) - 273.15:.1f} .. {np.nanmax(t2m) - 273.15:.1f} °C")
    print(f"  namlik w    : {np.nanmin(w):.2f} .. {np.nanmax(w):.2f} %")
    print(f"  katalog     : {kat}")
    print(f"\n  Ishga tushirish:  python -m dustflow --katalog {os.path.dirname(kat)} "
          f"--stsenariy {nom}")


# ===============================================================
# 8. SoilGrids ishonchliligini tekshirish
# ===============================================================
def soilgrids_tekshir():
    """Qum ulushi va gil boʻyicha 90 % bashorat oraligʻini sinflar kesimida baholaydi."""
    print("\n[soilgrids_tekshir] qoʻshimcha qatlamlar yuklanmoqda...")
    sinf_yol = os.path.join(KATALOG, "statik", "sinf.tif")
    if not os.path.exists(sinf_yol):
        sys.exit("  [xato] sinf.tif yoʻq — avval: python malumot_yuklash.py qoplam")
    sinf = _tif_torga(sinf_yol, *maqsad_tor()).round().astype(int)

    # hammasi ‰ (g/kg) da; /10 -> %
    qum = soilgrids("sand") / 10.0
    gil = soilgrids("clay") / 10.0
    g05 = soilgrids("clay", statistika="Q0.05") / 10.0
    g95 = soilgrids("clay", statistika="Q0.95") / 10.0

    NOM = {60: "yalangʻoch/siyrak", 30: "oʻtloq", 20: "butazor",
           40: "ekinzor", 50: "qurilgan"}
    print("\n  SoilGrids 2.0, 0–5 sm qatlam, sinflar boʻyicha mediana (%)")
    print(f"  {'sinf':<20}{'ulush':>7}{'qum':>7}{'gil':>7}{'gil Q05':>9}"
          f"{'gil Q95':>9}{'oraliq':>8}{'nisbiy':>8}")
    print("  " + "-" * 75)
    natija = {}
    for k, n in NOM.items():
        m = (sinf == k) & np.isfinite(gil) & np.isfinite(g05) & np.isfinite(g95)
        if m.sum() < 20:
            continue
        r = dict(ulush=float(np.mean(sinf == k) * 100),
                 qum=float(np.nanmedian(qum[m])), gil=float(np.median(gil[m])),
                 q05=float(np.median(g05[m])), q95=float(np.median(g95[m])))
        r["oraliq"] = r["q95"] - r["q05"]
        r["nisbiy"] = r["oraliq"] / r["gil"] if r["gil"] > 0 else float("nan")
        natija[n] = r
        print(f"  {n:<20}{r['ulush']:6.1f}%{r['qum']:7.1f}{r['gil']:7.1f}"
              f"{r['q05']:9.1f}{r['q95']:9.1f}{r['oraliq']:8.1f}{r['nisbiy']:8.2f}")
    print("  " + "-" * 75)
    print("  oraliq = Q95 − Q05 (90 % bashorat oraligʻi kengligi, %)")
    print("  nisbiy = oraliq / mediana  (SoilGrids noaniqlik indeksiga mos)")
    with open(katalog("statik", "soilgrids_tekshiruv.json"), "w", encoding="utf-8") as f:
        json.dump(natija, f, ensure_ascii=False, indent=2)
    print(f"\n  saqlandi: {os.path.join(KATALOG, 'statik', 'soilgrids_tekshiruv.json')}")


# ===============================================================
# 9. CAMS faylidan changli va sokin kunlarni topish
# ===============================================================
BUXORO = (64.4286, 39.7747)          # monitoring.meteo.uz stansiyasi yaqini


def chang_kunlar(yol=None, n=10):
    from netCDF4 import Dataset, num2date
    if yol is None:
        papka = os.path.join(KATALOG, "cams")
        fayllar = sorted(f for f in os.listdir(papka) if f.endswith(".nc")) \
            if os.path.isdir(papka) else []
        if not fayllar:
            sys.exit("  [xato] CAMS fayli yoʻq — avval: python malumot_yuklash.py cams ...")
        yol = os.path.join(papka, fayllar[-1])
    print(f"\n[chang_kunlar] {yol}")
    with Dataset(yol) as ds:
        v = ds.variables
        lon = np.array(v["longitude" if "longitude" in v else "lon"][:], float)
        lat = np.array(v["latitude" if "latitude" in v else "lat"][:], float)
        tn = "valid_time" if "valid_time" in v else "time"
        vaqt = num2date(v[tn][:], v[tn].units, getattr(v[tn], "calendar", "standard"))
        vaqt = [datetime(t.year, t.month, t.day, t.hour) for t in vaqt]
        aod = np.array(v["duaod550"][:], float)            # (t, lat, lon)
        pm10 = np.array(v["pm10"][:], float) * 1e9         # kg/m3 -> mkg/m3
    i = int(np.argmin(np.abs(lon - BUXORO[0]))); j = int(np.argmin(np.abs(lat - BUXORO[1])))

    kunlik = {}
    for k, t in enumerate(vaqt):
        d = kunlik.setdefault(t.date(), dict(aod=[], pm_bux=[], pm_max=[]))
        d["aod"].append(float(np.nanmax(aod[k])))
        d["pm_bux"].append(float(pm10[k, j, i]))
        d["pm_max"].append(float(np.nanmax(pm10[k])))
    qator = sorted(((dd, max(x["aod"]), max(x["pm_bux"]), max(x["pm_max"]))
                    for dd, x in kunlik.items()), key=lambda z: z[1], reverse=True)

    def chiqar(sarlavha, ruyxat):
        print(f"\n  {sarlavha}")
        print(f"  {'sana':<12}{'chang AOD':>11}{'PM10 Buxoro':>14}{'PM10 maks.':>13}")
        for dd, a, pb, pm in ruyxat:
            print(f"  {dd.isoformat():<12}{a:11.3f}{pb:14.1f}{pm:13.1f}")
    chiqar(f"ENG CHANGLI {n} KUN (hudud boʻyicha maksimal chang AOD)", qator[:n])
    chiqar(f"ENG SOKIN {n} KUN", qator[-n:][::-1])
    print("\n  Validatsiya uchun: bitta changli kun va unga bir hafta ichidagi")
    print("  bitta sokin kun tanlang, soʻng ikkalasi uchun era5 ni yuklang.")


# ===============================================================
# 7. Oʻrnatishni tekshirish
# ===============================================================
def tekshir():
    print("Kutubxonalar:")
    xato = False
    for m in ("numpy", "rasterio", "netCDF4", "cdsapi"):
        try:
            mod = __import__(m)
            print(f"  {m:10s} ok   {getattr(mod, '__version__', '')}")
        except ImportError:
            print(f"  {m:10s} YOʻQ  ->  pip install {m}")
            xato = True
    rc = os.path.join(os.path.expanduser("~"), ".cdsapirc")
    print(f"\nCDS sozlamasi ({rc}): {'bor' if os.path.exists(rc) else 'YOʻQ'}")
    print("ADS kaliti: .cdsapirc dagi token ishlatiladi (CDS va ADS uchun bir xil)")
    print(f"\nHudud: {LON0}–{LON1}° E, {LAT0}–{LAT1}° N")
    return 1 if xato else 0


# ===============================================================
def main():
    p = argparse.ArgumentParser(description="DustFlow uchun haqiqiy maʼlumotlarni yuklash")
    s = p.add_subparsers(dest="buyruq", required=True)
    s.add_parser("tekshir", help="kutubxonalar va kalitlarni tekshirish")
    s.add_parser("statik", help="relyef, tuproq, yer qoplami (kalitsiz)")
    s.add_parser("relyef"); s.add_parser("tuproq"); s.add_parser("qoplam")
    for n in ("era5", "cams"):
        q = s.add_parser(n)
        q.add_argument("--dan", required=True, help="YYYY-MM-DD")
        q.add_argument("--gacha", required=True, help="YYYY-MM-DD")
        if n == "cams":
            q.add_argument("--ads-url", default=os.environ.get(
                "ADS_URL", "https://ads.atmosphere.copernicus.eu/api"))
            q.add_argument("--ads-kalit", default=os.environ.get("ADS_KEY"))
    s.add_parser("soilgrids_tekshir", help="SoilGrids ishonchliligini sinflar boʻyicha tekshirish")
    q = s.add_parser("chang_kunlar", help="CAMS faylidan changli va sokin kunlarni topish")
    q.add_argument("--fayl", default=None)
    q.add_argument("-n", type=int, default=10)
    q = s.add_parser("stsenariy", help="tanlangan soat uchun stsenariy katalogi")
    q.add_argument("--vaqt", required=True, help='"YYYY-MM-DD HH:MM" (UTC)')
    q.add_argument("--nom", required=True)
    q.add_argument("--era5", default=None, help="ERA5 fayli (koʻrsatilmasa — oxirgisi)")
    a = p.parse_args()

    if a.buyruq == "tekshir":
        return tekshir()
    if a.buyruq in ("statik", "relyef"):
        relyef()
    if a.buyruq in ("statik", "qoplam"):
        qoplam()                     # tuproqdan oldin: gil sinflarga bogʻliq
    if a.buyruq in ("statik", "tuproq"):
        tuproq()
    if a.buyruq == "era5":
        era5(a.dan, a.gacha)
    if a.buyruq == "cams":
        cams(a.dan, a.gacha, a.ads_url, a.ads_kalit)
    if a.buyruq == "soilgrids_tekshir":
        soilgrids_tekshir()
    if a.buyruq == "chang_kunlar":
        chang_kunlar(a.fayl, a.n)
    if a.buyruq == "stsenariy":
        stsenariy(a.vaqt, a.nom, a.era5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
