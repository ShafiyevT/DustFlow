# -*- coding: utf-8 -*-
"""Zarrachalar harakat tezliklari — DustVel 2.0 yadrosining maydon ko'rinishi.

Dissertatsiya, III bob, § 3.1-3.2:
  tau_i = rho_i d_i^2 / (18 mu_a),   f(Re) = 1 + 0.15 Re^0.687          (3.4)
  muvozanat cho'kish tezligi: w_s f(rho_a d w_s / mu_a) = g tau        (3.6), (3.30)
  makroqadam: simmetrik oshkormas sxema (3.20) + 2 x ikkinchi tartibli
  uch qatlamli oshkormas sxema (3.23), (3.25); har bir kichik qadamda
  komponentalar bo'yicha iteratsiya (3.26), to'xtash sharti (3.27).
Barcha to'r tugunlari uchun vektorlashtirilgan.
"""
import numpy as np

G = 9.81
MU_A = 1.81e-5
RHO_A = 1.225


def f_Re(Re):
    """Reynolds soniga bog'liq qarshilik tuzatmasi  —  (3.4)."""
    return 1.0 + 0.15 * np.power(np.maximum(Re, 0.0), 0.687)


def relaksatsiya_vaqti(d, rho_p, mu_a=MU_A):
    """tau = rho_p d^2 / (18 mu_a), s  —  (3.4)."""
    return rho_p * d ** 2 / (18.0 * mu_a)


def beta_koef(d, rho_p, mu_a=MU_A):
    """Stoks qarshiligi koeffitsiyenti 1/tau (orqaga moslik uchun)."""
    return 1.0 / relaksatsiya_vaqti(d, rho_p, mu_a)


def stoks_tezligi(d, rho_p, mu_a=MU_A):
    """Stoks qonuni bo'yicha gravitatsion cho'kish tezligi w_g = g tau  —  (2.13)."""
    return G * relaksatsiya_vaqti(d, rho_p, mu_a)


def chokish_tezligi(d, rho_p, mu_a=MU_A, rho_a=RHO_A, qarshilik="re",
                    eps=1e-12, smax=200):
    """Muvozanat cho'kish tezligi w_s, m/s  —  (3.6), iteratsiya (3.30).

    qarshilik = "stoks" bo'lsa w_s = w_g (II bobdagi chiziqli model).
    """
    wg = stoks_tezligi(d, rho_p, mu_a)
    if qarshilik == "stoks":
        return wg
    k = rho_a * d / mu_a
    w = wg
    for _ in range(smax):
        wn = wg / f_Re(k * w)
        if abs(wn - w) <= eps * max(wn, 1e-30):
            return float(wn)
        w = wn
    return float(w)


class TezlikMaydoni:
    """Bitta fraksiya zarrachalarining tezliklar maydoni (holat makroqadamlar orasida saqlanadi)."""

    def __init__(self, d, rho_p, mu_a=MU_A, rho_a=RHO_A, qarshilik="re",
                 eps=1e-10, smax=50):
        self.d, self.rho_p = d, rho_p
        self.tau = relaksatsiya_vaqti(d, rho_p, mu_a)
        self.kRe = rho_a * d / mu_a
        self.qarshilik = qarshilik
        self.eps, self.smax = eps, smax
        self.w_s = chokish_tezligi(d, rho_p, mu_a, rho_a, qarshilik)
        self.v = None                    # (vx, vy, vz)
        self.iteratsiyalar = []

    def _lam(self, U, V):
        if self.qarshilik == "stoks":
            return np.full(U[0].shape, 1.0 / self.tau)
        r = np.sqrt((U[0] - V[0]) ** 2 + (U[1] - V[1]) ** 2 + (U[2] - V[2]) ** 2)
        return f_Re(self.kRe * r) / self.tau

    def muvozanat(self, U, Vv, W):
        """Muvozanat holati: v = u, v_z = w - w_s."""
        return [U.copy(), Vv.copy(), W - self.w_s]

    def _kichik_qadam(self, dt, v0, vm, u0, u1, sxema):
        """(3.20) yoki (3.23)/(3.25) va (3.26) iteratsiya; dt — makroqadam."""
        dz = (0.0, 0.0, 1.0)
        if sxema == "kn":
            lam0 = self._lam(u0, v0)
            v = [a.copy() for a in v0]
        else:
            v = [2.0 * v0[c] - vm[c] for c in range(3)]
        for m in range(1, self.smax + 1):
            dmax = 0.0
            for c in range(3):
                lam = self._lam(u1, v)
                if sxema == "kn":
                    vn = ((6.0 - dt * lam0) * v0[c] + dt * (lam * u1[c] + lam0 * u0[c])
                          - 2.0 * dt * G * dz[c]) / (6.0 + dt * lam)
                else:
                    vn = (12.0 * v0[c] - 3.0 * vm[c] + 2.0 * dt * lam * u1[c]
                          - 2.0 * dt * G * dz[c]) / (9.0 + 2.0 * dt * lam)
                dmax = max(dmax, float(np.max(np.abs(vn - v[c]))))
                v[c] = vn
            vabs = float(np.max(np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)))
            if dmax <= self.eps * max(1.0, vabs):
                break
        self.iteratsiyalar.append(m)
        return v

    def qadam(self, U, V, W, dt, U_old=None):
        """Bitta makroqadam. U, V, W — havo tezligi (yangi qatlamda);
        U_old — oldingi qatlamdagi havo tezligi (berilmasa, o'zgarmas deb olinadi).
        Qaytaradi: (vx, vy, vz) n+1 qatlamda."""
        u1 = (U, V, W)
        u0 = U_old if U_old is not None else u1
        if self.v is None:
            self.v = self.muvozanat(*u0)
        # havo tezligi makroqadam ichida chiziqli interpolyatsiya qilinadi
        uk = [tuple(a0 + k / 3.0 * (a1 - a0) for a0, a1 in zip(u0, u1)) for k in (1, 2, 3)]
        v13 = self._kichik_qadam(dt, self.v, None, u0, uk[0], "kn")
        v23 = self._kichik_qadam(dt, v13, self.v, None, uk[1], "bdf2")
        v1 = self._kichik_qadam(dt, v23, v13, None, uk[2], "bdf2")
        self.v = v1
        return tuple(v1)


def tezlik_maydoni(U, V, W_havo, d, rho_p, dt, mu_a=MU_A, n_qadam=1, qarshilik="re"):
    """Orqaga moslik uchun: muvozanat holatdan boshlab n_qadam makroqadam."""
    tm = TezlikMaydoni(d, rho_p, mu_a, qarshilik=qarshilik)
    for _ in range(n_qadam):
        v = tm.qadam(U, V, W_havo, dt)
    return v
