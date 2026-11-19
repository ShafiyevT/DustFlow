# -*- coding: utf-8 -*-
"""DustFlow — hisoblash jarayonini boshqaruvchi modul."""
import time
import logging
import numpy as np

log = logging.getLogger("dustflow")

from .grid import Tor, relyef_yarat
from .data import (buxoro_maydonlari, shamol_maydoni,
                   diffuziya_koeffitsiyentlari, KirishMaydonlari)
from .emission import emissiya_maydoni, dinamik_tezlik, C_ALPHA
from .velocity import (relaksatsiya_vaqti, chokish_tezligi, stoks_tezligi,
                       TezlikMaydoni)
from .solver import Yechuvchi
from .balance import Balans

STANDART_CHEGARALAR = [0.2e-6, 2.5e-6, 10.0e-6, 20.0e-6, 50.0e-6, 100.0e-6]
FRAKSIYA_NOMLARI = ["0.2-2.5 um (PM2.5)", "2.5-10 um (PM10)", "10-20 um",
                    "20-50 um", "50-100 um"]
FRAKSIYA_ZICHLIGI = [1500.0, 2000.0, 2200.0, 2400.0, 2600.0]


class Model:
    """Shamol eroziyasi va chang tarqalishining to'liq modeli.

    sxema     : "aniq"   — III bob, vaqt bo'yicha ikkinchi tartib (standart);
                "tezkor" — II bob, vaqt bo'yicha birinchi tartib.
    qarshilik : "re"     — f(Re) = 1 + 0.15 Re^0.687 (III bob, standart);
                "stoks"  — Stoks qonuni (II bob).
    """

    def __init__(self, tor: Tor, kirish: KirishMaydonlari,
                 chegaralar=None, sigma=1e-6, xi=None, Cb=0.0,
                 sxema="aniq", qarshilik="re", C_alpha=C_ALPHA,
                 K_h=1.0e3, h_s=100.0, h_0=10.0, w_dt=1.0e-3, xi_z=1.0e-4,
                 eps=1e-6, smax=30, cheklovchi=None):
        self.tor = tor
        self.kirish = kirish
        self.xi = xi
        self._xi_avto = xi is None      # None: xi har bir majburlashda shamoldan olinadi
        self.Cb = Cb
        self.chegaralar = chegaralar or STANDART_CHEGARALAR
        self.Nf = len(self.chegaralar) - 1
        self.sigma = sigma
        self.sxema = sxema
        self.qarshilik = qarshilik
        self.C_alpha = C_alpha
        self.K_h, self.h_s, self.h_0 = K_h, h_s, h_0
        self.w_dt, self.xi_z = w_dt, xi_z
        self.eps, self.smax = eps, smax
        self._tayyorla()

    # ----------------------------------------------------------
    def _tayyorla(self):
        t = self.tor
        self.d_ort = np.array([np.sqrt(self.chegaralar[i] * self.chegaralar[i + 1])
                               for i in range(self.Nf)])
        if self.Nf == len(FRAKSIYA_ZICHLIGI):
            self.rho_p = np.array(FRAKSIYA_ZICHLIGI)
        else:
            self.rho_p = np.interp(self.d_ort, [0.71e-6, 5e-6, 14.1e-6, 31.6e-6, 70.7e-6],
                                   FRAKSIYA_ZICHLIGI)
        self.tau = relaksatsiya_vaqti(self.d_ort, self.rho_p)
        self.w_g = stoks_tezligi(self.d_ort, self.rho_p)
        self.v_t = np.array([chokish_tezligi(d, r, qarshilik=self.qarshilik)
                             for d, r in zip(self.d_ort, self.rho_p)])
        self.w_d = self.v_t + self.w_dt                  # (2.22), (3.8)
        self.tezliklar = [TezlikMaydoni(d, r, qarshilik=self.qarshilik)
                          for d, r in zip(self.d_ort, self.rho_p)]
        self._havo_oldingi = None
        self._majburlash()
        self.C = np.zeros((self.Nf,) + t.shakl)
        # yer sirtiga to'plangan chang massasi, kg/m2 (fraksiyalar kesimida)
        self.chokindi = np.zeros((self.Nf, t.N + 1, t.M + 1))
        self.balans = [Balans(t) for _ in range(self.Nf)]
        self.vaqt = 0.0
        self.kesilgan = 0.0
        self.tarix = []
        self.iteratsiyalar = []

    # ----------------------------------------------------------
    def _majburlash(self):
        """Meteorologik majburlashga bog'liq maydonlarni hisoblaydi."""
        t, k = self.tor, self.kirish
        self.U, self.V, self.W = shamol_maydoni(t, k, h_s=self.h_s)
        z0_sh = k.z0 if getattr(k, "z0_shamol", None) is None else k.z0_shamol
        self.u_star = dinamik_tezlik(k.U10, z0_sh)          # ko'chish va diffuziya uchun
        self.Kx, self.Ky, self.Kz = diffuziya_koeffitsiyentlari(
            t, k, self.u_star, h_s=self.h_s, h_0=self.h_0, K_h=self.K_h)
        self.F, self.emis_info = emissiya_maydoni(
            k.U10, k.z0, k.w, k.m_cl, k.lam, k.A_ef, None, self.chegaralar,
            Cv=getattr(k, "Cv", None), z0r=getattr(k, "z0r", None), C_alpha=self.C_alpha)
        # orqaga moslik uchun nom: quruq cho'kish tezligi
        self.beta_dep = self.w_d
        # yon chegaralardagi almashinuv koeffitsiyenti: erkin chiqish uchun
        # xi ~ xarakterli shamol tezligi, (2.16)-(2.17)
        if self._xi_avto:
            self.xi = float(np.mean(np.abs(self.U)) + np.mean(np.abs(self.V)))

    def majburlash_yangila(self, kirish):
        """Vaqt boʻyicha oʻzgaruvchan majburlash: yangi kirish maydonlarini qabul qiladi.

        Konsentratsiya, choʻkindi, massa balansi va vaqt SAQLANADI — hisoblash
        uzluksiz davom etadi, faqat shamol, diffuziya, emissiya va choʻkish
        tezligi yangilanadi.
        """
        self.kirish = kirish
        self._majburlash()

    # ----------------------------------------------------------
    def qadam(self, dt):
        """Bitta makroqadam — barcha fraksiyalar uchun."""
        t = self.tor
        havo_old = self._havo_oldingi
        for i in range(self.Nf):
            vx, vy, vz = self.tezliklar[i].qadam(self.U, self.V, self.W, dt, U_old=havo_old)
            yech = Yechuvchi(t, self.Kx, self.Ky, self.Kz, sigma=self.sigma,
                             sxema=self.sxema, xi=self.xi, xi_z=self.xi_z,
                             th_E=self.Cb[i] if isinstance(self.Cb, (list, tuple)) else self.Cb,
                             eps=self.eps, smax=self.smax)
            self.C[i] = yech.qadam(self.C[i], vx, vy, vz, dt,
                                   F_yuza=self.F[i], w_d=self.w_d[i])
            b = self.balans[i]
            b.Q_em += yech.emissiya
            b.Q_cho += yech.chokish
            b.Q_chiq += yech.chiqish
            b.yutilish_qosh(self.C[i], self.sigma, dt)
            self.chokindi[i] += yech.chokish_oqimi * dt
            self.kesilgan += getattr(yech, "kesilgan_massa", 0.0)
            self.iteratsiyalar.extend(yech.iteratsiyalar)
        self._havo_oldingi = (self.U, self.V, self.W)
        self.vaqt += dt

    # ----------------------------------------------------------
    def ishga_tushir(self, T, dt, hisobot_qadam=None, jim=False,
                     baza=None, seans_id=None, surat_qadam=None):
        """T soniya davomida hisoblash.

        baza berilgan bo'lsa, vaqt qatorlari va suratlar bazaga yoziladi.
        """
        n = int(round(T / dt))
        hisobot_qadam = hisobot_qadam or max(1, n // 6)
        log.info("hisoblash boshlandi: %d qadam, dt=%.1f s", n, dt)
        t0 = time.perf_counter()
        for k in range(n):
            self.qadam(dt)
            if baza and seans_id and surat_qadam and (k + 1) % surat_qadam == 0:
                baza.surat_yozish(seans_id, self.vaqt, self.C.sum(axis=0))
            if (k + 1) % hisobot_qadam == 0 or k == n - 1:
                Q = [b.yozib_bor(self.vaqt, self.C[i])
                     for i, b in enumerate(self.balans)]
                yuza = self.yuza_konsentratsiya()
                b = self.massa_balansi()
                self.tarix.append(dict(t=self.vaqt, Q=sum(Q),
                                       C_max=float(yuza.max())))
                if baza and seans_id:
                    baza.qator_yozish(seans_id, self.vaqt, Q=b["Q"],
                                      Q_em=b["Q_em"], Q_cho=b["Q_cho"],
                                      Q_chiq=b["Q_chiq"], Q_yut=b["Q_yut"],
                                      C_max=float(yuza.max()),
                                      C_ort=float(yuza.mean()),
                                      nomuvofiqlik=b["nisbiy"])
                if not jim:
                    print(f"  t = {self.vaqt/3600:5.2f} soat   "
                          f"umumiy massa = {sum(Q):.4e} kg   "
                          f"C_max (yuza) = {yuza.max()*1e9:8.2f} mkg/m3")
        self.hisoblash_vaqti = time.perf_counter() - t0
        log.info("hisoblash yakunlandi: %.1f s", self.hisoblash_vaqti)
        if baza and seans_id:
            baza.seans_yopish(seans_id, self.hisoblash_vaqti)
        return self

    def davom_ettir(self, baza, seans_id, T, dt, **kw):
        """Uzilgan hisoblashni bazadagi oxirgi suratdan davom ettiradi."""
        t_oxirgi, C_yig = baza.oxirgi_surat(seans_id)
        if t_oxirgi is None:
            log.warning("surat topilmadi, noldan boshlanadi")
            return self.ishga_tushir(T, dt, baza=baza, seans_id=seans_id, **kw)
        ulush = self.emis_info["ulushlar"]
        for i in range(self.Nf):
            self.C[i] = C_yig * ulush[i]
        self.vaqt = t_oxirgi
        log.info("hisoblash %.1f soatdan davom ettirilmoqda", t_oxirgi / 3600)
        return self.ishga_tushir(T - t_oxirgi, dt, baza=baza,
                                 seans_id=seans_id, **kw)

    # ----------------------------------------------------------
    def yuza_konsentratsiya(self, fraksiya=None):
        """Yer sirtiga yaqin qatlamdagi umumiy konsentratsiya, kg/m3."""
        if fraksiya is None:
            return self.C[:, :, :, 0].sum(axis=0)
        return self.C[fraksiya, :, :, 0]

    def vertikal_profil(self, i=None, j=None):
        """Berilgan nuqtadagi vertikal profil."""
        i = i if i is not None else self.tor.N // 2
        j = j if j is not None else self.tor.M // 2
        z = self.tor.balandlik()[i, j, :]
        return z, self.C[:, i, j, :]

    def chokindi_qalinligi(self, rho_yotqizik=1400.0):
        """Cho'kindi qatlamining qalinligi, mm.

        rho_yotqizik — erkin yotqizilgan changning hajmiy zichligi, kg/m3.
        """
        return self.chokindi.sum(axis=0) / rho_yotqizik * 1000.0

    def masofa_boyicha_chokindi(self, manba_ij, yonalish_deg, n_bin=40, R=None):
        """Manbadan masofa bo'yicha cho'kindi taqsimoti.

        Qaytaradi: (masofa_km, qalinlik_mm, massa_kg_m2)
        """
        t = self.tor
        i0, j0 = manba_ij
        X, Y = np.meshgrid(t.x, t.y, indexing="ij")
        dx_ = X - t.x[i0]; dy_ = Y - t.y[j0]
        ang = np.deg2rad(yonalish_deg)
        # shamol yo'nalishi bo'yicha proyeksiya
        s_ = dx_ * np.cos(ang) + dy_ * np.sin(ang)
        R = R or float(s_.max())
        chegara = np.linspace(0.0, R, n_bin + 1)
        qal = self.chokindi_qalinligi()
        mas = self.chokindi.sum(axis=0)
        ind = np.digitize(s_, chegara) - 1
        mk, qk, mm = [], [], []
        for b in range(n_bin):
            m_ = (ind == b) & (s_ >= 0)
            if m_.sum() == 0:
                continue
            mk.append(0.5 * (chegara[b] + chegara[b + 1]) / 1000.0)
            qk.append(float(qal[m_].mean()))
            mm.append(float(mas[m_].mean()))
        return np.array(mk), np.array(qk), np.array(mm)

    def massa_balansi(self):
        """Barcha fraksiyalar bo'yicha balans ma'lumoti."""
        Q = sum(b.massa(self.C[i]) for i, b in enumerate(self.balans))
        em = sum(b.Q_em for b in self.balans)
        cho = sum(b.Q_cho for b in self.balans)
        yut = sum(b.Q_yut for b in self.balans)
        chiq = sum(b.Q_chiq for b in self.balans)
        qol = em - cho - yut - chiq + self.kesilgan - Q
        return dict(Q=Q, Q_em=em, Q_cho=cho, Q_yut=yut, Q_chiq=chiq,
                    kesilgan=self.kesilgan, qoldiq=qol,
                    nisbiy=abs(qol) / max(em, 1e-30) * 100.0)
