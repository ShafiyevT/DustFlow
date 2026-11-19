# -*- coding: utf-8 -*-
"""3-qadam. Sezgirlik tahlili (§ 4.2, (4.10)).

29.04.2025 06:00 dan 09:00 UTC gacha (3 soat) mahalliy emissiya bilan hisob; har bir parametr
bazaviy qiymatidan +-25 % ga o'zgartiriladi va 09:00 dagi yer sirtidagi o'rtacha konsentratsiya
taqqoslanadi.
"""
import os, sys, json, copy, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U

BOSH = dt.datetime(2025, 4, 29, 6)
kesh = U.kesh_oqi(BOSH, 3)
PARAM = [("U10", "Shamol tezligi U10"), ("m_cl", "Gil ulushi"), ("w", "Tuproq namligi w"),
         ("A_ef", "Eroziyalanuvchi yuza ulushi A_ef"), ("C_alpha", "Kalibrlash koeffitsiyenti C_alpha"),
         ("z0", "Aerodinamik g'adir-budurlik z0"), ("lam", "O'simlik qoplami"), ("eta", "Relyef balandligi")]


def hisob(p=None, f=1.0):
    kw = {"C_alpha": U.C_ALPHA * f} if p == "C_alpha" else {}
    m = None
    for v, k in kesh:
        k = copy.deepcopy(k)
        if p not in (None, "C_alpha"):
            setattr(k, p, getattr(k, p) * f)
        if m is None:
            m = U.model(k, **kw)
        else:
            m.majburlash_yangila(k)
        m.ishga_tushir(T=3600, dt=120.0, jim=True)
    return float((m.C[:, :, :, 0].sum(0) * 1e9).mean())


if __name__ == "__main__":
    C0 = hisob(); U.vaqt_belgisi(f"baza: {C0:.1f} mkg/m3")
    nat = dict(baza=C0, param=[])
    for p, nom in PARAM:
        cm, cp = hisob(p, 0.75), hisob(p, 1.25)
        dm, dp = (cm - C0) / C0 * 100, (cp - C0) / C0 * 100
        S = max(abs(dm), abs(dp)) / 25.0
        nat["param"].append(dict(p=p, nom=nom, minus=dm, plus=dp, S=S))
        U.vaqt_belgisi(f"{nom:36}  -25 %: {dm:+7.1f} %   +25 %: {dp:+7.1f} %   S = {S:.2f}")
    json.dump(nat, open(os.path.join(U.NATIJA, "sezgirlik.json"), "w"), indent=1)
