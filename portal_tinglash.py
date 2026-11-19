# -*- coding: utf-8 -*-
"""air-uzbekistan.uz portali qaysi API dan maʼlumot olayotganini aniqlash.

Skript Chrome'ni ochadi va brauzer serverdan olayotgan barcha JSON/matn
javoblarini (manzili va tanasi bilan) papkaga yozib boradi. Siz esa brauzerda
odatdagidek shaharni, sanani va rejimni tanlaysiz — tugmalarni skript bosmaydi,
shuning uchun sahifa tuzilishini oldindan bilish shart emas.

Oʻrnatish (bir marta):
    py -m pip install selenium

Ishga tushirish:
    py portal_tinglash.py

Tugatish: konsolda Ctrl+C yoki brauzer oynasini yopish.
Natija: portal_javoblar\\ papkasi (royxat.csv + javob fayllari).
"""
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

for _oqim in (sys.stdout, sys.stderr):
    try:
        _oqim.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

URL = "https://air-uzbekistan.uz/#trend_weather"
PAPKA = "portal_javoblar"
KERAKLI_TUR = ("json", "text/plain", "text/csv", "javascript")   # MIME boʻyicha
KERAKSIZ_KENG = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".ico",
                 ".woff", ".woff2", ".ttf", ".css", ".apk", ".map")


def kerakmi(url, mime):
    yol = urlparse(url).path.lower()
    if yol.endswith(KERAKSIZ_KENG):
        return False
    if yol.endswith(".js") and "/api/" not in yol:
        return False                                   # kutubxona fayllari
    return any(t in (mime or "").lower() for t in KERAKLI_TUR) or "/api/" in yol


def fayl_nomi(n, url):
    p = urlparse(url)
    asos = re.sub(r"[^A-Za-z0-9._-]+", "_", (p.path + ("_" + p.query if p.query else "")))
    return f"{n:04d}{asos[:120]}.txt"


def qayta_ishla(yozuvlar, holat, tana_ol, royxat_yoz):
    """Performance jurnalidagi yozuvlarni qayta ishlaydi.

    holat     — {"kutilmoqda": {requestId: (url, mime, status)}, "n": int}
    tana_ol   — requestId -> matn (yoki None)
    royxat_yoz — (qator lugʻati) -> None
    """
    for yoz in yozuvlar:
        try:
            m = json.loads(yoz["message"])["message"]
        except Exception:
            continue
        usul, par = m.get("method"), m.get("params", {})
        if usul == "Network.responseReceived":
            r = par.get("response", {})
            if kerakmi(r.get("url", ""), r.get("mimeType", "")):
                holat["kutilmoqda"][par["requestId"]] = (r.get("url"), r.get("mimeType"),
                                                          r.get("status"))
        elif usul == "Network.loadingFinished":
            rid = par.get("requestId")
            if rid not in holat["kutilmoqda"]:
                continue
            url, mime, status = holat["kutilmoqda"].pop(rid)
            tana = tana_ol(rid)
            if tana is None:
                continue
            holat["n"] += 1
            nom = fayl_nomi(holat["n"], url)
            with open(os.path.join(PAPKA, nom), "w", encoding="utf-8") as f:
                f.write(tana)
            royxat_yoz(dict(n=holat["n"], vaqt=datetime.now().strftime("%H:%M:%S"),
                            status=status, mime=mime, hajm=len(tana), url=url, fayl=nom))
            print(f"  [{holat['n']:>3}] {status} {len(tana):>8} bayt  {url[:110]}")


def main():
    try:
        from selenium import webdriver
        from selenium.common.exceptions import WebDriverException
    except ImportError:
        sys.exit("Selenium oʻrnatilmagan:  py -m pip install selenium")

    os.makedirs(PAPKA, exist_ok=True)
    rf = open(os.path.join(PAPKA, "royxat.csv"), "w", newline="", encoding="utf-8-sig")
    rw = csv.DictWriter(rf, fieldnames=["n", "vaqt", "status", "mime", "hajm", "url", "fayl"])
    rw.writeheader()

    opts = webdriver.ChromeOptions()
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    opts.add_argument("--start-maximized")
    d = webdriver.Chrome(options=opts)
    d.execute_cdp_cmd("Network.enable", {})

    def tana_ol(rid):
        try:
            r = d.execute_cdp_cmd("Network.getResponseBody", {"requestId": rid})
            if r.get("base64Encoded"):
                return None
            return r.get("body", "")
        except Exception:
            return None

    def yoz(q):
        rw.writerow(q); rf.flush()

    d.get(URL)
    print("=" * 78)
    print(" Brauzer ochildi. Endi brauzerda quyidagilarni bajaring:")
    print("   1) shahar sifatida BUXORO ni tanlang;")
    print("   2) «24 часа» rejimida sanani 30.04.2025 ga qoʻying, keyin 29.04.2025;")
    print("   3) «7 дней» rejimini bir marta bosing;")
    print("   4) iloji boʻlsa, NAVOIY va QARSHI uchun ham bitta sana tanlang.")
    print(" Tugatgach, shu oynada Ctrl+C bosing (yoki brauzerni yoping).")
    print("=" * 78)

    holat = {"kutilmoqda": {}, "n": 0}
    try:
        while True:
            try:
                yozuvlar = d.get_log("performance")
            except WebDriverException:
                print("\n  brauzer yopildi")
                break
            qayta_ishla(yozuvlar, holat, tana_ol, yoz)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n  toʻxtatildi")
    finally:
        rf.close()
        try:
            d.quit()
        except Exception:
            pass
    print(f"\n  Saqlangan javoblar: {holat['n']} ta  ->  {os.path.abspath(PAPKA)}")
    print("  Shu papkani zip qilib yuboring.")


if __name__ == "__main__":
    main()
