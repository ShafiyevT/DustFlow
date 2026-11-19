# -*- coding: utf-8 -*-
"""Oʻzgidromet avtomatik stansiyalaridan havo sifati maʼlumotlarini yigʻish.

monitoring.meteo.uz sayti arxiv saqlamaydi — faqat oxirgi soatlik qiymatni
koʻrsatadi. Shu sababli skript har soatda ishga tushirilib, qiymatlarni CSV
faylga (va ixtiyoriy ravishda DustFlow bazasiga) qoʻshib boradi.

Foydalanish:
    python uzgidromet_yigish.py                     # standart stansiyalar
    python uzgidromet_yigish.py --stansiya 723 722  # tanlangan stansiyalar
    python uzgidromet_yigish.py --qidir 700 740     # qaysi id lar mavjudligini aniqlash
    python uzgidromet_yigish.py --baza dustflow.db  # bazaga ham yozish
"""
import argparse
import csv
import html
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta

# Windows: chiqish faylga yoki rejalashtirilgan vazifaga yoʻnaltirilganda Python
# eski kodlashni (cp1251) ishlatadi va oʻzbekcha «ʻ» belgisida qulab tushadi.
# Chiqishni UTF-8 ga majburan oʻtkazamiz — shunda xabar chiqarish hech qachon
# maʼlumot yigʻishni toʻxtatmaydi.
for _oqim in (sys.stdout, sys.stderr):
    try:
        _oqim.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

URL = "https://monitoring.meteo.uz/ru/map/view/{}"

# Stansiya sahifalarida koordinata YOʻQ: pastdagi xarita — Oʻzgidromet bosh idorasi
# (Toshkent). Shu sababli koordinatalar shu jadvaldan olinadi. Ular shahar
# markazining taxminiy nuqtasi (meteo.uz shahar koordinatalari); aniq joylashuvni
# Oʻzgidrometdan soʻrash kerak. DustFlow toʻri ~6 km boʻlgani uchun bu yetarli.
STANSIYALAR = {
    723: ("Buxoro",     39.7747, 64.4286),
    722: ("Navoiy",     40.0844, 65.3792),
    721: ("Qarshi",     38.8606, 65.7891),
    716: ("Samarqand",  39.6542, 66.9597),
    719: ("Urganch",    41.5500, 60.6333),
    718: ("Nukus",      42.4531, 59.6103),
}
STANDART = [723, 722, 721]             # DustFlow hisoblash hududi ichidagilar
CSV_FAYL = "uzgidromet_kuzatuv.csv"
XATO_PAPKA = "uzgidromet_xato"
UTC_FARQ = timedelta(hours=5)          # sahifadagi vaqt — mahalliy (UTC+5)

MAYDONLAR = ["stansiya_id", "shahar", "manzil", "lat", "lon", "koord_manba",
             "vaqt_mahalliy", "vaqt_utc",
             "pm25", "pm10", "co", "so2", "no", "no2", "o3", "olingan"]

# sahifa matnidagi koʻrsatkichlar: (maydon, andoza)
KORSATKICH = [
    ("pm25", r"PM\s*2[.,]5\s*:\s*([\d.,]+)"),
    ("pm10", r"PM\s*10\s*:\s*([\d.,]+)"),
    ("co",   r"\(CO\)\s*:\s*([\d.,]+)"),
    ("so2",  r"Диоксид серы\s*:\s*([\d.,]+)"),
    ("no",   r"\(NO\)\s*:\s*([\d.,]+)"),
    ("no2",  r"\(NO2\)\s*:\s*([\d.,]+)"),
    ("o3",   r"\(O3\)\s*:\s*([\d.,]+)"),
]


def sahifa(stansiya_id, urinish=3):
    req = urllib.request.Request(URL.format(stansiya_id), headers={
        "User-Agent": "Mozilla/5.0 (DustFlow research; BuxDU)"})
    for i in range(urinish):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if i == urinish - 1:
                print(f"  [{stansiya_id}] tarmoq xatosi: {e}")
                return None
            time.sleep(5)


def matnga(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h))


def son(s):
    return float(s.replace(",", ".")) if s else None


def tahlil(stansiya_id, h):
    """Sahifadan qiymatlarni ajratadi. Stansiya yoki maʼlumot boʻlmasa None."""
    t = matnga(h)
    if "Концентрации загрязнителей" not in t:
        return None
    d = re.search(r"Дата\s*:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})", t)
    if not d:
        return None
    mahalliy = datetime.strptime(d.group(1), "%d.%m.%Y %H:%M")
    q = {"stansiya_id": stansiya_id,
         "vaqt_mahalliy": mahalliy.strftime("%Y-%m-%d %H:%M"),
         "vaqt_utc": (mahalliy - UTC_FARQ).strftime("%Y-%m-%d %H:%M"),
         "olingan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for nom, andoza in KORSATKICH:
        m = re.search(andoza, t)
        q[nom] = son(m.group(1)) if m else None
    # manzil: sarlavhadan keyin, «Обновлено» gacha
    m = re.search(r"Автоматическая станция мониторинга атмосферного воздуха\s*(?:\(Beta\))?\s*(.+?)\s*Обновлено", t)
    q["manzil"] = m.group(1).strip()[:150] if m else ""
    # koordinata: sahifadan EMAS (u yerda idora xaritasi), jadvaldan
    if stansiya_id in STANSIYALAR:
        q["shahar"], q["lat"], q["lon"] = STANSIYALAR[stansiya_id]
        q["koord_manba"] = "taxminiy: shahar markazi"
    else:
        q["shahar"], q["lat"], q["lon"], q["koord_manba"] = "", None, None, "nomaʼlum"
    return q


def mavjud_kalitlar(yol):
    if not os.path.exists(yol):
        return set()
    with open(yol, encoding="utf-8-sig") as f:
        return {(r["stansiya_id"], r["vaqt_mahalliy"]) for r in csv.DictReader(f)}


def yoz(qatorlar, yol=CSV_FAYL):
    bor = mavjud_kalitlar(yol)
    yangi = [q for q in qatorlar if (str(q["stansiya_id"]), q["vaqt_mahalliy"]) not in bor]
    if not yangi:
        return 0
    boshi = not os.path.exists(yol)
    with open(yol, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=MAYDONLAR)
        if boshi:
            w.writeheader()
        w.writerows(yangi)
    return len(yangi)


def bazaga(qatorlar, baza_yoli):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from dustflow.db import Baza
    except ImportError:
        print("  [eslatma] DustFlow topilmadi — bazaga yozilmadi")
        return
    b = Baza(baza_yoli)
    for q in qatorlar:
        b.kuzatuv_yozish(f"UzGM-{q['stansiya_id']}", q["lon"], q["lat"], q["vaqt_utc"],
                         C_pm10=q["pm10"], C_pm25=q["pm25"], izoh="monitoring.meteo.uz")


def yigish(idlar, baza=None):
    qatorlar = []
    for sid in idlar:
        h = sahifa(sid)
        if h is None:
            continue
        q = tahlil(sid, h)
        if q is None:
            os.makedirs(XATO_PAPKA, exist_ok=True)
            fayl = os.path.join(XATO_PAPKA, f"{sid}_{datetime.now():%Y%m%d_%H%M}.html")
            with open(fayl, "w", encoding="utf-8") as f:
                f.write(h)
            print(f"  [{sid}] qiymat topilmadi — sahifa saqlandi: {fayl}")
            continue
        qatorlar.append(q)
        print(f"  [{sid}] {q['shahar'] or q['manzil'][:30]:<10} {q['vaqt_mahalliy']}  "
              f"PM10={q['pm10']}  PM2.5={q['pm25']}")
        time.sleep(1.5)
    n = yoz(qatorlar)
    print(f"  CSV ga yangi yozuvlar: {n}  ->  {os.path.abspath(CSV_FAYL)}")
    if baza and qatorlar:
        bazaga(qatorlar, baza)


def qidir(dan, gacha):
    print(f"id {dan}…{gacha} oraligʻida avtomatik stansiyalar qidirilmoqda...")
    topildi = []
    for sid in range(dan, gacha + 1):
        h = sahifa(sid, urinish=1)
        q = tahlil(sid, h) if h else None
        if q and q["pm10"] is not None:
            topildi.append(q)
            print(f"  {sid:>5}  {q['manzil'][:70]}")
        time.sleep(1.0)
    print(f"Topildi: {len(topildi)} ta. Ularni --stansiya bilan bering.")


def main():
    p = argparse.ArgumentParser(description="Oʻzgidromet stansiyalaridan maʼlumot yigʻish")
    p.add_argument("--stansiya", nargs="+", type=int, default=STANDART)
    p.add_argument("--qidir", nargs=2, type=int, metavar=("DAN", "GACHA"))
    p.add_argument("--baza", default=None, help="DustFlow bazasiga ham yozish")
    a = p.parse_args()
    if a.qidir:
        qidir(*a.qidir)
    else:
        print(f"[{datetime.now():%Y-%m-%d %H:%M}] yigʻish")
        yigish(a.stansiya, a.baza)


if __name__ == "__main__":
    main()
