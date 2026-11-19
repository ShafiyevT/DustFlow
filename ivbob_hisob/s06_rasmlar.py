# -*- coding: utf-8 -*-
"""6-qadam. IV bob rasmlari (4.5–4.10) — ivbob_natija/rasm_4_*.png."""
import os, sys, json, pickle
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

N_ = U.NATIJA
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.linewidth": 0.8,
                     "grid.color": "#d9d9d9", "grid.linewidth": 0.6})
QIZ, OCH, KOK, KUL = "#d35400", "#f0b27a", "#2471b5", "#bdc3c7"
ST = U.STANSIYA


def _sn():
    global SN, LON, LAT, EXT
    SN = pickle.load(open(f"{N_}/boron_mahalliy_maydon.pkl", "rb"))
    LON, LAT = SN["lon"], SN["lat"]
    EXT = [LON[0], LON[-1], LAT[0], LAT[-1]]


def stansiyalar(ax, rang="k"):
    for s, (nm, la, lo) in ST.items():
        ax.plot(lo, la, "^", color="w", mec=rang, ms=6)
        # sharqiy chekkaga yaqin stansiya nomi chap tomonga yoziladi (kesilmasligi uchun)
        if lo > EXT[1] - 0.6:
            ax.text(lo - 0.07, la + 0.05, nm, fontsize=8, color=rang, ha="right")
        else:
            ax.text(lo + 0.07, la + 0.05, nm, fontsize=8, color=rang)


def r45():
    _sn(); c = SN["choqqi"]
    fig, ax = plt.subplots(1, 3, figsize=(13, 4.5))
    for a, (f, nom, cm, kw) in zip(ax, [(c["us"], r"a) $u_*$, m/s", "viridis", dict(vmin=0, vmax=1.6)),
                                         (c["ut"], r"b) $u_{*t}$, m/s", "magma_r", dict(vmin=0.2, vmax=1.2)),
                                         (np.where(c["F"] > 0, c["F"] * 1e9, np.nan),
                                          r"c) $F_e$, mkg/(m²·s)", "YlOrRd", dict(norm=LogNorm(1, 3e3)))]):
        im = a.imshow(np.asarray(f).T, origin="lower", extent=EXT, cmap=cm, aspect="auto", **kw)
        plt.colorbar(im, ax=a, shrink=0.85); a.set_title(nom, loc="left"); stansiyalar(a, "#222")
        a.set_xlabel("uzunlik, °"); a.set_ylabel("kenglik, °")
    fig.tight_layout(); fig.savefig(f"{N_}/rasm_4_5_emissiya.png", dpi=300); plt.close(fig)


def r46():
    _sn(); c = SN["choqqi"]
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    im = ax.imshow(np.maximum(c["yuza"], 1).T, origin="lower", extent=EXT, cmap="YlOrRd", aspect="auto",
                   norm=LogNorm(10, max(1e3, np.percentile(c["yuza"], 99.5))))
    plt.colorbar(im, ax=ax, shrink=0.9, label="chang konsentratsiyasi, mkg/m³")
    s = slice(None, None, 4)
    ax.quiver(LON[s], LAT[s], c["U"][s, s].T, c["V"][s, s].T, color="#555", scale=250, width=0.0025)
    stansiyalar(ax, "#14507d"); ax.set_xlabel("uzunlik, °"); ax.set_ylabel("kenglik, °")
    fig.tight_layout(); fig.savefig(f"{N_}/rasm_4_6_konsentratsiya.png", dpi=300); plt.close(fig)


def r47():
    S = json.load(open(f"{N_}/sezgirlik.json"))["param"]
    S = sorted(S, key=lambda r: r["S"])
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw=dict(width_ratios=[1.6, 1]))
    y = np.arange(len(S))
    ax[0].barh(y - 0.2, [r["minus"] for r in S], 0.4, color=KOK, label="−25 %")
    ax[0].barh(y + 0.2, [r["plus"] for r in S], 0.4, color=QIZ, label="+25 %")
    ax[0].set_yticks(y); ax[0].set_yticklabels([r["nom"] for r in S]); ax[0].axvline(0, color="k", lw=0.8)
    ax[0].set_xlabel("o'rtacha konsentratsiyaning o'zgarishi, %"); ax[0].legend(); ax[0].grid(axis="x")
    ax[0].set_title("a) parametr ±25 % ga o'zgarganda", loc="left")
    ax[1].barh(y, [r["S"] for r in S], color="#7f8c8d"); ax[1].set_yticks(y); ax[1].set_yticklabels([])
    for k, r in enumerate(S):
        ax[1].text(r["S"] + 0.05, k, f"{r['S']:.2f}", va="center", fontsize=9)
    ax[1].axvline(1, color="r", ls="--", lw=1); ax[1].set_xlabel("$S_p$"); ax[1].grid(axis="x")
    ax[1].set_xlim(0, max(r["S"] for r in S) * 1.15)
    ax[1].set_title("b) sezgirlik indeksi (4.10)", loc="left")
    fig.tight_layout(); fig.savefig(f"{N_}/rasm_4_7_sezgirlik.png", dpi=300); plt.close(fig)


def r48():
    from netCDF4 import Dataset, num2date
    import datetime as dt
    B = json.load(open(f"{N_}/baholash.json"))
    d = pd.read_csv(U.STANSIYA_CSV); d["t"] = pd.to_datetime(d.vaqt_utc)
    ds = Dataset(U.CAMS); clon = np.array(ds["longitude"][:]); clat = np.array(ds["latitude"][:])
    T = pd.DatetimeIndex([dt.datetime(x.year, x.month, x.day, x.hour)
                          for x in num2date(ds["valid_time"][:], ds["valid_time"].units)])
    P10 = np.array(ds["pm10"][:]) * 1e9
    Q = {V: pd.DataFrame(json.load(open(f"{N_}/boron_{V}.json"))["qator"]).assign(
        t=lambda x: pd.to_datetime(x.vaqt)).set_index("t") for V in ("chegara", "mahalliy")}
    A, Bt = "2025-04-28 00:00", "2025-04-30 23:00"
    fig = plt.figure(figsize=(15, 9.8)); gs = fig.add_gridspec(3, 3, width_ratios=[1, 1, 0.75])
    for n, (s, (nm, la, lo)) in enumerate(ST.items()):
        ax = fig.add_subplot(gs[n, :2])
        ob = d[d.shahar == s].set_index("t").pm10; fo = B["stansiya"][s]["fon"]
        o = (ob - fo).clip(lower=0).loc[A:Bt]
        ax.fill_between(o.index, o.values, color=KUL, label="kuzatuv − fon")
        ax.plot(Q["chegara"].index, Q["chegara"][f"{s}_pm10"], color=QIZ, lw=2, label="DustFlow (CAMS chegarasi bilan)")
        ax.plot(Q["mahalliy"].index, Q["mahalliy"][f"{s}_pm10"], "--", color=OCH, lw=1.8, label="DustFlow (faqat mahalliy)")
        i = int(np.argmin(abs(clon - lo))); j = int(np.argmin(abs(clat - la)))
        c = pd.Series(P10[:, j, i], index=T); c = (c - B["stansiya"][s]["fon_cams"]).loc[A:Bt]
        ax.plot(c.index, c.values, "o-", color=KOK, ms=4, lw=1.6, label="CAMS − fon")
        k = B["kun"][s]; r = B["stansiya"][s]
        ax.set_title(f"{'abc'[n]}) {nm}:  R = {r['chegara']['r']:.2f} (DustFlow),  {r['CAMS']['r']:.2f} (CAMS);   "
                     f"bo'ron kuni: kuzatuv {k['obs']:.0f}, DustFlow {k['chegara']:.0f} / {k['mahalliy']:.0f}, "
                     f"CAMS {k['CAMS']:.0f} mkg/m³", fontsize=9.5)
        ax.set_ylabel("PM10, mkg/m³"); ax.grid(True)
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
        if n == 0: ax.legend(ncol=2, fontsize=8.5)
    ax = fig.add_subplot(gs[:2, 2]); P = B["pool"]
    mk = ["r", "FAC2", "FB"]; x = np.arange(3)
    for q, (k, rang, lab) in enumerate([("chegara", QIZ, "DustFlow (chegara bilan)"),
                                        ("mahalliy", OCH, "DustFlow (mahalliy)"), ("CAMS", KOK, "CAMS")]):
        v = [P[k]["r"], P[k]["FAC2"], abs(P[k]["FB"])]
        ax.bar(x + (q - 1) * 0.26, v, 0.26, color=rang, ec="k", lw=0.6, label=lab)
        for xx, vv in zip(x + (q - 1) * 0.26, v): ax.text(xx, vv + 0.01, f"{vv:.2f}", ha="center", fontsize=8)
    ax.plot([0.75, 1.25], [0.5, 0.5], "r--"); ax.plot([1.75, 2.25], [0.3, 0.3], "r--")
    ax.set_xticks(x); ax.set_xticklabels(["R", "FAC2", "|FB|"]); ax.legend(fontsize=8.5); ax.grid(axis="y")
    ax.set_title(f"d) 3 stansiya, {B['n']} juftlik, 3 soatlik")
    ax = fig.add_subplot(gs[2, 2]); R = B["nisbat"]
    ax.axhspan(R["obs_min"], R["obs_max"], color="#d5dbdb", label=f"kuzatuv: soatlik oraliq ({R['obs_min']:.2f}–{R['obs_max']:.2f})")
    ax.axhline(R["obs_med"], color="#2c3e50", label=f"kuzatuv: mediana ({R['obs_med']:.2f})")
    for q, (k, rang, lab) in enumerate([("chegara", QIZ, "DustFlow\n(chegara)"), ("mahalliy", OCH, "DustFlow\n(mahalliy)"),
                                        ("CAMS", KOK, "CAMS")]):
        ax.plot(q, R[k], "D", color=rang, mec="k", ms=10); ax.text(q, R[k] + 0.03, f"{R[k]:.2f}", ha="center", weight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels(["DustFlow\n(chegara)", "DustFlow\n(mahalliy)", "CAMS"], fontsize=8.5)
    ax.set_xlim(-0.5, 2.5); ax.set_ylim(0, 0.6); ax.set_ylabel("PM2.5 / PM10"); ax.legend(fontsize=7.5, loc="upper left")
    ax.set_title("e) bo'rondagi zarracha o'lchami, Buxoro"); ax.grid(axis="y")
    fig.tight_layout(); fig.savefig(f"{N_}/rasm_4_8_taqqoslash.png", dpi=300); plt.close(fig)


def r49():
    q = pd.read_csv(f"{N_}/qurilish_soatlik.csv", index_col=0, parse_dates=True).loc["2025-04-28 00:00":"2025-04-30 12:00"]
    J = json.load(open(f"{N_}/qurilish_emissiya.json"))["jadval"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.3), gridspec_kw=dict(width_ratios=[1.5, 1]))
    a = ax[0]; a.bar(q.index, q.E_markaziy, width=0.035, color=QIZ, label="emissiya (gil 15 %, quruq grunt)")
    a.set_ylabel("emissiya, t/soat"); a2 = a.twinx(); a2.plot(q.index, q.U10, color=KOK, lw=1.6, label="$U_{10}$ (ERA5-Land)")
    a2.set_ylabel("$U_{10}$, m/s"); a.set_title("a) soatlik emissiya va shamol tezligi", loc="left"); a.grid(True)
    a.legend(loc="upper left", fontsize=8.5); a2.legend(loc="upper right", fontsize=8.5)
    import matplotlib.dates as mdates
    a.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12])); a.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
    a = ax[1]; g = list(J.keys()); x = np.arange(len(g))
    for q_, (k, rang, lab) in enumerate([("quruq", QIZ, "quruq grunt"), ("era5", OCH, "ERA5-Land namligi"),
                                         ("namlangan", KOK, "namlangan (15 %)")]):
        v = [max(J[gg]["boron"][k], 1e-2) for gg in g]
        a.bar(x + (q_ - 1) * 0.27, v, 0.27, color=rang, ec="k", lw=0.5, label=lab)
    a.set_yscale("log"); a.set_ylim(0.05, 500); a.set_xticks(x); a.set_xticklabels([f"{float(gg)*100:.0f} %" for gg in g])
    a.set_xlabel("gil ulushi"); a.set_ylabel("bo'ron davomida emissiya, t"); a.legend(fontsize=8.5); a.grid(axis="y")
    a.set_title("b) emissiyaning gil ulushi va sirt holatiga bog'liqligi", loc="left")
    fig.tight_layout(); fig.savefig(f"{N_}/rasm_4_9_qurilish_emissiya.png", dpi=300); plt.close(fig)


def r410():
    R = pickle.load(open(f"{N_}/qurilish_tarqalish.pkl", "rb"))
    x = (R["x"] - 10000) / 1000; y = (R["y"] - 10000) / 1000; ext = [x[0], x[-1], y[0], y[-1]]
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))
    for a, (f, nom, lab, cnt) in zip(ax, [(R["yig"]["ort"], "a) 32 soatlik o'rtacha PM10", "mkg/m³", [25, 75]),
                                          (R["yig"]["maks"], "b) soatlik maksimal PM10", "mkg/m³", [25, 75]),
                                          (R["qal"], "c) cho'kma qalinligi", "mkm", [0.1, 1.0])]):
        im = a.imshow(np.maximum(f, 1e-3).T, origin="lower", extent=ext, cmap="YlOrRd", norm=LogNorm(cnt[0] / 10, f.max()))
        cs = a.contour(x, y, f.T, levels=cnt, colors=["#555", "k"], linewidths=1)
        a.clabel(cs, fmt="%g", fontsize=8); plt.colorbar(im, ax=a, shrink=0.85, label=lab)
        si, sj = R["stansiya"]; a.plot(x[si], y[sj], "^", color="w", mec="k", ms=7); a.plot(0, 0, "s", color="k", ms=4)
        a.set_xlim(-6, 6); a.set_ylim(-9, 3); a.set_title(nom, loc="left"); a.set_xlabel("x, km"); a.set_ylabel("y, km")
    fig.tight_layout(); fig.savefig(f"{N_}/rasm_4_10_qurilish_tarqalish.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    for f in (r45, r46, r47, r48, r49, r410):
        try:
            f(); print("  ok", f.__name__)
        except FileNotFoundError as e:
            print("  o'tkazildi", f.__name__, "—", e)
