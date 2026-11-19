# -*- coding: utf-8 -*-
"""Kirish ma'lumotlarini tayyorlash moduli.

Turli manbalardan olinadigan maydonlarni yagona hisoblash to'riga keltiradi.
Haqiqiy ma'lumotlar (ERA5-Land, SMAP, MODIS, SRTM) NetCDF/GeoTIFF ko'rinishida
o'qiladi; mazkur modulda ular uchun yagona interfeys hamda sinov uchun
namunaviy maydonlarni yaratuvchi funksiyalar keltirilgan.
"""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class KirishMaydonlari:
    """Hisoblash uchun zarur barcha maydonlar."""
    U10: np.ndarray        # shamol tezligi 10 m da, m/s
    yonalish: np.ndarray   # shamol yo'nalishi, gradus
    w: np.ndarray          # tuproq namligi, %
    m_cl: np.ndarray       # gil ulushi, 0..1
    lam: np.ndarray        # o'simlik qoplami zichligi
    z0: np.ndarray         # g'adir-budurlik uzunligi, m
    A_ef: np.ndarray       # eroziyaga beriluvchan yuza ulushi
    eta: np.ndarray        # relyef, m
    manba: dict = field(default_factory=dict)
    Cv: np.ndarray = None  # o'simlik qoplami ulushi (berilmasa lam dan: lam = -0.35 ln(1-Cv))
    z0r: np.ndarray = None # eroziyalanuvchi sirt g'adir-budurligi, m (berilmasa f_r = 1)
    z0_shamol: np.ndarray = None  # ko'chish uchun shamol profili va K_z dagi g'adir-budurlik
                                  # (berilmasa z0); lokal manbalar uchun fon qiymati beriladi

    def tekshir(self):
        """Maydonlarning fizik chegaralarini tekshiradi."""
        xat = []
        if np.any(self.U10 < 0):        xat.append("U10 < 0")
        if np.any(self.w < 0):          xat.append("namlik < 0")
        if np.any(self.m_cl < 0) or np.any(self.m_cl > 1):
            xat.append("gil ulushi [0,1] dan tashqarida")
        if np.any(self.lam < 0):        xat.append("qoplam zichligi < 0")
        if np.any(self.z0 <= 0):        xat.append("z0 <= 0")
        if np.any(self.A_ef < 0) or np.any(self.A_ef > 1):
            xat.append("A_ef [0,1] dan tashqarida")
        return xat


def interpolyatsiya(manba_x, manba_y, manba_qiymat, tor):
    """Manba to'ridan hisoblash to'riga ikki chiziqli interpolyatsiya."""
    from numpy import interp
    oraliq = np.empty((len(manba_y), len(tor.x)))
    for j in range(len(manba_y)):
        oraliq[j] = interp(tor.x, manba_x, manba_qiymat[:, j] if
                           manba_qiymat.shape[0] == len(manba_x) else manba_qiymat[j])
    natija = np.empty((len(tor.x), len(tor.y)))
    for i in range(len(tor.x)):
        natija[i] = interp(tor.y, manba_y, oraliq[:, i])
    return natija


def buxoro_maydonlari(tor, U10_qiymat=9.0, yonalish=45.0, mavsum="yoz"):
    """Buxoro viloyati uchun namunaviy kirish maydonlari.

    Hudud ikki qismdan iborat: shimoli-g'arbda Qizilqum choli (quruq,
    yalang), janubi-sharqda Zarafshon vohasi (nam, o'simlik qoplami zich).
    """
    X, Y = np.meshgrid(tor.x / tor.Lx, tor.y / tor.Ly, indexing="ij")

    # voha ko'rsatkichi: janubi-sharqda 1 ga yaqin
    voha = 1.0 / (1.0 + np.exp(-12.0 * ((X + 0.75 * (1 - Y)) - 1.05)))

    if mavsum == "yoz":
        w_chol, w_voha = 0.6, 14.0
        lam_chol, lam_voha = 0.004, 0.09
    else:
        w_chol, w_voha = 3.5, 18.0
        lam_chol, lam_voha = 0.010, 0.05

    w = w_chol + (w_voha - w_chol) * voha
    lam = lam_chol + (lam_voha - lam_chol) * voha
    m_cl = 0.04 + 0.12 * voha
    z0 = 1.0e-4 + (2.0e-2 - 1.0e-4) * voha
    # eroziyaga beriluvchan yuza ulushi: choʻlning katta qismi qatqaloq,
    # taqir va shagʻal qoplami bilan band, shu sababli 0.25 dan oshmaydi
    A_ef = 0.25 * (1.0 - voha) + 0.02

    U10 = np.full_like(X, U10_qiymat) * (1.0 - 0.25 * voha)
    yon = np.full_like(X, yonalish)

    from .grid import relyef_yarat
    eta = tor.eta if tor.eta is not None else relyef_yarat(tor)

    return KirishMaydonlari(
        U10=U10, yonalish=yon, w=w, m_cl=m_cl, lam=lam,
        z0=z0, A_ef=A_ef, eta=eta,
        manba={"U10": "ERA5 / O'zgidromet", "w": "ERA5-Land, SMAP",
               "m_cl": "SoilGrids", "lam": "MODIS NDVI/LAI",
               "z0": "MODIS Land Cover", "A_ef": "MODIS Land Cover",
               "eta": "SRTM 30 m"})


def _puasson_neyman(f, dx, dy):
    """Lap(psi) = f, dpsi/dn = 0 (tugunli to'r, besh nuqtali Laplas operatori, DCT-I)."""
    from scipy.fft import dctn, idctn
    N, M = f.shape
    k = np.arange(N); l = np.arange(M)
    lam = ((2 * np.cos(np.pi * k / (N - 1)) - 2) / dx ** 2)[:, None] + \
          ((2 * np.cos(np.pi * l / (M - 1)) - 2) / dy ** 2)[None, :]
    fh = dctn(f - f.mean(), type=1)
    lam[0, 0] = 1.0
    ph = fh / lam; ph[0, 0] = 0.0
    return idctn(ph, type=1)


def _divergensiya(tor, He, U, V):
    return np.gradient(He * U, tor.dx, axis=0) + np.gradient(He * V, tor.dy, axis=1)


def shamol_maydoni(tor, kirish, h_s=100.0, massa_moslash=False):
    """Uch o'lchovli shamol maydoni.

    Gorizontal tashkil etuvchilar — logarifmik profil (2.23), h_s dan yuqorida
    o'zgarmas:  U(z) = u*/kappa ln((min(z, h_s) + z0)/z0),  z — yer sirtidan balandlik.
    Vertikal tashkil etuvchi relyefga moslashgan koordinatalarda uzluksizlik
    tenglamasidan topiladi:
        d(He u)/dx + d(He v)/dy + d(He omega)/ds = 0,   omega(s=0) = 0,
    so'ngra (3.12) dan  w = He omega + (1 - s)(u d eta/dx + v d eta/dy).

    Standart holatda (massa_moslash=False) vertikal tezlik yer sirtidan yuqoriga
    integrallanadi va yuqori chegara orqali havo oqimiga ruxsat beriladi; bu
    uzluksizlik tenglamasini aniq qanoatlantiradi va advektiv shakldagi sxemada
    massa balansini saqlaydi.
    massa_moslash=True (tajriba uchun): ustun bo'yicha integral divergensiya
    potensial tuzatma -grad(psi), Lap(psi) = D_ustun, bilan kamaytiriladi va
    yuqori chegarada omega(1) = 0 qilinadi. (2.23) profilda u* gorizontal
    bo'yicha kuchli o'zgarganda tuzatma katta bo'lishi mumkin.
    """
    from .emission import dinamik_tezlik, KARMAN
    He = tor.He[:, :, None]
    s = tor.s[None, None, :]
    w_s = tor.s_ogirligi()[None, None, :]
    z = He * s                                           # yer sirtidan balandlik
    z0_2d = kirish.z0 if getattr(kirish, "z0_shamol", None) is None else kirish.z0_shamol
    z0 = z0_2d[:, :, None]
    us = dinamik_tezlik(kirish.U10, z0_2d)[:, :, None]
    Uz = us / KARMAN * np.log((np.minimum(z, h_s) + z0) / z0)
    ang = np.deg2rad(kirish.yonalish)[:, :, None]
    U = Uz * np.cos(ang)
    V = Uz * np.sin(ang)
    if massa_moslash:
        for _ in range(2):
            D = np.sum(_divergensiya(tor, He, U, V) * w_s, axis=2)          # ustun integrali, m/s
            psi = _puasson_neyman(D, tor.dx, tor.dy)
            Qx = -np.gradient(psi, tor.dx, axis=0); Qy = -np.gradient(psi, tor.dy, axis=1)
            wgt = Uz / np.maximum(np.sum(Uz * w_s, axis=2, keepdims=True), 1e-12)   # int wgt ds = 1
            U = U + Qx[:, :, None] * wgt / He
            V = V + Qy[:, :, None] * wgt / He
    div = _divergensiya(tor, He, U, V)
    He_om = np.zeros_like(U)
    He_om[:, :, 1:] = -np.cumsum(0.5 * (div[:, :, 1:] + div[:, :, :-1]) * tor.hs, axis=2)
    if massa_moslash:
        He_om -= s * He_om[:, :, -1:]              # qolgan kichik nomuvofiqlik (sonli)
    d_eta_dx = np.gradient(tor.eta, tor.dx, axis=0)[:, :, None]
    d_eta_dy = np.gradient(tor.eta, tor.dy, axis=1)[:, :, None]
    W = He_om + (1.0 - s) * (U * d_eta_dx + V * d_eta_dy)
    return U, V, W


def diffuziya_koeffitsiyentlari(tor, kirish, u_star, h_s=100.0, h_0=10.0, K_h=1.0e3):
    """K_x = K_y = K_h va K_z = kappa u* (min(z, h_s) + h_0)  —  (2.24).

    z — yer sirtidan balandlik; h_0 — sirt yaqinidagi turbulent almashinuv masshtabi.
    """
    z = tor.He[:, :, None] * tor.s[None, None, :]
    Kz = 0.4 * np.asarray(u_star)[:, :, None] * (np.minimum(z, h_s) + h_0)
    Kz = np.maximum(Kz, 0.1)
    return K_h, K_h, Kz
