# -*- coding: utf-8 -*-
"""Hisoblash natijalarini haqiqiy karta asosida chizish.

Karta asosi OpenStreetMap plitkalaridan olinadi (contextily kutubxonasi orqali).
Internet mavjud boʻlmaganda sxematik asosga avtomatik oʻtiladi.

Talab qilinadigan kutubxonalar:
    pip install contextily pyproj

Foydalanish:
    python -m dustflow.karta natija.npz --lon 64.4252 --lat 39.7682
yoki dasturda:
    from dustflow.karta import karta_chiz
    karta_chiz(x, y, C, lon0=64.4252, lat0=39.7682, manba_qutisi=(x0,y0,x1,y1))
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Polygon, FancyArrow, FancyBboxPatch

# Konsentratsiya sinflari, mkg/m3
CHEGARALAR = [50, 100, 200, 300, 500, 1000, 2000, 4000, 8000]
RANGLAR = ["#cfc9c4", "#c5aa9c", "#c0907d", "#c4735d", "#c25844",
           "#b93d31", "#a32820", "#851713", "#5e0d0b"]
ETIKETLAR = ["50 – 100", "100 – 200", "200 – 300", "300 – 500", "500 – 1000",
             "1000 – 2000", "2000 – 4000", "4000 – 8000", "> 8000"]
REMK = 300.0        # noorganik chang uchun ruxsat etilgan maksimal konsentratsiya

R_YER = 6378137.0


# ---------------------------------------------------------------
def lonlat_to_merc(lon, lat):
    """Geografik koordinatalardan Web Mercator (EPSG:3857) ga."""
    x = R_YER * np.deg2rad(lon)
    y = R_YER * np.log(np.tan(np.pi / 4.0 + np.deg2rad(lat) / 2.0))
    return x, y


def tor_merc(x_m, y_m, lon0, lat0):
    """Model toʻrini (metr, lokal) Web Mercator koordinatalariga oʻtkazadi.

    Model koordinatalari lokal ekvitoreal proyeksiyada berilgani uchun
    masshtab koeffitsiyenti orqali qayta hisoblanadi.
    """
    cx, cy = lonlat_to_merc(lon0, lat0)
    k = 1.0 / np.cos(np.deg2rad(lat0))        # Mercator masshtab koeffitsiyenti
    X = cx + (x_m - x_m.mean()) * k
    Y = cy + (y_m - y_m.mean()) * k
    return X, Y


def _asos_qoysh(ax, manba="OSM"):
    """OSM plitkalarini fon sifatida qoʻyadi. Muvaffaqiyatsiz boʻlsa False."""
    try:
        import contextily as cx
        uslub = {"OSM": cx.providers.OpenStreetMap.Mapnik,
                 "CARTO": cx.providers.CartoDB.Positron,
                 "TOPO": cx.providers.OpenTopoMap}.get(
                     manba, cx.providers.OpenStreetMap.Mapnik)
        cx.add_basemap(ax, source=uslub, crs="EPSG:3857",
                       attribution_size=6, zoom="auto")
        return True
    except Exception as e:                      # internet yoki kutubxona yoʻq
        print(f"  [eslatma] karta asosini yuklab boʻlmadi ({type(e).__name__}); "
              f"sxematik asos ishlatiladi")
        return False


# ---------------------------------------------------------------
def karta_chiz(x_m, y_m, C, lon0, lat0, manba_qutisi=None,
               yonalish=40.0, U10=None, sarlavha="", izoh="",
               oyna=None, asos="OSM", yol="karta.png",
               malumot=None, silliqlash=1.1):
    """Konsentratsiya maydonini karta ustiga chizadi.

    x_m, y_m  — model toʻri, metr
    C         — konsentratsiya, mkg/m3, shakli (len(x), len(y))
    lon0,lat0 — soha markazining geografik koordinatalari
    manba_qutisi — manba chegaralari (x0, y0, x1, y1), metr
    oyna      — koʻrsatiladigan soha (x0, y0, x1, y1), metr; None — hammasi
    malumot   — chap panelda koʻrsatiladigan (nom, qiymat) juftliklari
    """
    X, Y = tor_merc(x_m, y_m, lon0, lat0)
    k = 1.0 / np.cos(np.deg2rad(lat0))

    fig = plt.figure(figsize=(14.6, 9.8))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.185, 0.085, 0.795, 0.845])

    if oyna:
        cx0, cy0 = tor_merc(np.array([oyna[0], oyna[2]]),
                            np.array([oyna[1], oyna[3]]), lon0, lat0)
        # markazni saqlagan holda
        mx = X.mean(); my = Y.mean()
        ax.set_xlim(mx + (oyna[0] - x_m.mean()) * k, mx + (oyna[2] - x_m.mean()) * k)
        ax.set_ylim(my + (oyna[1] - y_m.mean()) * k, my + (oyna[3] - y_m.mean()) * k)
    else:
        ax.set_xlim(X.min(), X.max()); ax.set_ylim(Y.min(), Y.max())
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])

    bor = _asos_qoysh(ax, asos)
    if not bor:
        ax.set_facecolor("#f2efe9")

    # --- konsentratsiya qatlami ---
    try:
        from scipy.ndimage import gaussian_filter
        Cs = gaussian_filter(np.asarray(C).T, sigma=silliqlash)
    except ImportError:
        Cs = np.asarray(C).T
    ax.contourf(X, Y, Cs, levels=CHEGARALAR + [1e12], colors=RANGLAR,
                alpha=0.58, zorder=5)
    ct = ax.contour(X, Y, Cs, levels=[REMK], colors="#4a0000",
                    linewidths=2.0, zorder=6)
    ax.clabel(ct, fmt=lambda v: f"REMK {REMK:.0f}", fontsize=8.5, colors="#4a0000")

    # --- manba ---
    if manba_qutisi:
        mx = X.mean(); my = Y.mean()
        bx0 = mx + (manba_qutisi[0] - x_m.mean()) * k
        bx1 = mx + (manba_qutisi[2] - x_m.mean()) * k
        by0 = my + (manba_qutisi[1] - y_m.mean()) * k
        by1 = my + (manba_qutisi[3] - y_m.mean()) * k
        ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0,
                               facecolor="none", edgecolor="#1a1a1a", lw=2.4,
                               hatch="///", zorder=7))
        ax.text((bx0 + bx1) / 2, by1 + (by1 - by0) * 0.12, "MANBA",
                fontsize=9.5, fontweight="bold", ha="center", zorder=8,
                bbox=dict(fc="white", ec="#1a1a1a", lw=0.9, alpha=0.9,
                          boxstyle="round,pad=0.3"))

    # --- shamol strelkasi ---
    x0a, x1a = ax.get_xlim(); y0a, y1a = ax.get_ylim()
    Lx_ = x1a - x0a; Ly_ = y1a - y0a
    ang = np.deg2rad(yonalish)
    sx = x0a + 0.12 * Lx_; sy = y0a + 0.14 * Ly_
    ax.add_patch(FancyArrow(sx, sy, 0.11 * Lx_ * np.cos(ang),
                            0.11 * Lx_ * np.sin(ang),
                            width=0.006 * Lx_, head_width=0.022 * Lx_,
                            head_length=0.024 * Lx_, facecolor="#12306b",
                            edgecolor="white", lw=1.0, zorder=10,
                            length_includes_head=True))
    if U10:
        ax.text(sx, sy - 0.045 * Ly_, f"shamol {U10:.1f} m/s", fontsize=9,
                color="#12306b", fontweight="bold", ha="center", zorder=10,
                bbox=dict(fc="white", ec="#12306b", lw=0.9, alpha=0.9,
                          boxstyle="round,pad=0.3"))

    # --- masshtab ---
    sb_m = 500.0 * k
    bx = x1a - sb_m - 0.05 * Lx_; by = y0a + 0.05 * Ly_
    ax.add_patch(Rectangle((bx - 0.015 * Lx_, by - 0.022 * Ly_),
                           sb_m + 0.045 * Lx_, 0.055 * Ly_,
                           facecolor="white", edgecolor="#b0aaa0",
                           alpha=0.9, zorder=11))
    ax.plot([bx, bx + sb_m], [by, by], color="#2b2b2b", lw=3.2, zorder=12)
    ax.text(bx + sb_m / 2, by + 0.012 * Ly_, "500 m", fontsize=8.6,
            ha="center", zorder=12)

    # --- shimol ---
    nx_ = x0a + 0.045 * Lx_; ny_ = y1a - 0.10 * Ly_
    ax.add_patch(Polygon([[nx_, ny_ + 0.035 * Ly_], [nx_ - 0.012 * Lx_, ny_ - 0.022 * Ly_],
                          [nx_, ny_ - 0.009 * Ly_], [nx_ + 0.012 * Lx_, ny_ - 0.022 * Ly_]],
                         closed=True, facecolor="#2b2b2b", edgecolor="white",
                         lw=1.0, zorder=12))
    ax.text(nx_, ny_ + 0.048 * Ly_, "N", fontsize=11.5, fontweight="bold",
            ha="center", zorder=12)

    # --- chap panel ---
    fig.text(0.014, 0.945, "Chang konsentratsiyasi", fontsize=13.5,
             fontweight="bold", color="#1f2d3d")
    fig.text(0.014, 0.921, "yer sirtiga yaqin qatlamda,  mkg/m³",
             fontsize=9, color="#5a6672")
    lx, ly, lw_, lh = 0.022, 0.868, 0.036, 0.0335
    for i, (c, e) in enumerate(zip(RANGLAR, ETIKETLAR)):
        yy = ly - i * (lh + 0.004)
        fig.patches.append(plt.Rectangle((lx, yy - lh), lw_, lh,
                           transform=fig.transFigure, facecolor=c,
                           edgecolor="#9e9e9e", lw=0.6, alpha=0.85))
        fig.text(lx + lw_ + 0.011, yy - lh / 2, e, fontsize=8.6,
                 va="center", color="#333")
        if e == "300 – 500":
            fig.text(lx + lw_ + 0.088, yy - lh / 2, "◀ REMK", fontsize=8.4,
                     va="center", color="#a32820", fontweight="bold")

    if malumot:
        yb = ly - 9 * (lh + 0.004) - 0.03
        fig.patches.append(FancyBboxPatch((0.016, yb - 0.048 - 0.032 * len(malumot)),
                           0.152, 0.038 + 0.032 * len(malumot),
                           transform=fig.transFigure,
                           boxstyle="round,pad=0.008,rounding_size=0.01",
                           facecolor="#f5f7f9", edgecolor="#c8d2da", lw=1.0))
        for i, (a_, b_) in enumerate(malumot):
            yy = yb - 0.024 - i * 0.0322
            fig.text(0.026, yy, a_, fontsize=8.0, color="#5a6672")
            fig.text(0.026, yy - 0.0135, b_, fontsize=8.4, color="#1f2d3d",
                     fontweight="bold")

    if sarlavha:
        fig.text(0.585, 0.963, sarlavha, fontsize=13.5, fontweight="bold",
                 ha="center", color="#1f2d3d")
    if izoh:
        fig.text(0.585, 0.944, izoh, fontsize=9, ha="center", color="#5a6672")

    fig.savefig(yol, bbox_inches="tight", facecolor="white", pad_inches=0.18, dpi=300)
    print(f"  karta saqlandi: {yol}")
    return fig


# ---------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(prog="dustflow.karta",
                                description="Natijalarni karta ustida chizish")
    p.add_argument("fayl", help="npz fayli (npz_eksport bilan yaratilgan)")
    p.add_argument("--lon", type=float, required=True, help="soha markazi, uzunlik")
    p.add_argument("--lat", type=float, required=True, help="soha markazi, kenglik")
    p.add_argument("--asos", default="OSM", choices=["OSM", "CARTO", "TOPO"])
    p.add_argument("--yonalish", type=float, default=40.0)
    p.add_argument("-o", "--chiqish", default="karta.png")
    a = p.parse_args(argv)

    d = np.load(a.fayl)
    x, y = d["x"], d["y"]
    C = d["C"].sum(axis=0)[:, :, 0] * 1e9 if d["C"].ndim == 4 else d["C"]
    karta_chiz(x, y, C, a.lon, a.lat, yonalish=a.yonalish,
               asos=a.asos, yol=a.chiqish)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
