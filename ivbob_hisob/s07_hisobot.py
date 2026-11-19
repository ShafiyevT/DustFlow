# -*- coding: utf-8 -*-
"""7-qadam. IV bob jadvallari uchun barcha raqamlar — ivbob_natija/hisobot.txt va hisobot.json."""
import os, sys, json, pickle, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
from dustflow.emission import emissiya_maydoni

N_ = U.NATIJA
J = lambda f: json.load(open(os.path.join(N_, f)))
H = {}
satr = []
p = lambda s="": satr.append(s)

# --- 4.6-jadval: bo'ronning bosqichlari (emissiya) ---
t = U.tor(); S = t.yuza_ogirligi()
def emis(v):
    _, k = pickle.load(open(U.kesh_fayl(v), "rb"))
    F, inf = emissiya_maydoni(k.U10, k.z0, k.w, k.m_cl, k.lam, k.A_ef, None, U.CH, C_alpha=U.C_ALPHA)
    Ft = inf["F_tot"]; chol = k.A_ef > 0.2
    return dict(vaqt=f"{v:%d.%m.%Y %H:%M}", U10=float(k.U10.max()), w_chol=float(np.median(k.w[chol])),
                eroziya=float(np.mean(Ft[1:-1, 1:-1] > 0) * 100), E=float(np.sum(Ft * S) * 3600 / 1000))
H["bosqichlar"] = [emis(v) for v in (dt.datetime(2025, 4, 23, 9), dt.datetime(2025, 4, 28, 21),
                                     dt.datetime(2025, 4, 29, 9), dt.datetime(2025, 4, 29, 15),
                                     dt.datetime(2026, 2, 15, 9))]
p("4.6-jadval. Bo'ronning bosqichlari")
for r in H["bosqichlar"]:
    p(f"  {r['vaqt']}  U10 maks {r['U10']:5.1f} m/s  cho'l namligi {r['w_chol']:5.1f} %  "
      f"eroziya {r['eroziya']:5.1f} %  emissiya {r['E']:9.0f} t/soat")

# --- bo'ron: 48 soatlik balans (mahalliy) ---
B = J("boron_mahalliy.json"); b = B["b48"]; q = B["qator"]
sh = sum(x["E_soat"] for x in q)
H["boron"] = dict(em_kt=b["Q_em"] / 1e6, pm10=(b["frak"][0] + b["frak"][1]) / b["Q_em"] * 100,
                  cho=b["Q_cho"] / b["Q_em"] * 100, chiq=b["Q_chiq"] / b["Q_em"] * 100,
                  qolgan=b["Q"] / b["Q_em"] * 100, balans=b["nisbiy"], vaqt_min=B["vaqt"] / 60 * 48 / U.SOAT,
                  it_ort=B["it_ort"], it_maks=B["it_maks"], eroziya_oraliq=(min(x["eroziya"] for x in q[18:42]),
                                                                           max(x["eroziya"] for x in q[18:42])))
r = H["boron"]
p(); p("Bo'ron, 28.04 00:00 – 30.04 00:00 UTC, faqat mahalliy emissiya")
p(f"  ko'tarilgan chang {r['em_kt']:.0f} ming t, PM10 ulushi {r['pm10']:.0f} %, cho'kkan {r['cho']:.0f} %, "
  f"chiqib ketgan {r['chiq']:.0f} %, sohada qolgan {r['qolgan']:.0f} %")
p(f"  massa balansi nomuvofiqligi {r['balans']:.2f} %, hisoblash vaqti {r['vaqt_min']:.1f} daq (48 soat), "
  f"iteratsiyalar {r['it_ort']:.2f} / {r['it_maks']}")
p(f"  eroziya maydoni 28.04 18:00 – 29.04 18:00: {r['eroziya_oraliq'][0]:.0f}–{r['eroziya_oraliq'][1]:.0f} %")

# --- baholash ---
E = J("baholash.json"); H["baholash"] = E
p(); p(f"4.9-jadval. Stansiyalar bilan taqqoslash ({E['n']} juftlik)")
for k, nm in (("chegara", "DustFlow, chegara bilan"), ("mahalliy", "DustFlow, mahalliy"), ("CAMS", "CAMS")):
    n = E["pool"][k]
    p(f"  {nm:24}: R {n['r']:.2f}  NMB {n['NMB']:+.0f} %  FAC2 {n['FAC2']:.2f}  |FB| {abs(n['FB']):.2f}  NMSE {n['NMSE']:.2f}")
for s, r_ in E["stansiya"].items():
    kk = E["kun"][s]
    p(f"  {r_['nom']:7}: R {r_['chegara']['r']:.2f} / {r_['mahalliy']['r']:.2f} / {r_['CAMS']['r']:.2f};  "
      f"bo'ron kuni ortiqcha PM10: kuzatuv {kk['obs']:.0f}, chegara {kk['chegara']:.0f}, mahalliy {kk['mahalliy']:.0f}, CAMS {kk['CAMS']:.0f}")
n = E["nisbat"]
p(f"  PM2.5/PM10 Buxoro: kuzatuv {n['obs_min']:.2f}–{n['obs_max']:.2f} (mediana {n['obs_med']:.2f}), "
  f"chegara {n['chegara']:.2f}, mahalliy {n['mahalliy']:.2f}, CAMS {n['CAMS']:.2f}")
f_ = E["fazo"]
p(f"  CAMS bilan fazoviy (29.04 09:00): mahalliy NMB {f_['mahalliy']['NMB']:+.0f} %, FAC2 {f_['mahalliy']['FAC2']:.2f}; "
  f"chegara NMB {f_['chegara']['NMB']:+.0f} %, FAC2 {f_['chegara']['FAC2']:.2f}; mahalliy ulush {E['mahalliy_ulush']*100:.0f} %")
p(); p("4.7-jadval. C_alpha (mahalliy variant: butun ortiqcha chang mahalliy emissiyaga tegishli deb qaralganda)")
for r_ in E["kalibrlash_mahalliy"]:
    p(f"  C_alpha {r_['C']:.4f}: stansiyalar M/O {r_['Rs']:.2f}, FB {r_['FBs']:+.2f}, FAC2 {r_['FAC2s']:.2f} | "
      f"CAMS M/O {r_['Rc']:.2f}, FB {r_['FBc']:+.2f}, FAC2 {r_['FAC2c']:.2f} | max|FB| {r_['maxFB']:.2f}")
p(f"  optimum: C_alpha = {E['optimum_mahalliy']['C']:.4f}, max|FB| = {E['optimum_mahalliy']['maxFB']:.2f}")
p(); p("  (taqqoslash uchun) chegara varianti, (4.9):")
for r_ in E["kalibrlash"]:
    p(f"  C_alpha {r_['C']:.4f}: stansiyalar M/O {r_['Rs']:.2f}, FB {r_['FBs']:+.2f} | CAMS M/O {r_['Rc']:.2f}, "
      f"FB {r_['FBc']:+.2f} | max|FB| {r_['maxFB']:.2f}")
p(f"  optimum: C_alpha = {E['optimum']['C']:.4f}, max|FB| = {E['optimum']['maxFB']:.2f}")

# --- sezgirlik ---
if os.path.exists(os.path.join(N_, "sezgirlik.json")):
    Z = J("sezgirlik.json"); H["sezgirlik"] = Z
    p(); p(f"4.8-jadval. Sezgirlik (baza {Z['baza']:.1f} mkg/m3)")
    for r_ in sorted(Z["param"], key=lambda x: -x["S"]):
        p(f"  {r_['nom']:36}: -25 % {r_['minus']:+6.1f} %   +25 % {r_['plus']:+6.1f} %   S = {r_['S']:.2f}")

# --- qurilish ---
Q = J("qurilish_emissiya.json"); H["qurilish_emissiya"] = Q
p(); p("4.11-jadval. Qurilish maydoni: bo'ron davomida emissiya, t")
for g, r_ in Q["jadval"].items():
    p(f"  gil {float(g)*100:4.0f} %: quruq {r_['boron']['quruq']:6.1f}  ERA5 {r_['boron']['era5']:6.1f}  "
      f"namlangan {r_['boron']['namlangan']:5.1f}")
m = Q["markaziy"]
p(f"  markaziy: {m['boron']:.1f} t, {m['soat']} soat, maks {m['maks']:.2f} t/soat ({m['maks_vaqt']}), shamol x0,7: {m['boron_07']:.1f} t")
if os.path.exists(os.path.join(N_, "qurilish_tarqalish.json")):
    T_ = J("qurilish_tarqalish.json"); H["qurilish_tarqalish"] = T_; bb = T_["balans"]
    p(); p("4.12-jadval. Qurilish maydoni: tarqalish")
    p(f"  ko'tarilgan {bb['Q_em']/1e3:.1f} t, cho'kkan {bb['Q_cho']/1e3:.1f} t ({bb['Q_cho']/bb['Q_em']*100:.0f} %), "
      f"chiqib ketgan {bb['Q_chiq']/1e3:.1f} t ({bb['Q_chiq']/bb['Q_em']*100:.0f} %), balans {bb['nisbiy']:.2f} %")
    p(f"  o'rtacha PM10 maks {T_['ort_maks']:.0f} mkg/m3; o'rtacha >75: {T_['zona_ort75'][0]:.2f} km2, {T_['zona_ort75'][1]:.1f} km gacha")
    p(f"  soatlik >75: {T_['zona_soat75'][0]:.2f} km2, {T_['zona_soat75'][1]:.1f} km; soatlik >25: {T_['zona_soat25'][0]:.1f} km2, "
      f"{T_['zona_soat25'][1]:.1f} km")
    p(f"  cho'kma maks {T_['qal_maks']:.2f} mkm; >0,1 mkm: {T_['zona_qal01'][0]:.1f} km2, {T_['zona_qal01'][1]:.1f} km gacha; "
      f"stansiya nuqtasida {T_['stansiya_ort']:.1f} mkg/m3")
open(os.path.join(N_, "hisobot.txt"), "w", encoding="utf-8").write("\n".join(satr) + "\n")
json.dump(H, open(os.path.join(N_, "hisobot.json"), "w"), indent=1, default=float)
print("\n".join(satr))
