# -*- coding: utf-8 -*-
"""Natijalarni eksport qilish moduli."""
import os
import numpy as np


def csv_eksport(yol, tor, maydon, sarlavha="konsentratsiya"):
    """Ikki o'lchovli maydonni CSV ga yozadi (x, y, qiymat)."""
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        f.write(f"x_m,y_m,{sarlavha}\n")
        for i, x in enumerate(tor.x):
            for j, y in enumerate(tor.y):
                f.write(f"{x:.1f},{y:.1f},{maydon[i, j]:.6e}\n")
    return yol


def ascii_grid_eksport(yol, tor, maydon, nodata=-9999.0):
    """GIS dasturlari uchun ESRI ASCII Grid formati."""
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        f.write(f"ncols {tor.N + 1}\n")
        f.write(f"nrows {tor.M + 1}\n")
        f.write("xllcorner 0.0\n")
        f.write("yllcorner 0.0\n")
        f.write(f"cellsize {tor.dx:.2f}\n")
        f.write(f"NODATA_value {nodata}\n")
        for j in range(tor.M, -1, -1):
            f.write(" ".join(f"{maydon[i, j]:.6e}" for i in range(tor.N + 1)) + "\n")
    return yol


def npz_eksport(yol, tor, model):
    """To'liq natijani NumPy arxiviga saqlaydi."""
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    np.savez_compressed(
        yol, x=tor.x, y=tor.y, s=tor.s, eta=tor.eta, He=tor.He,
        C=model.C.astype(np.float32), F=model.F.astype(np.float32),
        U=model.U.astype(np.float32), V=model.V.astype(np.float32),
        vaqt=model.vaqt, tau=model.tau, v_t=model.v_t)
    return yol


def hisobot(yol, model, stsenariy=None):
    """Matnli hisobot yaratadi."""
    b = model.massa_balansi()
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        f.write("DustFlow — hisoblash hisoboti\n")
        f.write("=" * 60 + "\n")
        if stsenariy:
            f.write(f"Stsenariy      : {stsenariy.nom}\n")
            f.write(f"Shamol tezligi : {stsenariy.U10} m/s, yo'nalish {stsenariy.yonalish}°\n")
            f.write(f"To'r           : {stsenariy.N}x{stsenariy.M}x{stsenariy.L}\n")
        f.write(f"Hisoblash davri: {model.vaqt/3600:.1f} soat\n")
        f.write(f"Sxema          : {model.sxema}  (aniq — 2-tartib, tezkor — 1-tartib)\n")
        f.write(f"Cho'kish       : {model.qarshilik}  (re — f(Re), stoks — Stoks qonuni)\n")
        f.write(f"C_alpha        : {model.C_alpha:g}\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'chiqqan massa':<28}{b['Q_em']/1e6:12.2f} ming tonna\n")
        f.write(f"{'cho''kkan massa':<28}{b['Q_cho']/1e6:12.2f} ming tonna\n")
        f.write(f"{'chegaradan chiqqan':<28}{b['Q_chiq']/1e6:12.2f} ming tonna\n")
        f.write(f"{'atmosferada yutilgan':<28}{b['Q_yut']/1e6:12.2f} ming tonna\n")
        f.write(f"{'sohada muallaq':<28}{b['Q']/1e6:12.2f} ming tonna\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'balans nomuvofiqligi':<28}{b['nisbiy']:12.5f} %\n")
        yuza = model.yuza_konsentratsiya() * 1e9
        f.write(f"{'yuza konsentratsiyasi':<28}{yuza.mean():12.1f} mkg/m3 (o'rtacha)\n")
        f.write(f"{'':<28}{yuza.max():12.1f} mkg/m3 (maksimal)\n")
    return yol
