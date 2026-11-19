# -*- coding: utf-8 -*-
"""IV bob hisoblarining barchasini ketma-ket bajaradi (DustFlow 2.0).

    python ivbob_hisob/hammasi.py            # hammasi
    python ivbob_hisob/hammasi.py 4 6        # faqat 4- va 6-qadamlar

Natijalar: ivbob_natija/ (JSON, PNG) va ivbob_natija/hisobot.txt.
Taxminiy vaqt (2 yadroli kompyuter): 1-qadam 1 daq., 2-qadam 30 daq. (ikki variant parallel),
3-qadam 20 daq., 5-qadam 20 daq., qolganlari 1 daq.
8-qadam: stansiyalar bo'yicha batafsil tahlil (dissertatsiyaning 2-ilovasi).
"""
import os, sys, subprocess, time
B = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
QADAM = {1: [["s01_kesh.py"]],
         2: [["s02_boron.py", "mahalliy"], ["s02_boron.py", "chegara"]],
         3: [["s03_sezgirlik.py"], ["s05_qurilish.py", "emissiya"]],
         4: [["s04_baholash.py"]],
         5: [["s05_qurilish.py", "tarqalish"]],
         6: [["s06_rasmlar.py"]],
         7: [["s07_hisobot.py"]],
         8: [["s08_vakillik.py"]]}
tanlov = [int(a) for a in sys.argv[1:]] or sorted(QADAM)
os.makedirs(os.path.join(os.path.dirname(B), "ivbob_natija"), exist_ok=True)
for q in tanlov:
    t0 = time.time(); print(f"\n===== {q}-qadam: {' | '.join(' '.join(x) for x in QADAM[q])} =====", flush=True)
    jar = [subprocess.Popen([PY, os.path.join(B, x[0]), *x[1:]]) for x in QADAM[q]]   # parallel
    kod = [p.wait() for p in jar]
    if any(kod):
        sys.exit(f"[xato] {q}-qadam muvaffaqiyatsiz tugadi (kodlar {kod})")
    print(f"===== {q}-qadam tugadi: {time.time() - t0:.0f} s =====", flush=True)
print("\nBarcha hisoblar tugadi. Natijalar: ivbob_natija/  (hisobot.txt, rasm_4_*.png, *.json)")
