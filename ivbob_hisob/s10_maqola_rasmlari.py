# -*- coding: utf-8 -*-
"""10-qadam. CMES maqolasi rasmlari (Fig. 3, 4, 6-10), ingliz tilida.

    python ivbob_hisob/s10_maqola_rasmlari.py

Talab qiladi: s02 (mahalliy), s03, s04, s09 natijalari. Natija: ivbob_natija/maqola/Fig*.png, *.tif
"""
import os, sys, json, pickle, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import umumiy as U
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm, TwoSlopeNorm
from dustflow import emission as E
from dustflow.velocity import stoks_tezligi, chokish_tezligi

N_ = U.NATIJA
OUT = os.path.join(N_, "maqola"); os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 10, "axes.linewidth": 0.9,
                     "mathtext.fontset": "dejavusans"})
RED, BLUE, GREY, ORANGE, GREEN = "#b03a2e", "#1f4e79", "#9e9e9e", "#e67e22", "#2e7d32"
NAMES = {"bukhara": "Bukhara", "navoi": "Navoi", "navoiy": "Navoi", "karshi": "Karshi", "qarshi": "Karshi",
         "Buxoro": "Bukhara", "Navoiy": "Navoi", "Qarshi": "Karshi"}


def _save(fig, n):
    fig.savefig(f"{OUT}/Fig{n}.png", dpi=300)
    fig.savefig(f"{OUT}/Fig{n}.tif", dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


def _panel(ax, s):
    ax.text(-0.12, 1.04, s, transform=ax.transAxes, fontsize=13, weight="bold")


def _stations(ax, ext, col="k"):
    for s, (nm, la, lo) in U.STANSIYA.items():
        ax.plot(lo, la, "*", color="w", mec=col, ms=10, mew=0.9)
        right = lo > ext[1] - 0.7
        ax.text(lo + (-0.12 if right else 0.12), la + 0.10, NAMES.get(s, NAMES.get(nm, nm)), fontsize=8.5, color=col,
                ha="right" if right else "left")


def fig3():
    us = np.linspace(0.2, 1.2, 600)
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.4))
    for ut, c in zip((0.22, 0.30, 0.45, 0.60), (BLUE, GREEN, ORANGE, RED)):
        F = E.vertikal_oqim(E.gorizontal_oqim(us, ut), 5.0, 0.0, C_alpha=U.C_ALPHA)
        ax[0].semilogy(us, np.where(F > 0, F, np.nan), color=c, lw=1.8, label=rf"$u_{{*t}}^{{eff}}$ = {ut:.2f} m/s")
    ax[0].set_ylim(1e-9, 1e-4); ax[0].set_xlabel(r"Friction velocity $u_*$ (m/s)")
    ax[0].set_ylabel(r"Vertical dust flux $F$ (kg m$^{-2}$ s$^{-1}$)"); ax[0].legend(fontsize=8.5, frameon=False)
    cl = np.linspace(0, 35, 400)
    ax[1].semilogy(cl, U.C_ALPHA * E.sandblast_koeffitsiyenti(cl), "k", lw=1.8)
    ax[1].axvline(20, color="k", ls=":", lw=1); ax[1].text(21, 2e-5, "cap at 20%", color="#555", fontsize=9)
    ax[1].set_xlabel("Clay content (%)"); ax[1].set_ylabel(r"$C_\alpha\,\alpha = F/Q$ (m$^{-1}$)")
    _panel(ax[0], "A"); _panel(ax[1], "B"); fig.tight_layout(); _save(fig, 3)


def fig4():
    ch = np.array([0.2e-6, 2.5e-6, 10e-6, 20e-6, 50e-6, 100e-6])
    D, S, W = (1.5e-6, 6.7e-6, 45e-6), (1.7, 1.6, 1.5), (0.05, 0.40, 0.55)
    d = np.logspace(-7, np.log10(2e-4), 600)
    pdf = sum(w / (np.sqrt(2 * np.pi) * np.log(s)) * np.exp(-np.log(d / Dm) ** 2 / (2 * np.log(s) ** 2))
              for Dm, s, w in zip(D, S, W))
    p = E.fraksiya_ulushlari(ch)
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.4))
    ax[0].semilogx(d * 1e6, pdf, "k", lw=1.8)
    for c in ch: ax[0].axvline(c * 1e6, color=GREY, ls="--", lw=0.9)
    for k in range(5):
        xm = np.sqrt(ch[k] * ch[k + 1]) * 1e6
        ax[0].text(xm, 0.58 + 0.04 * (k % 2), f"{p[k]:.3f}", color=RED, fontsize=8.5, ha="center")
    ax[0].text(0.15, 0.66, "Mass share:", color=RED, fontsize=8.5)
    ax[0].set_ylim(0, 0.72); ax[0].set_xlabel("Diameter (µm)"); ax[0].set_ylabel(r"$dM/d\ln d$ (normalized)")
    rho = np.array([1500.0, 2000.0, 2200.0, 2400.0, 2600.0]); dm = np.sqrt(ch[:-1] * ch[1:])
    dd = np.logspace(-7, np.log10(2e-4), 200)
    ax[1].loglog(dd * 1e6, stoks_tezligi(dd, 2500.0) * 100, color=GREY, lw=1.2, label=r"Stokes, $\rho_p$ = 2500 kg/m$^3$")
    ax[1].loglog(dd * 1e6, [chokish_tezligi(x, 2500.0, qarshilik="re") * 100 for x in dd], color=BLUE, lw=1.6,
                 label=r"with $f(Re)$, $\rho_p$ = 2500 kg/m$^3$")
    ws = np.array([chokish_tezligi(x, r, qarshilik="re") for x, r in zip(dm, rho)]) * 100
    ax[1].loglog(dm * 1e6, ws, "o", color=RED, ms=7, label="Transport fractions")
    for x, y in zip(dm * 1e6, ws): ax[1].text(x * 1.15, y * 0.6, f"{y:.3g}", fontsize=8.5)
    ax[1].set_xlabel("Diameter (µm)"); ax[1].set_ylabel(r"Settling velocity $w_s$ (cm/s)")
    ax[1].legend(fontsize=8.5, frameon=False, loc="upper left")
    _panel(ax[0], "A"); _panel(ax[1], "B"); fig.tight_layout(); _save(fig, 4)


def _snap():
    S = pickle.load(open(f"{N_}/boron_mahalliy_maydon.pkl", "rb"))
    return S, [S["lon"][0], S["lon"][-1], S["lat"][0], S["lat"][-1]]


def fig6():
    S, ext = _snap(); c = S["choqqi"]; lon, lat = S["lon"], S["lat"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    im = ax[0].imshow(np.where(c["F"] > 0, c["F"], np.nan).T, origin="lower", extent=ext, aspect="auto",
                      cmap="YlOrRd", norm=LogNorm(1e-9, 1e-5))
    plt.colorbar(im, ax=ax[0], shrink=0.9, label=r"Emission flux (kg m$^{-2}$ s$^{-1}$)")
    im = ax[1].imshow(np.maximum(c["yuza"], 1).T, origin="lower", extent=ext, aspect="auto", cmap="YlOrBr",
                      norm=LogNorm(10, max(1e3, np.percentile(c["yuza"], 99.5))))
    plt.colorbar(im, ax=ax[1], shrink=0.9, label=r"Near-surface concentration (µg/m$^3$)")
    s = slice(2, None, 5)
    for a in ax:
        a.quiver(lon[s], lat[s], c["U"][s, s].T, c["V"][s, s].T, color="#444", scale=230, width=0.0028)
        _stations(a, ext, "#0b3d66"); a.set_xlabel("Longitude (°E)"); a.set_ylabel("Latitude (°N)")
    _panel(ax[0], "A"); _panel(ax[1], "B"); fig.tight_layout(); _save(fig, 6)


def fig7():
    q = pd.DataFrame(json.load(open(f"{N_}/boron_mahalliy.json"))["qator"])
    q["t"] = pd.to_datetime(q.vaqt) + pd.Timedelta(hours=1); q = q[q.t <= U.BORON_48[1]]
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw=dict(width_ratios=[1.6, 1]))
    for k, lab, col in (("Q_em", "Emitted", "k"), ("Q_cho", "Dry-deposited", RED), ("Q_chiq", "Exported", BLUE),
                        ("Q", "Airborne", ORANGE), ("Q_yut", "Scavenged", GREEN), ("kesilgan", "Undershoot zeroing", GREY)):
        ax[0].plot(q.t, q[k] / 1e6, color=col, lw=1.8, label=lab)
    ax[0].set_ylabel("Mass (kt)"); ax[0].legend(fontsize=8.5, frameon=False, ncol=2)
    r = q[q.Q_em > 0.01 * q.Q_em.max()]                   # emissiya sezilarli bo'lgan davr
    ax[1].plot(r.t, r.nisbiy, "k", lw=1.5); ax[1].set_ylabel("Relative budget residual (%)")
    ax[1].set_ylim(0, max(1.0, r.nisbiy.max() * 1.25)); ax[1].set_xlim(q.t.iloc[0], q.t.iloc[-1])
    for a in ax:
        a.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
        a.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M")); a.grid(color="#e0e0e0", lw=0.6)
    _panel(ax[0], "A"); _panel(ax[1], "B"); fig.tight_layout(); _save(fig, 7)


def fig8():
    S, ext = _snap()
    P = {v: pickle.load(open(f"{N_}/bir_moda_{v}.pkl", "rb"))["ort"].sum(0) for v in ("besh", "bir")}
    T = json.load(open(f"{N_}/bir_moda_taqqoslash.json"))
    vmax = max(1e3, np.percentile(P["besh"], 99.5))
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 8.6)); ax = ax.ravel()
    for a, v, ttl in ((ax[0], "besh", "five fractions"), (ax[1], "bir", "single mode")):
        im = a.imshow(np.maximum(P[v], 1).T, origin="lower", extent=ext, aspect="auto", cmap="YlOrBr", norm=LogNorm(10, vmax))
        plt.colorbar(im, ax=a, shrink=0.9, label=r"48-h mean concentration (µg/m$^3$)"); a.set_title(ttl, fontsize=10)
    rel = np.where(P["besh"] > 1.0, (P["bir"] - P["besh"]) / np.maximum(P["besh"], 1e-9) * 100, np.nan)
    im = ax[2].imshow(rel.T, origin="lower", extent=ext, aspect="auto", cmap="RdBu_r",
                      norm=TwoSlopeNorm(0, vmin=-100, vmax=max(100, np.nanpercentile(rel, 99))))
    plt.colorbar(im, ax=ax[2], shrink=0.9, label="(single − five) / five (%)")
    for a in ax[:3]:
        _stations(a, ext, "#0b3d66"); a.set_xlabel("Longitude (°E)"); a.set_ylabel("Latitude (°N)")
    k = ["chokkan", "chegaradan", "havoda"]; lab = ["Dry-deposited", "Exported", "Airborne"]; x = np.arange(3)
    for o, (v, col, nm) in enumerate((("besh", RED, "Five fractions"), ("bir", BLUE, "Single mode"))):
        vals = [T[v][kk] for kk in k]
        ax[3].bar(x + (o - 0.5) * 0.38, vals, 0.38, color=col, label=nm)
        for xx, vv in zip(x + (o - 0.5) * 0.38, vals): ax[3].text(xx, vv + 8, f"{vv:.0f}", ha="center", fontsize=8.5)
    ax[3].set_xticks(x); ax[3].set_xticklabels(lab); ax[3].set_ylabel("Mass after 48 h (kt)"); ax[3].legend(frameon=False)
    for a, s in zip(ax, "ABCD"): _panel(a, s)
    fig.tight_layout(); _save(fig, 8)


def fig9():
    S = json.load(open(f"{N_}/sezgirlik.json"))["param"]
    en = {"U10": r"Wind speed $U_{10}$", "m_cl": r"Clay fraction $m_{cl}$", "w": r"Soil moisture $w$",
          "A_ef": r"Erodible fraction $A_{ef}$", "C_alpha": r"Calibration coefficient $C_\alpha$",
          "z0": r"Roughness length $z_0$", "lam": r"Roughness density $\lambda$", "eta": r"Terrain elevation $h$"}
    S = sorted(S, key=lambda r: r["S"]); y = np.arange(len(S))
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.barh(y - 0.2, [r["minus"] for r in S], 0.4, color=BLUE, label="−25%")
    ax.barh(y + 0.2, [r["plus"] for r in S], 0.4, color=RED, label="+25%")
    ax.set_yticks(y); ax.set_yticklabels([en.get(r["p"], r["p"]) for r in S]); ax.axvline(0, color="k", lw=0.8)
    lim = max(abs(r["plus"]) for r in S) * 1.25
    for k, r in enumerate(S): ax.text(lim * 0.98, k, rf"$S_p$ = {r['S']:.2f}", va="center", ha="right", fontsize=8.5)
    ax.set_xlim(-max(abs(r["minus"]) for r in S) * 1.2, lim)
    ax.set_xlabel("Change of the domain-mean near-surface concentration (%)"); ax.legend(frameon=False, loc="lower left")
    fig.tight_layout(); _save(fig, 9)


def fig10():
    from netCDF4 import Dataset, num2date
    B = json.load(open(f"{N_}/baholash.json"))
    d = pd.read_csv(U.STANSIYA_CSV); d["t"] = pd.to_datetime(d.vaqt_utc)
    ds = Dataset(U.CAMS); clon = np.array(ds["longitude"][:]); clat = np.array(ds["latitude"][:])
    T = pd.DatetimeIndex([dt.datetime(x.year, x.month, x.day, x.hour) for x in num2date(ds["valid_time"][:], ds["valid_time"].units)])
    P10 = np.array(ds["pm10"][:]) * 1e9
    q = pd.DataFrame(json.load(open(f"{N_}/boron_mahalliy.json"))["qator"]).assign(t=lambda x: pd.to_datetime(x.vaqt)).set_index("t")
    s, (nm, la, lo) = "bukhara", U.STANSIYA["bukhara"]; A, Bt = "2025-04-28 00:00", "2025-04-30 23:00"
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw=dict(width_ratios=[2.3, 1]))
    ob = d[d.shahar == s].set_index("t").pm10
    o = (ob - B["stansiya"][s]["fon"]).clip(lower=0).loc[A:Bt]
    ax[0].fill_between(o.index, o.values, color="#cfcfcf", label="Observed − background")
    ax[0].plot(q.index, q[f"{s}_pm10"], color=RED, lw=1.9, label="Model (local emission)")
    i = int(np.argmin(abs(clon - lo))); j = int(np.argmin(abs(clat - la)))
    c = (pd.Series(P10[:, j, i], index=T) - B["stansiya"][s]["fon_cams"]).loc[A:Bt]
    ax[0].plot(c.index, c.values, "o-", color=BLUE, ms=4, lw=1.5, label="CAMS − background")
    ax[0].set_ylabel(r"Excess PM$_{10}$ (µg/m$^3$)"); ax[0].legend(frameon=False, fontsize=8.5)
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M")); ax[0].grid(color="#e0e0e0", lw=0.6)
    R = B["nisbat"]
    ax[1].axhspan(R["obs_min"], R["obs_max"], color="#dcdcdc", label=f"Observed hourly range ({R['obs_min']:.2f}–{R['obs_max']:.2f})")
    ax[1].axhline(R["obs_med"], color="k", lw=1.2, label=f"Observed median ({R['obs_med']:.2f})")
    for x, (k, col, lab) in enumerate((("mahalliy", RED, "Model"), ("CAMS", BLUE, "CAMS"))):
        ax[1].plot(x, R[k], "D", color=col, mec="k", ms=10); ax[1].text(x, R[k] + 0.03, f"{R[k]:.2f}", ha="center", weight="bold")
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["Model", "CAMS"]); ax[1].set_xlim(-0.6, 1.6); ax[1].set_ylim(0, 0.6)
    ax[1].set_ylabel(r"PM$_{2.5}$ / PM$_{10}$"); ax[1].legend(frameon=False, fontsize=8, loc="upper left")
    _panel(ax[0], "A"); _panel(ax[1], "B"); fig.tight_layout(); _save(fig, 10)


if __name__ == "__main__":
    for f in (fig3, fig4, fig6, fig7, fig9, fig10) + ((fig8,) if os.path.exists(f"{N_}/bir_moda_taqqoslash.json") else ()):
        f(); print(f.__name__, "tayyor")
