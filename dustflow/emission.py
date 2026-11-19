# -*- coding: utf-8 -*-
"""Shamol eroziyasi natijasidagi chang emissiyasi sxemasi.

Dissertatsiya, II bob, § 2.1, (2.1)-(2.12) va (2.25):

  u*        — dinamik tezlik, logarifmik profildan                        (2.1)
  u*t0      — quruq, silliq, o'simliksiz sirt uchun kritik tezlik (Shao-Lu) (2.3)
  u*t       = u*t0(d_s) f_w(w) f_r(z0r) f_v(C_v)                          (2.4)
  f_w       — tuproq namligi tuzatmasi (Fecan va b.)                      (2.5)-(2.6)
  f_r       — g'adir-budurlik tuzatmasi (Marticorena-Bergametti)          (2.7)
  f_v       — o'simlik qoplami tuzatmasi (Raupach va b.)                  (2.8)-(2.9)
  Q         — gorizontal saltatsiya oqimi (White), c = 2.61               (2.10)
  alpha     = 100 * 10^(0.134 %clay - 6), 1/m                             (2.11)
  F_e       = C_alpha * alpha * Q * (1 - C_v)                             (2.12)
  F_e,i     = p_i F_e                                                     (2.25)

C_alpha — kalibrlash koeffitsiyenti (IV bob, § 4.2), standart qiymati 1e-2.
"""
import numpy as np

G = 9.81
KARMAN = 0.4
RHO_A = 1.225
RHO_TUPROQ = 2650.0
D_S = 100e-6             # saltatsiyalanuvchi zarrachalarning xarakterli diametri, m
C_ALPHA = 1.0e-2         # kalibrlash koeffitsiyenti (2.12)


# ---------------------------------------------------------------
# Kritik dinamik tezlik va tuzatmalar
# ---------------------------------------------------------------
def kritik_tezlik(d=D_S, rho_p=RHO_TUPROQ, rho_a=RHO_A, A_N=0.0123, gamma=3.0e-4):
    """Quruq, silliq va o'simliksiz sirt uchun u*t0, m/s  —  (2.3)."""
    return np.sqrt(A_N * (rho_p * G * d / rho_a + gamma / (rho_a * d)))


def namlik_tuzatmasi(w, gil_foiz):
    """Fecan tuzatmasi f_w  —  (2.5)-(2.6).

    w        — tuproqning gravimetrik namligi, %
    gil_foiz — loy (gil) zarrachalari ulushi, %
    """
    w = np.asarray(w, dtype=float)
    cl = np.asarray(gil_foiz, dtype=float)
    w_prime = 0.0014 * cl ** 2 + 0.17 * cl
    dw = np.clip(w - w_prime, 0.0, None)
    return np.where(w > w_prime, np.sqrt(1.0 + 1.21 * dw ** 0.68), 1.0)


def gadir_tuzatmasi(z0r, d_s=D_S):
    """Marticorena-Bergametti tuzatmasi f_r  —  (2.7).

    z0r — eroziyalanuvchi sirtning g'adir-budurlik parametri, m
          (aerodinamik z0 bilan aralashtirilmaydi); None -> silliq sirt, f_r = 1.
    z0s = d_s/30 — silliq sirt parametri.
    Samarali ulush f_eff <= 0 bo'lgan nuqtalarda eroziya bo'lmaydi (f_r = inf).
    """
    if z0r is None:
        return 1.0
    z0r_sm = np.asarray(z0r, dtype=float) * 100.0
    z0s_sm = d_s * 100.0 / 30.0
    f_eff = 1.0 - np.log(np.maximum(z0r_sm, z0s_sm) / z0s_sm) / np.log(0.35 * (10.0 / z0s_sm) ** 0.8)
    return np.where(f_eff > 1e-6, 1.0 / np.maximum(f_eff, 1e-6), np.inf)


def qoplam_ulushi(lam):
    """Frontal maydon indeksidan o'simlik qoplami ulushi: lambda = -0.35 ln(1 - C_v)."""
    return 1.0 - np.exp(-np.asarray(lam, dtype=float) / 0.35)


def qoplam_tuzatmasi(Cv, m_r=0.5, beta_r=90.0, sigma_r=1.0):
    """Raupach tuzatmasi f_v  —  (2.8)-(2.9),  lambda = -0.35 ln(1 - C_v)."""
    Cv = np.clip(np.asarray(Cv, dtype=float), 0.0, 0.99)
    lam = -0.35 * np.log(1.0 - Cv)
    num = (1.0 - m_r * sigma_r * lam) * (1.0 + m_r * beta_r * lam)
    return np.where(num > 1e-12, np.sqrt(np.maximum(num, 1e-12)), np.inf)


def samarali_kritik_tezlik(w, gil_foiz, Cv, z0r=None, d_s=D_S):
    """u*t = u*t0(d_s) f_w f_r f_v  —  (2.4)."""
    return (kritik_tezlik(d_s) * namlik_tuzatmasi(w, gil_foiz)
            * gadir_tuzatmasi(z0r, d_s) * qoplam_tuzatmasi(Cv))


# ---------------------------------------------------------------
# Dinamik tezlik va oqimlar
# ---------------------------------------------------------------
def dinamik_tezlik(U10, z0, z_ref=10.0):
    """Logarifmik profildan u*, m/s  —  (2.1)."""
    return KARMAN * np.asarray(U10, dtype=float) / np.log(z_ref / np.asarray(z0, dtype=float))


def gorizontal_oqim(u_star, u_star_t, rho_a=RHO_A, c=2.61):
    """White formulasi bo'yicha saltatsiya oqimi Q, kg/(m s)  —  (2.10)."""
    us = np.asarray(u_star, dtype=float)
    ut = np.broadcast_to(np.asarray(u_star_t, dtype=float), us.shape)
    Q = np.zeros_like(us)
    m = us > ut
    if np.any(m):
        r = ut[m] / us[m]
        Q[m] = c * rho_a / G * us[m] ** 3 * (1.0 + r) * (1.0 - r ** 2)
    return Q


def sandblast_koeffitsiyenti(gil_foiz):
    """alpha = 100 * 10^(0.134 %clay - 6), 1/m  —  (2.11); loy ulushi 20 % gacha."""
    cl = np.clip(np.asarray(gil_foiz, dtype=float), 0.0, 20.0)
    return 100.0 * 10.0 ** (0.134 * cl - 6.0)


def vertikal_oqim(Q, gil_foiz, Cv, C_alpha=C_ALPHA, A_ef=1.0):
    """F_e = C_alpha alpha Q (1 - C_v), kg/(m^2 s)  —  (2.12).

    A_ef — yacheykadagi eroziyalanuvchi yuza ulushi (yer qoplami xaritasidan).
    """
    return C_alpha * sandblast_koeffitsiyenti(gil_foiz) * Q * (1.0 - np.asarray(Cv)) * A_ef


# ---------------------------------------------------------------
# Fraksiyalar bo'yicha taqsimot
# ---------------------------------------------------------------
def fraksiya_ulushlari(chegaralar, D_mod=(1.5e-6, 6.7e-6, 45.0e-6),
                       sigma=(1.7, 1.6, 1.5), ulush=(0.05, 0.40, 0.55)):
    """Uch modali lognormal taqsimot bo'yicha massa ulushlari p_i  —  (2.25).

    Standart beshta fraksiya uchun: 0.049, 0.327, 0.088, 0.327, 0.208.
    """
    from math import erf, log, sqrt
    ch = np.asarray(chegaralar, dtype=float)
    p = np.zeros(len(ch) - 1)
    for Dm, sg, wj in zip(D_mod, sigma, ulush):
        lnsg = np.log(sg)
        cdf = np.array([0.5 * (1.0 + erf((log(max(c, 1e-12)) - log(Dm)) / (sqrt(2.0) * lnsg)))
                        for c in ch])
        p += wj * np.diff(cdf)
    s = p.sum()
    return p / s if s > 0 else p


def emissiya_maydoni(U10, z0, w, m_cl, lam, A_ef, fraksiyalar=None, chegaralar=None,
                     Cv=None, z0r=None, C_alpha=C_ALPHA, d_s=D_S, ulushlar=None):
    """Barcha fraksiyalar uchun emissiya oqimi F_e,i, kg/(m^2 s)  —  (2.12), (2.25).

    m_cl — loy ulushi (0..1); lam — o'simlik frontal maydon indeksi;
    Cv berilmasa lam dan hisoblanadi. Qaytaradi: (F, info), F shakli (Nf, N+1, M+1).
    """
    gil = 100.0 * np.asarray(m_cl, dtype=float)
    if Cv is None:
        Cv = qoplam_ulushi(lam)
    u_star = dinamik_tezlik(U10, z0)
    ut = samarali_kritik_tezlik(w, gil, Cv, z0r, d_s)
    Q = gorizontal_oqim(u_star, ut)
    F_tot = vertikal_oqim(Q, gil, Cv, C_alpha, A_ef)
    p = np.asarray(ulushlar) if ulushlar is not None else fraksiya_ulushlari(chegaralar)
    return F_tot[None, :, :] * p[:, None, None], dict(
        u_star=u_star, u_star_t=ut, Q=Q, F_tot=F_tot, ulushlar=p, Cv=np.asarray(Cv))
