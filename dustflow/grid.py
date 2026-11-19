# -*- coding: utf-8 -*-
"""Hisoblash to'ri va relyefga moslashgan koordinatalar.

Dissertatsiya, III bob: s = (z - eta)/He, He = Hz - eta  (3.9)-(3.12).
To'r tugunli (nodal): chegaraviy tugunlar ham noma'lumlar qatoriga kiradi,
shuning uchun hajm va yuza integrallari trapetsiya og'irliklari bilan olinadi.
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class Tor:
    """Uch o'lchovli hisoblash to'ri."""
    Lx: float          # soha uzunligi, m
    Ly: float          # soha kengligi, m
    Hz: float          # yuqori chegara balandligi, m
    N: int             # x bo'yicha tugunlar
    M: int             # y bo'yicha tugunlar
    L: int             # s bo'yicha tugunlar
    eta: np.ndarray = None   # relyef eta(x,y), m
    beta_s: float = 0.0      # vertikal quyuqlashtirish parametri (0 — tekis to'r)

    def __post_init__(self):
        self.dx = self.Lx / self.N
        self.dy = self.Ly / self.M
        self.x = np.arange(self.N + 1) * self.dx
        self.y = np.arange(self.M + 1) * self.dy
        zeta = np.arange(self.L + 1) / self.L
        if self.beta_s > 0:
            # yer sirti yaqinida quyuqlashgan to'r: s = (e^{beta zeta} - 1)/(e^{beta} - 1)
            self.s = np.expm1(self.beta_s * zeta) / np.expm1(self.beta_s)
        else:
            self.s = zeta
        self.hs = np.diff(self.s)              # s bo'yicha qadamlar (L,)
        self.ds = float(self.hs.mean())
        if self.eta is None:
            self.eta = np.zeros((self.N + 1, self.M + 1))
        self.He = self.Hz - self.eta          # (3.9)

    @property
    def shakl(self):
        return (self.N + 1, self.M + 1, self.L + 1)

    def balandlik(self):
        """Har bir tugunning haqiqiy z balandligi, m."""
        return self.eta[:, :, None] + self.He[:, :, None] * self.s[None, None, :]

    @staticmethod
    def _trap(n):
        w = np.ones(n + 1); w[0] = w[-1] = 0.5
        return w

    def yuza_ogirligi(self):
        """Gorizontal tugunlarga mos yuza, m^2 (chegarada yarim, burchakda chorak)."""
        return self.dx * self.dy * np.outer(self._trap(self.N), self._trap(self.M))

    def s_ogirligi(self):
        """s bo'yicha tugunlarga mos uzunliklar (trapetsiya), o'lchamsiz."""
        w = np.zeros(self.L + 1)
        w[:-1] += 0.5 * self.hs; w[1:] += 0.5 * self.hs
        return w

    def yacheyka_hajmi(self):
        """Tugunga mos hajm (trapetsiya og'irliklari bilan), m^3."""
        return (self.yuza_ogirligi()[:, :, None] * self.He[:, :, None]
                * self.s_ogirligi()[None, None, :])

    def metrik(self):
        """ds/dx va ds/dy metrik koeffitsiyentlari, (3.62)."""
        d_eta_dx = np.gradient(self.eta, self.dx, axis=0)
        d_eta_dy = np.gradient(self.eta, self.dy, axis=1)
        one_minus_s = 1.0 - self.s[None, None, :]
        ds_dx = -one_minus_s * d_eta_dx[:, :, None] / self.He[:, :, None]
        ds_dy = -one_minus_s * d_eta_dy[:, :, None] / self.He[:, :, None]
        return ds_dx, ds_dy


def relyef_yarat(tor: Tor, tur: str = "buxoro", amplituda: float = 250.0):
    """Namunaviy relyef maydonini yaratadi."""
    X, Y = np.meshgrid(tor.x, tor.y, indexing="ij")
    xn, yn = X / tor.Lx, Y / tor.Ly
    if tur == "tekis":
        return np.zeros_like(X)
    if tur == "buxoro":
        # Qizilqum tomonda past tepaliklar, vohada tekis pastlik
        e = (amplituda * np.exp(-(((xn - 0.30) / 0.22) ** 2 + ((yn - 0.70) / 0.28) ** 2))
             + 0.7 * amplituda * np.exp(-(((xn - 0.62) / 0.18) ** 2 + ((yn - 0.45) / 0.20) ** 2))
             + 0.4 * amplituda * np.exp(-(((xn - 0.85) / 0.15) ** 2 + ((yn - 0.80) / 0.22) ** 2)))
        return e
    raise ValueError(f"noma'lum relyef turi: {tur}")
