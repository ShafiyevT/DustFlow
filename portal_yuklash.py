# -*- coding: utf-8 -*-
"""air-uzbekistan.uz (Oʻzgidromet «DigitalMeteo» portali) soatlik arxivini yuklash.

API (brauzer soʻrovlaridan aniqlangan):
    /api/horiba.php                          — stansiyalar roʻyxati va koordinatalari
    /api/horiba-heatmap-city.php?city=..&from=YYYY/MM/DD&to=YYYY/MM/DD&binHours=1
        — shahar stansiyasining soatlik PM2.5 va PM10 qiymatlari.
          «to» sanasi natijaga KIRMAYDI (u kun qatori boʻsh qaytadi).

Foydalanish:
    py portal_yuklash.py                                   # standart davrlar va shaharlar
    py portal_yuklash.py --dan 2025-04-20 --gacha 2025-05-01
    py portal_yuklash.py --shahar bukhara navoi --dan 2026-02-14 --gacha 2026-02-17

Natija:
    portal_soatlik.csv  — barcha soatlik qiymatlar (mahalliy va UTC vaqt bilan)
    portal_xom\\         — serverning asl JSON javoblari (manba sifatida saqlanadi)
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

for _oqim in (sys.stdout, sys.stderr):
    try:
        _oqim.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BAZA = "https://air-uzbekistan.uz/api"
XOM = "portal_xom"
CSV_FAYL = "portal_soatlik.csv"
MAHALLIY = timezone(timedelta(hours=5))
BOLAK = 7                                   # bitta soʻrovdagi kunlar soni

# shahar nomlari (city parametri); bir nechta variant sinab koʻriladi
SHAHARLAR = {
    "bukhara": ["bukhara"],
    "navoi":   ["navoi", "navoiy"],
    "qarshi":  ["qarshi", "karshi"],
}
STANDART_DAVRLAR = [("2025-04-20", "2025-05-01"), ("2026-02-14", "2026-02-17")]

MAYDONLAR = ["shahar", "stansiya_id", "stansiya", "lat", "lon",
             "vaqt_mahalliy", "vaqt_utc", "pm25", "pm10"]


def olish(yol, **par):
    par["_ts"] = int(time.time() * 1000)
    url = f"{BAZA}/{yol}?{urllib.parse.urlencode(par)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (DustFlow research; BuxDU)",
        "Referer": "https://air-uzbekistan.uz/",
        "Accept": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return url, r.read().decode("utf-8")
        except Exception as e:
            if i == 2:
                print(f"    [xato] {e}")
                return url, None
            time.sleep(4)


def xom_saqla(nom, matn):
    os.makedirs(XOM, exist_ok=True)
    with open(os.path.join(XOM, nom), "w", encoding="utf-8") as f:
        f.write(matn)


def stansiyalar():
    """horiba.php dan stansiya id -> (nom, lat, lon)."""
    _, matn = olish("horiba.php")
    if not matn:
        return {}
    xom_saqla("horiba_stansiyalar.json", matn)
    return {s["id"]: (s["name"], s["latitude"], s["longitude"]) for s in json.loads(matn)}


def ajrat(d, shahar, st_royxat):
    """heatmap javobidan soatlik qatorlarni ajratadi."""
    sid = d.get("stationId")
    nom, lat, lon = st_royxat.get(sid, (d.get("stationName", ""), None, None))
    qatorlar = []
    for qator in d.get("matrix", []):
        for c in qator:
            if not c or c.get("pm10") is None and c.get("pm25") is None:
                continue
            t = datetime.fromtimestamp(c["from"], tz=timezone.utc)
            qatorlar.append(dict(
                shahar=shahar, stansiya_id=sid, stansiya=nom, lat=lat, lon=lon,
                vaqt_mahalliy=t.astimezone(MAHALLIY).strftime("%Y-%m-%d %H:%M"),
                vaqt_utc=t.strftime("%Y-%m-%d %H:%M"),
                pm25=c.get("pm25"), pm10=c.get("pm10")))
    return qatorlar


def shahar_yukla(kalit, dan, gacha, st_royxat):
    d0 = datetime.strptime(dan, "%Y-%m-%d")
    d1 = datetime.strptime(gacha, "%Y-%m-%d") + timedelta(days=1)   # «to» kirmaydi
    hammasi, slug = [], None
    for variant in SHAHARLAR.get(kalit, [kalit]):
        _, matn = olish("horiba-heatmap-city.php", city=variant,
                        **{"from": d0.strftime("%Y/%m/%d"),
                           "to": min(d0 + timedelta(days=1), d1).strftime("%Y/%m/%d"),
                           "binHours": 1})
        try:
            if matn and json.loads(matn).get("ok"):
                slug = variant
                break
        except ValueError:
            pass
    if slug is None:
        print(f"  [{kalit}] portal bu shaharni tanimadi (sinalgan: {SHAHARLAR.get(kalit)})")
        return []
    t = d0
    while t < d1:
        t2 = min(t + timedelta(days=BOLAK), d1)
        _, matn = olish("horiba-heatmap-city.php", city=slug,
                        **{"from": t.strftime("%Y/%m/%d"), "to": t2.strftime("%Y/%m/%d"),
                           "binHours": 1})
        if matn:
            xom_saqla(f"{slug}_{t:%Y%m%d}_{t2:%Y%m%d}.json", matn)
            try:
                q = ajrat(json.loads(matn), kalit, st_royxat)
            except ValueError:
                print(f"    [{slug}] {t:%Y-%m-%d}: JSON emas — xom faylga qarang")
                q = []
            kutilgan = int((t2 - t).total_seconds() // 3600)
            print(f"  [{slug}] {t:%Y-%m-%d} … {t2 - timedelta(days=1):%Y-%m-%d}: "
                  f"{len(q)}/{kutilgan} soat")
            hammasi += q
        t = t2
        time.sleep(1.0)
    return hammasi


def yoz(qatorlar, yol=CSV_FAYL):
    bor = {}
    if os.path.exists(yol):
        with open(yol, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                bor[(r["shahar"], r["vaqt_utc"])] = r
    for q in qatorlar:
        bor[(q["shahar"], q["vaqt_utc"])] = q                 # yangisi ustun
    with open(yol, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=MAYDONLAR)
        w.writeheader()
        w.writerows(sorted(bor.values(), key=lambda r: (r["shahar"], r["vaqt_utc"])))
    return len(bor)


def main():
    p = argparse.ArgumentParser(description="DigitalMeteo portali soatlik arxivini yuklash")
    p.add_argument("--shahar", nargs="+", default=list(SHAHARLAR))
    p.add_argument("--dan"); p.add_argument("--gacha")
    a = p.parse_args()
    davrlar = [(a.dan, a.gacha)] if a.dan and a.gacha else STANDART_DAVRLAR

    print("Stansiyalar roʻyxati...")
    st = stansiyalar()
    print(f"  {len(st)} ta stansiya")
    qatorlar = []
    for dan, gacha in davrlar:
        print(f"\nDavr: {dan} … {gacha}")
        for sh in a.shahar:
            qatorlar += shahar_yukla(sh, dan, gacha, st)
    n = yoz(qatorlar)
    print(f"\nJami yozuvlar: {n}  ->  {os.path.abspath(CSV_FAYL)}")
    print(f"Asl javoblar:  {os.path.abspath(XOM)}")


if __name__ == "__main__":
    main()
