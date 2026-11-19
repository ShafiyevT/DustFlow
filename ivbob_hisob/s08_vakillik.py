# -*- coding: utf-8 -*-
"""Stansiyalar bilan taqqoslashning batafsil tahlili (dissertatsiyaning 2-ilovasi).

    python ivbob_hisob/s08_vakillik.py

Talab qiladi: s02_boron.py natijalari (boron_{V}.json va boron_{V}_qoshni.pkl).
Natija: ivbob_natija/vakillik.json va ivbob_natija/vakillik.txt

1) har bir stansiya bo'yicha alohida statistika (DustFlow ikki varianti va CAMS) - 2.1-jadval;
2) vakillik va vaqt siljishi tahlili - 2.2-jadval:
   stansiya atrofidagi 3x3 va 5x5 yacheykalar, -6...+6 soat siljish,
   +-3 soat oyna, 12 soatlik sirpanuvchi o'rtacha.
"Eng yaqin qiymat" usullarida har bir kuzatuv uchun oyna ichidan kuzatuvga eng yaqin
model qiymati tanlanadi, shuning uchun ular moslikning yuqori chegarasini beradi.
"""
import os, sys, json, pickle, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
from dustflow.validatsiya import baho

VARIANT = ("mahalliy", "chegara")
VAQT = pd.date_range("2025-04-28 00:00", "2025-04-30 21:00", freq="3h")   # 3 soatlik taqqoslash


def kuzatuvlar():
    d = pd.read_csv(U.STANSIYA_CSV); d["t"] = pd.to_datetime(d.vaqt_utc)
    obs = {}
    for s in U.STANSIYA:
        ob = d[d.shahar == s].set_index("t").pm10
        ob = ob[~ob.index.duplicated()]
        obs[s] = ob - ob.loc[U.FON[0]:U.FON[1]].median()            # fondan ortiqcha PM10
    return obs


def model_qatorlari():
    return {V: pd.DataFrame(json.load(open(os.path.join(U.NATIJA, f"boron_{V}.json")))["qator"])
              .assign(t=lambda x: pd.to_datetime(x.vaqt)).set_index("t") for V in VARIANT}


def cams_qatorlari():
    from netCDF4 import Dataset, num2date
    ds = Dataset(U.CAMS)
    lon = np.array(ds["longitude"][:]); lat = np.array(ds["latitude"][:])
    T = pd.DatetimeIndex([dt.datetime(x.year, x.month, x.day, x.hour)
                          for x in num2date(ds["valid_time"][:], ds["valid_time"].units)])
    p10 = np.array(ds["pm10"][:]) * 1e9
    out = {}
    for s, (nm, la, lo) in U.STANSIYA.items():
        i = int(np.argmin(abs(lon - lo))); j = int(np.argmin(abs(lat - la)))
        c = pd.Series(p10[:, j, i], index=T)
        out[s] = c - c.loc[U.FON[0]:U.FON[1]].median()
    return out


def juftla(o, m):
    o = o.reindex(VAQT); m = m.reindex(VAQT); ok = o.notna() & m.notna()
    return o[ok].values, m[ok].values


def umumiy_baho(obs, seriyalar):
    O, M = [], []
    for s in U.STANSIYA:
        a, b = juftla(obs[s], seriyalar[s]); O.append(a); M.append(b)
    return baho(np.concatenate(O), np.concatenate(M))


def oyna_eng_yaqin(o, m, w):
    """Har bir kuzatuv uchun +-w soat ichidagi eng yaqin model qiymati."""
    mv = []
    for t, x in o.reindex(VAQT).items():
        c = m.reindex(pd.date_range(t - pd.Timedelta(hours=w), t + pd.Timedelta(hours=w), freq="h")).dropna()
        mv.append(np.nan if (len(c) == 0 or np.isnan(x)) else c.values[np.argmin(abs(c.values - x))])
    return pd.Series(mv, index=VAQT)


def silliqla(x, n):
    x = x.reindex(pd.date_range(x.index.min(), x.index.max(), freq="h"))
    return x.rolling(n, center=True, min_periods=n // 2 + 1).mean()


def main():
    obs = kuzatuvlar(); Q = model_qatorlari(); cams = cams_qatorlari()
    nom = {s: v[0] for s, v in U.STANSIYA.items()}
    natija = {"stansiyalar": {}, "vakillik": {}}
    qator = ["1. Stansiyalar bo'yicha alohida statistika (fondan ortiqcha PM10, 3 soatlik)", ""]

    for s in U.STANSIYA:
        for k, m in (("mahalliy", Q["mahalliy"][f"{s}_pm10"]), ("chegara", Q["chegara"][f"{s}_pm10"]), ("CAMS", cams[s])):
            a, b = juftla(obs[s], m); r = baho(a, b)
            r.update(n=int(len(a)), O=float(a.mean()), M=float(b.mean()))
            natija["stansiyalar"][f"{nom[s]}|{k}"] = r
            qator.append(f"{nom[s]:8s} {k:9s} n={r['n']:2d} O={r['O']:6.0f} M={r['M']:6.0f} R={r['r']:+.2f} "
                         f"FAC2={r['FAC2']:.2f} FB={r['FB']:+.2f} NMSE={r['NMSE']:6.2f} NMB={r['NMB']:+5.0f} %")

    qator += ["", "2. Vakillik va vaqt siljishi tahlili (3 stansiya)", ""]
    for V in VARIANT:
        q = pickle.load(open(os.path.join(U.NATIJA, f"boron_{V}_qoshni.pkl"), "rb"))
        T = pd.to_datetime(q["vaqt"])
        markaz = {s: Q[V][f"{s}_pm10"] for s in U.STANSIYA}
        usullar = {}

        def maydon(s, r, f):
            return pd.Series([f(x[s]["pm10"][2 - r:3 + r, 2 - r:3 + r]) for x in q["maydon"]], index=T)

        usullar["asosiy (stansiya yacheykasi)"] = markaz
        usullar["3x3 o'rtacha"] = {s: maydon(s, 1, np.mean) for s in U.STANSIYA}
        for r, nm in ((1, "3x3 eng yaqin"), (2, "5x5 eng yaqin")):
            ser = {}
            for s in U.STANSIYA:
                o = obs[s]; vals = []
                for k, x in enumerate(q["maydon"]):
                    t = T[k]
                    if t in o.index and np.isfinite(o[t]):
                        c = x[s]["pm10"][2 - r:3 + r, 2 - r:3 + r].ravel(); vals.append(c[np.argmin(abs(c - o[t]))])
                    else:
                        vals.append(np.nan)
                ser[s] = pd.Series(vals, index=T)
            usullar[nm] = ser
        siljish = {L: umumiy_baho(obs, {s: markaz[s].shift(L) for s in U.STANSIYA}) for L in range(-6, 7)}
        eng = max(siljish, key=lambda L: siljish[L]["r"])
        usullar["+-3 soat oyna, eng yaqin"] = {s: oyna_eng_yaqin(obs[s], markaz[s], 3) for s in U.STANSIYA}

        res = {nm: umumiy_baho(obs, ser) for nm, ser in usullar.items()}
        res[f"vaqt siljishi, eng yaxshi ({eng:+d} soat)"] = siljish[eng]
        sobs = {s: silliqla(obs[s], 12) for s in U.STANSIYA}
        res["12 soatlik sirpanuvchi o'rtacha"] = umumiy_baho(sobs, {s: silliqla(markaz[s], 12) for s in U.STANSIYA})
        natija["vakillik"][V] = dict(usullar=res, siljish={str(k): v for k, v in siljish.items()})
        qator.append(f"-- {V}")
        for nm, r in res.items():
            qator.append(f"   {nm:34s} R={r['r']:.2f} FAC2={r['FAC2']:.2f} FB={r['FB']:+.2f}")

    json.dump(natija, open(os.path.join(U.NATIJA, "vakillik.json"), "w"), indent=1, default=float)
    open(os.path.join(U.NATIJA, "vakillik.txt"), "w", encoding="utf-8").write("\n".join(qator) + "\n")
    print("\n".join(qator))


if __name__ == "__main__":
    main()
