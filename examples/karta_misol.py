# -*- coding: utf-8 -*-
"""Buxoro qurilish maydoni uchun OSM asosidagi kartani chizish.

Ishlatish (internetli kompyuterda):
    pip install contextily
    python examples/karta_misol.py
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dustflow.grid import Tor
from dustflow.data import KirishMaydonlari
from dustflow.emission import (samarali_kritik_tezlik, qoplam_ulushi, dinamik_tezlik,
                               gorizontal_oqim, vertikal_oqim, fraksiya_ulushlari)
from dustflow.model import Model
from dustflow.karta import karta_chiz

# --- obyekt: Buxoro shahri markazidagi qurilish maydoni ---
LON, LAT = 64.4252, 39.7682
S_MAYDON = 226915.0                     # m2  (Google Maps oʻlchovi)
KENG, UZUN = 430.0, 528.0
U10_OCHIQ, F_PANOH, YONALISH = 22.0, 0.60, 40.0
Z0, W, M_CL, LAM, A_EF = 5.0e-3, 2.0, 0.15, 0.01, 0.80

U10 = U10_OCHIQ * F_PANOH
u_star = float(dinamik_tezlik(np.array([U10]), np.array([Z0]))[0])
CV = float(qoplam_ulushi(LAM))
ut = float(samarali_kritik_tezlik(W, 100 * M_CL, CV))                 # (2.4)
Q = float(gorizontal_oqim(np.array([u_star]), np.array([ut]))[0])    # (2.10)
F = float(vertikal_oqim(Q, 100 * M_CL, CV, A_ef=A_EF))                # (2.12)

t = Tor(Lx=6000.0, Ly=6000.0, Hz=600.0, N=120, M=120, L=24, beta_s=6.0)
t.eta = np.zeros(t.shakl[:2]); t.He = t.Hz - t.eta
X, Y = np.meshgrid(t.x, t.y, indexing="ij")
x0, y0 = 1800.0, 3000.0
qur = (np.abs(X - x0) <= UZUN / 2) & (np.abs(Y - y0) <= KENG / 2)

k = KirishMaydonlari(
    U10=np.full_like(X, U10), yonalish=np.full_like(X, YONALISH),
    w=np.where(qur, W, 4.0), m_cl=np.full_like(X, M_CL),
    lam=np.where(qur, LAM, 0.25), z0=np.where(qur, Z0, 1.0),
    A_ef=np.where(qur, A_EF, 0.0), eta=t.eta)

m = Model(t, k)
p = fraksiya_ulushlari(m.chegaralar)
m.F = np.zeros_like(m.F)
for i in range(m.Nf):
    m.F[i] = np.where(qur, F * p[i], 0.0)

print("hisoblanmoqda...")
m.ishga_tushir(T=2 * 3600, dt=30.0, jim=True)
C = m.yuza_konsentratsiya() * 1e9

ii, jj = np.where(qur)
XC, YC = t.x[int(ii.mean())], t.y[int(jj.mean())]
karta_chiz(
    t.x, t.y, C, lon0=LON, lat0=LAT,
    manba_qutisi=(t.x[ii.min()], t.y[jj.min()], t.x[ii.max()], t.y[jj.max()]),
    oyna=(XC - 900, YC - 1500, XC + 2500, YC + 1200),
    yonalish=YONALISH, U10=U10, asos="OSM",
    sarlavha="Buxoro shahri qurilish maydonidan changning tarqalishi",
    izoh=f"ekstremal shamol ($U_{{10}}$ = {U10_OCHIQ:.0f} m/s ochiq joyda),  "
         f"hisoblash davri 2 soat  ·  DustFlow majmuasi",
    malumot=[("Koordinatalar", f"{LAT:.4f} N, {LON:.4f} E"),
             ("Maydon", f"{S_MAYDON/1e4:.1f} ga"),
             ("$u_*$", f"{u_star:.2f} m/s"),
             ("Emissiya", f"{F*S_MAYDON*3600:.0f} kg/soat")],
    yol="karta_buxoro.png")
