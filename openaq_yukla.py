# -*- coding: utf-8 -*-
"""OpenAQ arxividan havo sifati ma'lumotlarini yuklab olish.

Skript ikki rejimda ishlaydi:

  1) qamrovni tekshirish — mamlakat bo'yicha qanday stansiyalar bor,
     ular qaysi ko'rsatkichlarni o'lchaydi va qaysi davrni qamrab oladi;

  2) yuklab olish — tanlangan stansiyalar uchun soatlik qatorlarni olib,
     CSV faylga va DustFlow ma'lumotlar bazasiga yozadi.

OpenAQ v3 API kaliti talab qiladi (bepul): https://explore.openaq.org/register
Kalitni OPENAQ_API_KEY muhit o'zgaruvchisiga yozing yoki --kalit bilan bering.

Foydalanish:
    python openaq_yukla.py --qamrov
    python openaq_yukla.py --qamrov --mamlakat KZ
    python openaq_yukla.py --stansiya 12345 --dan 2025-04-01 --gacha 2025-05-01
    python openaq_yukla.py --shahar Bukhara --dan 2025-01-01 --gacha 2026-01-01
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

BAZA = "https://api.openaq.org/v3"
KECHIKISH = 1.1          # so'rovlar orasidagi pauza, s (tezlik cheklovi uchun)
CHEKLOV = 1000           # bir sahifadagi maksimal yozuv


# ===============================================================
# API bilan ishlash
# ===============================================================
def sorov(yol, kalit, **parametrlar):
    """OpenAQ API ga so'rov yuboradi va JSON qaytaradi."""
    url = f"{BAZA}/{yol}"
    if parametrlar:
        url += "?" + urllib.parse.urlencode(
            {k: v for k, v in parametrlar.items() if v is not None})
    req = urllib.request.Request(url, headers={
        "X-API-Key": kalit,
        "Accept": "application/json",
        "User-Agent": "DustFlow/1.0 (research)"})
    for urinish in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:                     # tezlik cheklovi
                kut = 5 * (urinish + 1)
                print(f"    [tezlik cheklovi] {kut} s kutilmoqda...")
                time.sleep(kut)
                continue
            if e.code == 401:
                sys.exit("  [xato] API kaliti noto'g'ri yoki berilmagan.\n"
                         "  Bepul kalit: https://explore.openaq.org/register")
            if e.code == 404:
                return None
            raise
        except urllib.error.URLError as e:
            print(f"    [tarmoq xatosi] {e.reason}, qayta urinish...")
            time.sleep(3)
    return None


# ===============================================================
# 1-rejim: qamrovni tekshirish
# ===============================================================
def mamlakat_id(kalit, kod):
    """ISO kod bo'yicha mamlakat identifikatorini topadi."""
    d = sorov("countries", kalit, limit=200)
    if not d:
        return None
    for c in d.get("results", []):
        if c.get("code", "").upper() == kod.upper():
            return c["id"], c.get("name", kod)
    return None


def qamrov(kalit, kod="UZ"):
    """Mamlakat bo'yicha mavjud stansiyalarni ro'yxatlaydi."""
    m = mamlakat_id(kalit, kod)
    if not m:
        print(f"  '{kod}' mamlakati OpenAQ ro'yxatida topilmadi.")
        return []
    mid, nomi = m
    print("=" * 96)
    print(f"  OpenAQ qamrovi: {nomi} ({kod}), id = {mid}")
    print("=" * 96)

    stansiyalar, sahifa = [], 1
    while True:
        d = sorov("locations", kalit, countries_id=mid, limit=200, page=sahifa)
        if not d or not d.get("results"):
            break
        stansiyalar += d["results"]
        if len(d["results"]) < 200:
            break
        sahifa += 1
        time.sleep(KECHIKISH)

    if not stansiyalar:
        print("  Stansiya topilmadi.")
        print("\n  Bu shuni bildiradiki, OpenAQ da bu mamlakat bo'yicha ma'lumot yo'q.")
        print("  Muqobil manbalar: monitoring.meteo.uz (O'zgidromet), aqicn.org (WAQI).")
        return []

    print(f"{'id':>8}  {'nomi':<34}{'koordinata':<22}{'koʻrsatkichlar':<26}{'oxirgi yozuv'}")
    print("-" * 96)
    for s in stansiyalar:
        koord = s.get("coordinates") or {}
        xy = (f"{koord.get('latitude', 0):.3f}, {koord.get('longitude', 0):.3f}"
              if koord else "—")
        par = ", ".join(sorted({p.get("parameter", {}).get("name", "?")
                                if isinstance(p.get("parameter"), dict)
                                else p.get("name", "?")
                                for p in s.get("sensors", [])}))[:24]
        oxirgi = (s.get("datetimeLast") or {}).get("utc", "—")[:10]
        print(f"{s['id']:>8}  {s.get('name', '—')[:34]:<34}{xy:<22}{par:<26}{oxirgi}")
    print("-" * 96)
    print(f"  Jami: {len(stansiyalar)} ta stansiya")

    chang = [s for s in stansiyalar
             if any("pm" in (p.get("parameter", {}).get("name", "")
                             if isinstance(p.get("parameter"), dict)
                             else p.get("name", "")).lower()
                    for p in s.get("sensors", []))]
    print(f"  Shundan PM oʻlchaydiganlari: {len(chang)} ta")
    return stansiyalar


# ===============================================================
# 2-rejim: ma'lumotni yuklab olish
# ===============================================================
def sensorlar(kalit, stansiya_id):
    d = sorov(f"locations/{stansiya_id}", kalit)
    if not d or not d.get("results"):
        return []
    return d["results"][0].get("sensors", [])


def olchovlar(kalit, sensor_id, dan, gacha):
    """Bitta sensor bo'yicha soatlik qiymatlarni yuklaydi."""
    natija, sahifa = [], 1
    while True:
        d = sorov(f"sensors/{sensor_id}/hours", kalit,
                  datetime_from=dan, datetime_to=gacha,
                  limit=CHEKLOV, page=sahifa)
        if not d or not d.get("results"):
            break
        natija += d["results"]
        if len(d["results"]) < CHEKLOV:
            break
        sahifa += 1
        time.sleep(KECHIKISH)
        if sahifa > 60:                       # himoya chegarasi
            break
    return natija


def yukla(kalit, stansiya_idlar, dan, gacha, chiqish="openaq_malumot.csv"):
    qatorlar = []
    for sid in stansiya_idlar:
        d = sorov(f"locations/{sid}", kalit)
        if not d or not d.get("results"):
            print(f"  [{sid}] stansiya topilmadi")
            continue
        st = d["results"][0]
        koord = st.get("coordinates") or {}
        print(f"\n  [{sid}] {st.get('name', '—')}  "
              f"({koord.get('latitude', 0):.3f}, {koord.get('longitude', 0):.3f})")
        for s in st.get("sensors", []):
            par = s.get("parameter", {})
            nom = par.get("name") if isinstance(par, dict) else s.get("name", "?")
            if "pm" not in str(nom).lower():
                continue
            birlik = par.get("units", "") if isinstance(par, dict) else ""
            print(f"      {nom} yuklanmoqda...", end="", flush=True)
            m = olchovlar(kalit, s["id"], dan, gacha)
            print(f" {len(m)} ta yozuv")
            for z in m:
                vaqt = (z.get("period", {}).get("datetimeFrom", {}) or {}).get("utc")
                qatorlar.append(dict(
                    stansiya_id=sid, stansiya=st.get("name", ""),
                    lat=koord.get("latitude"), lon=koord.get("longitude"),
                    korsatkich=nom, birlik=birlik,
                    sana=vaqt, qiymat=z.get("value")))
            time.sleep(KECHIKISH)

    if not qatorlar:
        print("\n  Maʼlumot yuklanmadi.")
        return []

    with open(chiqish, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(qatorlar[0].keys()))
        w.writeheader(); w.writerows(qatorlar)
    print(f"\n  Saqlandi: {chiqish}  ({len(qatorlar)} ta yozuv)")
    return qatorlar


# ===============================================================
# DustFlow bazasiga yozish
# ===============================================================
def bazaga_yoz(qatorlar, baza_yoli="dustflow.db"):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from dustflow.db import Baza
    except ImportError:
        print("  [eslatma] DustFlow topilmadi, bazaga yozish oʻtkazib yuborildi")
        return
    b = Baza(baza_yoli)
    jamlangan = {}
    for q in qatorlar:
        kalit = (q["stansiya"], q["sana"])
        z = jamlangan.setdefault(kalit, dict(stansiya=q["stansiya"],
                                             x=q["lon"], y=q["lat"],
                                             sana=q["sana"], C_pm10=None,
                                             C_pm25=None))
        nom = str(q["korsatkich"]).lower()
        if nom == "pm10":
            z["C_pm10"] = q["qiymat"]
        elif nom in ("pm25", "pm2.5"):
            z["C_pm25"] = q["qiymat"]
    for z in jamlangan.values():
        b.kuzatuv_yozish(z["stansiya"], z["x"], z["y"], z["sana"],
                         C_pm10=z["C_pm10"], C_pm25=z["C_pm25"],
                         izoh="OpenAQ")
    print(f"  Bazaga yozildi: {len(jamlangan)} ta yozuv -> {baza_yoli}")


# ===============================================================
def main():
    p = argparse.ArgumentParser(
        description="OpenAQ arxividan havo sifati maʼlumotlarini yuklash")
    p.add_argument("--kalit", default=os.environ.get("OPENAQ_API_KEY"),
                   help="OpenAQ API kaliti (yoki OPENAQ_API_KEY muhit oʻzgaruvchisi)")
    p.add_argument("--qamrov", action="store_true",
                   help="mamlakat boʻyicha mavjud stansiyalarni koʻrsatish")
    p.add_argument("--mamlakat", default="UZ", help="ISO kodi (UZ, KZ, TM, ...)")
    p.add_argument("--stansiya", nargs="+", type=int, help="stansiya id lari")
    p.add_argument("--shahar", help="nomi boʻyicha stansiya qidirish")
    p.add_argument("--dan", default=None, help="boshlanish sanasi, YYYY-MM-DD")
    p.add_argument("--gacha", default=None, help="tugash sanasi, YYYY-MM-DD")
    p.add_argument("-o", "--chiqish", default="openaq_malumot.csv")
    p.add_argument("--baza", default=None, help="DustFlow bazasiga ham yozish")
    a = p.parse_args()

    if not a.kalit:
        sys.exit("  [xato] API kaliti berilmagan.\n"
                 "  Bepul roʻyxatdan oʻtish: https://explore.openaq.org/register\n"
                 "  Soʻngra: export OPENAQ_API_KEY=...  yoki  --kalit ...")

    if a.qamrov or not (a.stansiya or a.shahar):
        st = qamrov(a.kalit, a.mamlakat)
        if not a.stansiya and not a.shahar:
            return 0

    idlar = list(a.stansiya) if a.stansiya else []
    if a.shahar:
        st = st if a.qamrov else qamrov(a.kalit, a.mamlakat)
        idlar += [s["id"] for s in st
                  if a.shahar.lower() in str(s.get("name", "")).lower()]
        if not idlar:
            sys.exit(f"  '{a.shahar}' boʻyicha stansiya topilmadi")

    gacha = a.gacha or datetime.utcnow().strftime("%Y-%m-%d")
    dan = a.dan or (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
    print(f"\n  Davr: {dan} … {gacha}")
    q = yukla(a.kalit, idlar, dan, gacha, a.chiqish)
    if q and a.baza:
        bazaga_yoz(q, a.baza)
    return 0


if __name__ == "__main__":
    sys.exit(main())
