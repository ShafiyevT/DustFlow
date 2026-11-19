# -*- coding: utf-8 -*-
"""Modelning adekvatligini baholash moduli.

Hisoblash natijalarini kuzatuv ma'lumotlari bilan solishtirish uchun
atmosfera modellarini baholashda qabul qilingan statistik mezonlar
to'plami amalga oshirilgan.
"""
import numpy as np


def _tayyorla(kuz, hisob):
    o = np.asarray(kuz, dtype=float).ravel()
    m = np.asarray(hisob, dtype=float).ravel()
    yaroqli = np.isfinite(o) & np.isfinite(m)
    return o[yaroqli], m[yaroqli]


# ---------------------------------------------------------------
# Asosiy mezonlar
# ---------------------------------------------------------------
def siljish(kuz, hisob):
    """O'rtacha siljish MB (mean bias). Ideal qiymat: 0."""
    o, m = _tayyorla(kuz, hisob)
    return float(np.mean(m - o))


def nisbiy_siljish(kuz, hisob):
    """Normallashtirilgan o'rtacha siljish NMB, %. Ideal: 0."""
    o, m = _tayyorla(kuz, hisob)
    return float(np.sum(m - o) / np.sum(o) * 100.0)


def rmse(kuz, hisob):
    """O'rtacha kvadratik xatolik. Ideal: 0."""
    o, m = _tayyorla(kuz, hisob)
    return float(np.sqrt(np.mean((m - o) ** 2)))


def nmse(kuz, hisob):
    """Normallashtirilgan o'rtacha kvadratik xatolik. Ideal: 0."""
    o, m = _tayyorla(kuz, hisob)
    return float(np.mean((m - o) ** 2) / (np.mean(o) * np.mean(m)))


def korrelyatsiya(kuz, hisob):
    """Pirson korrelyatsiya koeffitsiyenti. Ideal: 1."""
    o, m = _tayyorla(kuz, hisob)
    if len(o) < 2:
        return float("nan")
    return float(np.corrcoef(o, m)[0, 1])


def fac2(kuz, hisob):
    """Ikki barobar oralig'iga tushgan nuqtalar ulushi. Ideal: 1."""
    o, m = _tayyorla(kuz, hisob)
    mask = o > 0
    if not np.any(mask):
        return float("nan")
    nisbat = m[mask] / o[mask]
    return float(np.mean((nisbat >= 0.5) & (nisbat <= 2.0)))


def fb(kuz, hisob):
    """Fraksion siljish FB. Ideal: 0, qabul qilinadigan oraliq |FB| < 0.3."""
    o, m = _tayyorla(kuz, hisob)
    return float(2.0 * (np.mean(o) - np.mean(m)) / (np.mean(o) + np.mean(m)))


def willmott(kuz, hisob):
    """Willmott moslik indeksi d. Ideal: 1."""
    o, m = _tayyorla(kuz, hisob)
    o_ort = np.mean(o)
    payda = np.sum((m - o) ** 2)
    maxraj = np.sum((np.abs(m - o_ort) + np.abs(o - o_ort)) ** 2)
    return float(1.0 - payda / maxraj) if maxraj > 0 else float("nan")


# ---------------------------------------------------------------
# Jamlanma baho
# ---------------------------------------------------------------
MEZONLAR = [
    ("MB",   "o'rtacha siljish, mkg/m³",            siljish,        "0 ga yaqin"),
    ("NMB",  "normallashtirilgan siljish, %",       nisbiy_siljish, "|NMB| < 30"),
    ("RMSE", "o'rtacha kvadratik xatolik, mkg/m³",  rmse,           "kichik"),
    ("NMSE", "normallashtirilgan o'rt. kv. xatolik", nmse,          "NMSE < 1,5"),
    ("r",    "korrelyatsiya koeffitsiyenti",        korrelyatsiya,  "r > 0,5"),
    ("FAC2", "ikki barobar oralig'idagi ulush",     fac2,           "FAC2 > 0,5"),
    ("FB",   "fraksion siljish",                    fb,             "|FB| < 0,3"),
    ("d",    "Willmott moslik indeksi",             willmott,       "d > 0,7"),
]


def baho(kuz, hisob, jim=True):
    """Barcha mezonlarni hisoblaydi va lug'at ko'rinishida qaytaradi."""
    n = {}
    for belgi, tavsif, f, mezon in MEZONLAR:
        n[belgi] = f(kuz, hisob)
    if not jim:
        o, m = _tayyorla(kuz, hisob)
        print(f"{'mezon':<7}{'tavsif':<38}{'qiymat':>12}{'talab':>16}")
        print("-" * 75)
        for belgi, tavsif, f, mezon in MEZONLAR:
            print(f"{belgi:<7}{tavsif:<38}{n[belgi]:>12.3f}{mezon:>16}")
        print("-" * 75)
        print(f"solishtirilgan juftliklar soni: {len(o)}")
    return n


def qoniqarlimi(n):
    """Model adekvat deb hisoblanadimi (Chang va Hanna mezonlari bo'yicha)."""
    return (abs(n["FB"]) < 0.3 and n["NMSE"] < 1.5 and n["FAC2"] > 0.5)


# ---------------------------------------------------------------
# Kuzatuv ma'lumotlari bilan solishtirish
# ---------------------------------------------------------------
def nuqtada_olish(model, tor, x_m, y_m, fraksiya=None):
    """Berilgan koordinatadagi yuza konsentratsiyasi, mkg/m³."""
    i = int(np.argmin(np.abs(tor.x - x_m)))
    j = int(np.argmin(np.abs(tor.y - y_m)))
    if fraksiya is None:
        return float(model.yuza_konsentratsiya()[i, j] * 1e9)
    return float(model.C[fraksiya, i, j, 0] * 1e9)


def stansiyalar_boyicha(model, tor, stansiyalar):
    """Stansiyalar ro'yxati bo'yicha hisoblangan qiymatlarni qaytaradi.

    stansiyalar — [{'nom':..., 'x':..., 'y':..., 'C_pm10':...}, ...]
    """
    kuz, his, nomlar = [], [], []
    for s in stansiyalar:
        if s.get("C_pm10") is None:
            continue
        kuz.append(s["C_pm10"])
        his.append(nuqtada_olish(model, tor, s["x"], s["y"]))
        nomlar.append(s["nom"])
    return np.array(kuz), np.array(his), nomlar
