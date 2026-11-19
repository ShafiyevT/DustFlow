# -*- coding: utf-8 -*-
"""DustFlow — namunaviy hisoblash."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dustflow.grid import Tor, relyef_yarat
from dustflow.data import buxoro_maydonlari
from dustflow.model import Model

t = Tor(Lx=380e3, Ly=390e3, Hz=5000.0, N=40, M=40, L=30, beta_s=8.0)
t.eta = relyef_yarat(t); t.He = t.Hz - t.eta

k = buxoro_maydonlari(t, U10_qiymat=12.0, yonalish=40.0)
print("kirish maydonlari tekshiruvi:", k.tekshir() or "xatoliksiz")

m = Model(t, k, sxema="aniq")      # yoki sxema="tezkor"
m.ishga_tushir(T=6 * 3600, dt=120.0)

b = m.massa_balansi()
print(f"\nchiqqan   : {b['Q_em']/1e6:8.1f} ming tonna")
print(f"cho'kkan  : {b['Q_cho']/1e6:8.1f} ming tonna")
print(f"chegaradan: {b['Q_chiq']/1e6:8.1f} ming tonna")
print(f"sohada    : {b['Q']/1e6:8.1f} ming tonna")
print(f"balans nomuvofiqligi: {b['nisbiy']:.4f} %")
