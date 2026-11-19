# -*- coding: utf-8 -*-
"""9-qadam. Besh transport fraksiyasi va bitta effektiv moda: 48 soatlik bo'ron hisobi.

    python ivbob_hisob/s09_bir_moda.py besh      # standart 5 fraksiya
    python ivbob_hisob/s09_bir_moda.py bir       # bitta moda, 0,2-100 mkm (d = 4,5 mkm)
    python ivbob_hisob/s09_bir_moda.py taqqosla  # ikkala natijani solishtirish

Ikkala hisobda emissiya sxemasi va ko'tarilgan massa bir xil; farq faqat chang
fraksiyalarga bo'linadimi yoki yo'qligida. Faqat hudud ichidagi emissiya (mahalliy variant).
Natija: ivbob_natija/bir_moda_{variant}.json, .pkl va bir_moda_taqqoslash.json/.txt
"""
import os, sys, json, pickle, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U

SOAT = 48
CHEGARALAR = {"besh": None, "bir": [0.2e-6, 100e-6]}


def ishga(variant):
    kesh = U.kesh_oqi(U.BOSH, SOAT)
    m = U.model(kesh[0][1], chegaralar=CHEGARALAR[variant]); t = m.tor
    IJ = {s: U.ij(t, la, lo) for s, (_, la, lo) in U.STANSIYA.items()}
    ort = np.zeros((m.Nf,) + m.C.shape[1:3]); qator = []; choqqi = None; t0 = time.time()
    for v, k in kesh:
        m.majburlash_yangila(k)
        m.ishga_tushir(T=3600, dt=120.0, jim=True)
        y = m.C[:, :, :, 0] * 1e9                       # mkg/m3, yer sirti
        ort += y / SOAT
        b = m.massa_balansi()
        qator.append(dict(vaqt=v.strftime("%Y-%m-%d %H:%M"), yuza_ort=float(y.sum(0)[1:-1, 1:-1].mean()),
                          Q=float(b["Q"]), Q_em=float(b["Q_em"]), nisbiy=float(b["nisbiy"]),
                          **{f"{s}": float(y.sum(0)[i, j]) for s, (i, j) in IJ.items()}))
        if v == U.CHOQQI:
            choqqi = y.sum(0).copy()
        U.vaqt_belgisi(f"{variant} {v:%d.%m %H:%M}  massa {b['Q']/1e9:7.1f} kt  balans {b['nisbiy']:.2f} %")
    b = m.massa_balansi()
    natija = dict(variant=variant, Nf=m.Nf, d=m.d_ort.tolist(), rho=m.rho_p.tolist(), w_s=m.v_t.tolist(),
                  balans={k_: float(x) for k_, x in b.items()},
                  frak_em=[float(m.balans[i].Q_em) for i in range(m.Nf)],
                  frak_cho=[float(m.balans[i].Q_cho) for i in range(m.Nf)],
                  qator=qator, ij=IJ, vaqt=time.time() - t0)
    json.dump(natija, open(os.path.join(U.NATIJA, f"bir_moda_{variant}.json"), "w"), indent=1)
    pickle.dump(dict(ort=ort, choqqi=choqqi), open(os.path.join(U.NATIJA, f"bir_moda_{variant}.pkl"), "wb"))
    U.vaqt_belgisi(f"{variant} tugadi: balans {b['nisbiy']:.2f} %, {time.time() - t0:.0f} s")


def taqqosla():
    R = {v: json.load(open(os.path.join(U.NATIJA, f"bir_moda_{v}.json"))) for v in CHEGARALAR}
    P = {v: pickle.load(open(os.path.join(U.NATIJA, f"bir_moda_{v}.pkl"), "rb")) for v in CHEGARALAR}
    kt = lambda x: x / 1e6                      # kg -> kt
    out = {}
    for v in CHEGARALAR:
        b = R[v]["balans"]; ort = P[v]["ort"].sum(0)[1:-1, 1:-1]
        out[v] = dict(chiqarilgan=kt(b["Q_em"]), chokkan=kt(b["Q_cho"]), chegaradan=kt(b["Q_chiq"]),
                      havoda=kt(b["Q"]), yutilgan=kt(b["Q_yut"]), kesilgan=kt(b["kesilgan"]),
                      yuza_48_ort=float(ort.mean()), yuza_choqqi_ort=float(P[v]["choqqi"][1:-1, 1:-1].mean()),
                      balans_nisbiy=b["nisbiy"], w_s=R[v]["w_s"], d=R[v]["d"])
    a, c = P["besh"]["ort"].sum(0)[1:-1, 1:-1], P["bir"]["ort"].sum(0)[1:-1, 1:-1]
    mask = a > 1.0                                          # 1 mkg/m3 dan katta yacheykalar
    rel = (c[mask] - a[mask]) / a[mask] * 100
    i, j = R["besh"]["ij"]["bukhara"]
    bux = (P["bir"]["ort"].sum(0)[i, j] / P["besh"]["ort"].sum(0)[i, j] - 1) * 100
    hissa = (P["besh"]["ort"][:, 1:-1, 1:-1].sum((1, 2)) / P["besh"]["ort"][:, 1:-1, 1:-1].sum() * 100).tolist()
    out["farq"] = dict(median=float(np.median(rel)), p90=float(np.percentile(rel, 90)),
                       buxoro=float(bux), hissa_besh=hissa,
                       chokish_nisbati=out["besh"]["chokkan"] / out["bir"]["chokkan"])
    json.dump(out, open(os.path.join(U.NATIJA, "bir_moda_taqqoslash.json"), "w"), indent=1)
    q = []
    for k_ in ("chiqarilgan", "chokkan", "chegaradan", "havoda", "yutilgan", "kesilgan", "yuza_48_ort", "yuza_choqqi_ort", "balans_nisbiy"):
        q.append(f"{k_:16s} besh {out['besh'][k_]:10.2f}   bir {out['bir'][k_]:10.2f}   nisbat {out['besh'][k_]/max(out['bir'][k_],1e-30):6.2f}")
    q.append(f"nisbiy farq (bir - besh)/besh: median {out['farq']['median']:+.1f} %, 90-persentil {out['farq']['p90']:+.1f} %, Buxoro {bux:+.1f} %")
    q.append("fraksiyalar hissasi (yer sirti, 48 soat): " + ", ".join(f"{h:.0f} %" for h in hissa))
    q.append(f"bitta moda: d = {out['bir']['d'][0]*1e6:.2f} mkm, w_s = {out['bir']['w_s'][0]*100:.3f} sm/s")
    open(os.path.join(U.NATIJA, "bir_moda_taqqoslash.txt"), "w", encoding="utf-8").write("\n".join(q) + "\n")
    print("\n".join(q))


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "besh"
    taqqosla() if a == "taqqosla" else ishga(a)
