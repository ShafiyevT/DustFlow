# -*- coding: utf-8 -*-
"""Massa balansini nazorat qilish.

Sohadagi massa Q(t) = sum th dV (tugunli to'r, trapetsiya og'irliklari) va
chegaralar orqali oqimlar yig'indisi taqqoslanadi:
    Q(t) = Q(0) + Q_em - Q_cho - Q_chiq - Q_yut (+ manfiy qiymatlarni kesishda qo'shilgan massa).
Advektiv shakldagi sxema massani aynan saqlamaydi, shuning uchun nomuvofiqlik
sxemaning konservativlik xatosini ko'rsatadi.
"""
import numpy as np


class Balans:
    def __init__(self, tor):
        self.tor = tor
        self.dV = tor.yacheyka_hajmi()
        self.Q_em = 0.0
        self.Q_cho = 0.0
        self.Q_chiq = 0.0
        self.Q_yut = 0.0
        self.tarix = []

    def massa(self, C):
        """Sohadagi umumiy massa, kg."""
        if C.ndim == 4:
            return float(np.sum(C * self.dV[None, ...]))
        return float(np.sum(C * self.dV))

    def emissiya_qosh(self, F, dt):
        """Yer sirtidan chiqqan massa, kg."""
        self.Q_em += float(np.sum(F * self.tor.yuza_ogirligi()) * dt)

    def chokish_qosh(self, oqim, dt):
        """Sirtga cho'kkan massa, kg (oqim — w_d th, kg/(m^2 s))."""
        self.Q_cho += float(np.sum(oqim * self.tor.yuza_ogirligi()) * dt)

    def yutilish_qosh(self, C, sigma, dt):
        """Atmosferada yutilgan massa, kg."""
        self.Q_yut += float(np.sum(sigma * C * self.dV) * dt)

    def yozib_bor(self, t, C):
        Q = self.massa(C)
        kutilgan = self.Q_em - self.Q_cho - self.Q_chiq - self.Q_yut
        self.tarix.append(dict(t=t, Q=Q, Q_em=self.Q_em, Q_cho=self.Q_cho,
                               Q_chiq=self.Q_chiq, Q_yut=self.Q_yut,
                               kutilgan=kutilgan))
        return Q

    def nomuvofiqlik(self, Q0=0.0):
        """Balansning nisbiy nomuvofiqligi, %."""
        if not self.tarix:
            return 0.0
        z = self.tarix[-1]
        kutilgan = Q0 + z["Q_em"] - z["Q_cho"] - z["Q_chiq"] - z["Q_yut"]
        if abs(kutilgan) < 1e-30:
            return 0.0
        return abs(z["Q"] - kutilgan) / abs(kutilgan) * 100.0
