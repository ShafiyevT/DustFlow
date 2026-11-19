# -*- coding: utf-8 -*-
"""Ko'chish va diffuziya masalasining sonli yechuvchisi.

Tenglama relyefga moslashgan koordinatalarda (3.9)-(3.12), advektiv shaklda:

  dth/dt + v_x dth/dx + v_y dth/dy + omega dth/ds
      = (1/He) d/dx(He K_x dth/dx) + (1/He) d/dy(He K_y dth/dy)
        + (1/He^2) d/ds(K_z dth/ds) - sigma th + f,

  omega He = v_z - (1 - s)(v_x d eta/dx + v_y d eta/dy)                       (3.12)

Chegaraviy shartlar (2.16)-(2.21), (3.8):
  -K_x dth/dx |x=0  = xi (th_E - th),     K_x dth/dx |x=Lx = xi (th_E - th),
  -K_y dth/dy |y=0  = xi (th_E - th),     K_y dth/dy |y=Ly = xi (th_E - th),
  -K_z dth/dz |z=eta = F_e,i - w_d,i th,  K_z dth/dz |z=Hz = xi_z (th_E - th),
  w_d,i = w_s,i + w_dt.
Chegaraviy shartlar uch nuqtali bir tomonlama formulalar (ikkinchi tartib) bilan
aproksimatsiyalanadi va progonka koeffitsiyentlari alpha_0, beta_0 hamda
th_N formulalari orqali hisobga olinadi.

Fazoviy operator (3.37):  Lambda_d th_i = A_i th_{i-1} - (A_i + C_i) th_i + C_i th_{i+1},
  A_i = K_{i-1/2}/h^2 + v_i^+/h,   C_i = K_{i+1/2}/h^2 - v_i^-/h.

Ikki rejim:

  sxema="tezkor"  — II bob, § 2.3: fazoviy yo'nalishlar bo'yicha ajratish
      (Ox -> Oy -> Oz), har bir bosqich to'liq Delta_tau bilan, oshkormas,
      sigma/3 va f/3; vaqt bo'yicha birinchi tartib.

  sxema="aniq"    — III bob, § 3.3: makroqadam uch kichik qadamga bo'linadi:
      n -> n+1/3 simmetrik oshkormas sxema (Krank-Nikolson), gamma = Delta_tau/6,
      n+1/3 -> n+2/3 va n+2/3 -> n+1 ikkinchi tartibli uch qatlamli oshkormas
      sxema (BDF2), gamma = 2 Delta_tau/9. Har bir kichik qadamdagi uch
      o'lchovli tenglama  th - gamma Lambda th = F  fazoviy yo'nalishlar bo'yicha
      ajratishga asoslangan iteratsiya (3.43) bilan yechiladi:
        th^(m+1/3) - gamma Lam1 th^(m+1/3) = F + gamma (Lam2 + Lam3 - sigma) th^(m)
        th^(m+2/3) - gamma Lam2 th^(m+2/3) = th^(m+1/3) - gamma Lam2 th^(m)
        th^(m+1)   - gamma (Lam3 - sigma) th^(m+1) = th^(m+2/3) - gamma (Lam3 - sigma) th^(m)
      vaqt bo'yicha ikkinchi tartib.
"""
import numpy as np


def uch_nuqta(h1, h2):
    """Chegaradagi hosila uchun uch nuqtali bir tomonlama formula koeffitsiyentlari.

    y'(x_0) ~ p0 y_0 + p1 y_1 + p2 y_2,  h1 = x_1 - x_0, h2 = x_2 - x_1.
    Tekis to'rda (h1 = h2 = h):  p = (-3, 4, -1)/(2h).
    """
    p0 = -(2 * h1 + h2) / (h1 * (h1 + h2))
    p1 = (h1 + h2) / (h1 * h2)
    p2 = -h1 / (h2 * (h1 + h2))
    return p0, p1, p2


def progonka(a, b, c, d, chap, ong):
    """Uch nuqtali chegaraviy shartli progonka.

    Ichki tugunlarda:  a_i y_{i-1} - b_i y_i + c_i y_{i+1} = -d_i,  i = 1..n-1.
    chap = (K, xi, g, p0, p1, p2):   K (p0 y_0 + p1 y_1 + p2 y_2)            = xi y_0 - g,
    ong  = (K, xi, g, q0, q1, q2):  -K (q0 y_n + q1 y_{n-1} + q2 y_{n-2})    = xi y_n - g,
    bu yerda p, q — uch nuqtali formulaning koeffitsiyentlari (uch_nuqta).
    Tekis to'rda p = (-3, 4, -1)/(2h), q = (3, -4, 1)/(2h) va formulalar
      alpha_0 = K(4c_1 - b_1)/(3Kc_1 - Ka_1 + 2h xi c_1),
      beta_0  = (K d_1 + 2h c_1 g)/(3Kc_1 - Ka_1 + 2h xi c_1),
      y_n = (2h g + K(4beta_{n-1} - beta_{n-2} - alpha_{n-2}beta_{n-1}))
            / (3K + 2h xi + K alpha_{n-2}alpha_{n-1} - 4K alpha_{n-1})
    ko'rinishga keladi. Massivlar shakli (n+1, P); qolganlari skalyar yoki (P,).
    """
    n = a.shape[0] - 1
    al = np.zeros_like(b); be = np.zeros_like(b)
    K0, xi0, g0, p0, p1, p2 = chap
    den = K0 * p0 * c[1] - K0 * p2 * a[1] - xi0 * c[1]
    al[0] = -K0 * (p1 * c[1] + p2 * b[1]) / den
    be[0] = (K0 * p2 * d[1] - g0 * c[1]) / den
    for i in range(1, n):
        z = b[i] - a[i] * al[i - 1]
        al[i] = c[i] / z
        be[i] = (a[i] * be[i - 1] + d[i]) / z
    K1, xi1, g1, q0, q1, q2 = ong
    y = np.empty_like(b)
    num = g1 - K1 * (q1 * be[n - 1] + q2 * (al[n - 2] * be[n - 1] + be[n - 2]))
    den = xi1 + K1 * (q0 + q1 * al[n - 1] + q2 * al[n - 2] * al[n - 1])
    y[n] = num / den
    for i in range(n - 1, -1, -1):
        y[i] = al[i] * y[i + 1] + be[i]
    return y


class Yechuvchi:
    """Ko'chish-diffuziya masalasi uchun bitta fraksiya yechuvchisi."""

    def __init__(self, tor, Kx, Ky, Kz, sigma=0.0, sxema="aniq", xi=1e-3, xi_z=1e-4,
                 th_E=0.0, eps=1e-6, smax=30, manfiy_kesish=True, cheklovchi=None):
        if sxema not in ("aniq", "tezkor"):
            raise ValueError("sxema: 'aniq' yoki 'tezkor'")
        self.tor = tor
        self.Kx, self.Ky = float(Kx), float(Ky)
        L = tor.L + 1
        self.Kz = (np.asarray(Kz, dtype=float) if np.ndim(Kz) == 3
                   else np.full(tor.shakl, float(Kz)))
        self.sigma = sigma
        self.sxema = sxema
        self.xi, self.xi_z = xi, xi_z
        self.th_E = th_E
        self.eps, self.smax = eps, smax
        self.manfiy_kesish = manfiy_kesish
        self.iteratsiyalar = []
        self._F2 = np.zeros((tor.N + 1, tor.M + 1)); self._wd = 0.0
        # metrik kattaliklar
        He = tor.He
        self._He = He[:, :, None]
        self._Hx_m = np.empty_like(He); self._Hx_p = np.empty_like(He)
        Hfx = 0.5 * (He[1:] + He[:-1])
        self._Hx_m[1:] = Hfx / He[1:]; self._Hx_m[0] = 1.0
        self._Hx_p[:-1] = Hfx / He[:-1]; self._Hx_p[-1] = 1.0
        self._Hy_m = np.empty_like(He); self._Hy_p = np.empty_like(He)
        Hfy = 0.5 * (He[:, 1:] + He[:, :-1])
        self._Hy_m[:, 1:] = Hfy / He[:, 1:]; self._Hy_m[:, 0] = 1.0
        self._Hy_p[:, :-1] = Hfy / He[:, :-1]; self._Hy_p[:, -1] = 1.0
        self._hz = He[:, :, None] * tor.hs[None, None, :]        # (N+1, M+1, L) qatlam qalinligi
        self._eta_x = np.gradient(tor.eta, tor.dx, axis=0)[:, :, None]
        self._eta_y = np.gradient(tor.eta, tor.dy, axis=1)[:, :, None]
        Kh = np.empty_like(self.Kz)
        Kh[:, :, 1:] = 0.5 * (self.Kz[:, :, 1:] + self.Kz[:, :, :-1])
        self._Kz_m = Kh                                          # K_{k-1/2} (k>=1)
        self._Kz_p = np.empty_like(self.Kz)
        self._Kz_p[:, :, :-1] = Kh[:, :, 1:]                     # K_{k+1/2}

    # ------------------------------------------------------------------
    def koeffitsiyentlar(self, vx, vy, vz):
        """A^d, C^d koeffitsiyentlari (3.37) va s bo'yicha tezlik (3.12)."""
        t = self.tor
        s = t.s[None, None, :]
        Wp = vz - (1.0 - s) * (vx * self._eta_x + vy * self._eta_y)     # He*omega, m/s
        self.Wp = Wp
        dx2, dy2 = t.dx ** 2, t.dy ** 2
        self.Ax = self.Kx * self._Hx_m[:, :, None] / dx2 + np.maximum(vx, 0) / t.dx
        self.Cx = self.Kx * self._Hx_p[:, :, None] / dx2 - np.minimum(vx, 0) / t.dx
        self.Ay = self.Ky * self._Hy_m[:, :, None] / dy2 + np.maximum(vy, 0) / t.dy
        self.Cy = self.Ky * self._Hy_p[:, :, None] / dy2 - np.minimum(vy, 0) / t.dy
        # notekis vertikal to'r: h_m = z_k - z_{k-1}, h_p = z_{k+1} - z_k
        hm = np.empty_like(Wp); hp = np.empty_like(Wp)
        hm[:, :, 1:] = self._hz; hm[:, :, 0] = self._hz[:, :, 0]
        hp[:, :, :-1] = self._hz; hp[:, :, -1] = self._hz[:, :, -1]
        hb = 0.5 * (hm + hp)
        self.Az = self._Kz_m / (hb * hm) + np.maximum(Wp, 0) / hb
        self.Cz = self._Kz_p / (hb * hp) - np.minimum(Wp, 0) / hb
        self.vx, self.vy = vx, vy

    def _Lam(self, th, ax):
        """Lambda_ax th ichki tugunlarda (ax bo'yicha chegaraviy tugunlarda 0)."""
        A, C = [(self.Ax, self.Cx), (self.Ay, self.Cy), (self.Az, self.Cz)][ax]
        T = np.moveaxis(th, ax, 0); A = np.moveaxis(A, ax, 0); C = np.moveaxis(C, ax, 0)
        r = np.zeros_like(T)
        r[1:-1] = A[1:-1] * T[:-2] - (A[1:-1] + C[1:-1]) * T[1:-1] + C[1:-1] * T[2:]
        return np.moveaxis(r, 0, ax)

    def _thE(self, kalit, shakl):
        e = self.th_E
        a = np.asarray(e.get(kalit, 0.0) if isinstance(e, dict) else e, dtype=float)
        if a.ndim == 2 and a.shape != tuple(shakl):
            a = a[1:-1, 1:-1]                    # to'liq yuza berilgan, ichki qismi olinadi
        return np.broadcast_to(a, shakl)

    def _sweep(self, ax, b0, rhs, out, sigma_b=0.0):
        """ax yo'nalishi bo'yicha progonka: ichki tugunlarda
        (b0 + A + C + sigma_b) th_i - A th_{i-1} - C th_{i+1} = rhs_i,
        chekkalarda chegaraviy shartlar. Natija out ning ichki chiziqlariga yoziladi."""
        A, C = [(self.Ax, self.Cx), (self.Ay, self.Cy), (self.Az, self.Cz)][ax]
        Ao = np.moveaxis(A, ax, 0); Co = np.moveaxis(C, ax, 0); Ro = np.moveaxis(rhs, ax, 0)
        sl = (slice(None), slice(1, -1), slice(1, -1))
        Ao, Co, Ro = Ao[sl], Co[sl], Ro[sl]
        n1 = Ao.shape[0]; P = Ao.shape[1] * Ao.shape[2]
        a = Ao.reshape(n1, P); c = Co.reshape(n1, P); d = Ro.reshape(n1, P)
        b = a + c + b0 + sigma_b
        t = self.tor
        if ax < 2:
            h = t.dx if ax == 0 else t.dy
            K = self.Kx if ax == 0 else self.Ky
            p = uch_nuqta(h, h); q = tuple(-v for v in p)
            sh = (t.M - 1, t.L - 1) if ax == 0 else (t.N - 1, t.L - 1)
            k0, k1 = ("x0", "x1") if ax == 0 else ("y0", "y1")
            chap = (K, self.xi, self.xi * self._thE(k0, sh).reshape(P)) + p
            ong = (K, self.xi, self.xi * self._thE(k1, sh).reshape(P)) + q
        else:
            hz = self._hz[1:-1, 1:-1]
            p = uch_nuqta(hz[..., 0].reshape(P), hz[..., 1].reshape(P))
            q = tuple(-v for v in uch_nuqta(hz[..., -1].reshape(P), hz[..., -2].reshape(P)))
            chap = (self.Kz[1:-1, 1:-1, 0].reshape(P), self._wd, self._F) + p
            ong = (self.Kz[1:-1, 1:-1, -1].reshape(P), self.xi_z,
                   self.xi_z * self._thE("z1", (t.N - 1, t.M - 1)).reshape(P)) + q
        y = progonka(a, b, c, d, chap, ong)
        Oo = np.moveaxis(out, ax, 0)
        Oo[sl] = y.reshape(Ao.shape)

    @staticmethod
    def _qirralar(t):
        """Ikki chegaraviy tekislik kesishgan qirralardagi tugunlar qo'shnisidan olinadi."""
        t[0, 0, :] = t[1, 1, :]; t[0, -1, :] = t[1, -2, :]
        t[-1, 0, :] = t[-2, 1, :]; t[-1, -1, :] = t[-2, -2, :]
        t[0, :, 0] = t[1, :, 0]; t[-1, :, 0] = t[-2, :, 0]
        t[:, 0, 0] = t[:, 1, 0]; t[:, -1, 0] = t[:, -2, 0]
        t[0, :, -1] = t[1, :, -1]; t[-1, :, -1] = t[-2, :, -1]
        t[:, 0, -1] = t[:, 1, -1]; t[:, -1, -1] = t[:, -2, -1]

    # ------------------------------------------------------------------
    def _tezkor(self, C, dt, f):
        """II bob: Ox, Oy, Oz bosqichlari, har biri to'liq dt, sigma/3, f/3."""
        th = C.copy()
        f3 = 0.0 if f is None else f / 3.0
        for ax in range(3):
            rhs = th / dt + f3
            self._sweep(ax, 1.0 / dt, rhs, th, sigma_b=self.sigma / 3.0)
        self._qirralar(th)
        return th, [(1.0, th)]

    def _douglas(self, gamma, F, guess):
        """th - gamma Lambda th = F  ni (3.43) iteratsiya bilan yechadi."""
        thm = guess.copy(); self._qirralar(thm)
        sg = self.sigma
        for m in range(1, self.smax + 1):
            L2 = self._Lam(thm, 1); L3 = self._Lam(thm, 2)
            ta = thm.copy()
            self._sweep(0, 1.0 / gamma, F / gamma + L2 + L3 - sg * thm, ta)
            tb = ta.copy()
            self._sweep(1, 1.0 / gamma, ta / gamma - L2, tb)
            tc = tb.copy()
            self._sweep(2, 1.0 / gamma, tb / gamma - L3 + sg * thm, tc, sigma_b=sg)
            self._qirralar(tc)
            dl = np.max(np.abs(tc - thm)); mx = np.max(np.abs(tc))
            thm = tc
            if dl <= self.eps * max(mx, 1e-300):
                break
        self.iteratsiyalar.append(m)
        return thm

    def chegara_tuzat(self, th):
        """Chegaraviy tugunlarni chegaraviy shartlardan (uch nuqtali formula) aniqlaydi.

        Simmetrik sxemaning oshkor qismi chegaraviy shartlarni qanoatlantiruvchi
        holatga qo'llanishi kerak (majburlash yangilanganda yoki boshlang'ich
        holat ixtiyoriy berilganda)."""
        t = self.tor
        for ax, h, K, (k0, k1) in ((0, t.dx, self.Kx, ("x0", "x1")), (1, t.dy, self.Ky, ("y0", "y1"))):
            T = np.moveaxis(th, ax, 0)
            p0, p1, p2 = uch_nuqta(h, h)
            E0 = self._thE(k0, T[0].shape); E1 = self._thE(k1, T[-1].shape)
            T[0] = (K * p1 * T[1] + K * p2 * T[2] + self.xi * E0) / (self.xi - K * p0)
            T[-1] = (self.xi * E1 + K * p1 * T[-2] + K * p2 * T[-3]) / (self.xi - K * p0)
        hz = self._hz
        p0, p1, p2 = uch_nuqta(hz[..., 0], hz[..., 1])
        K0 = self.Kz[:, :, 0]
        th[:, :, 0] = (K0 * p1 * th[:, :, 1] + K0 * p2 * th[:, :, 2] + self._F2) / (self._wd - K0 * p0)
        q0, q1, q2 = uch_nuqta(hz[..., -1], hz[..., -2])
        KL = self.Kz[:, :, -1]
        E = self._thE("z1", th[:, :, -1].shape)
        th[:, :, -1] = (self.xi_z * E + KL * q1 * th[:, :, -2] + KL * q2 * th[:, :, -3]) / (self.xi_z - KL * q0)
        self._qirralar(th)
        return th

    def _aniq(self, C, dt, f):
        """III bob: n -> n+1/3 (KN), n+2/3, n+1 (BDF2)."""
        f_ = 0.0 if f is None else f
        C = self.chegara_tuzat(C.copy())
        g1 = dt / 6.0
        LC = self._Lam(C, 0) + self._Lam(C, 1) + self._Lam(C, 2) - self.sigma * C
        th1 = self._douglas(g1, C + g1 * LC + 2.0 * g1 * f_, C)
        g2 = 2.0 * dt / 9.0
        th2 = self._douglas(g2, (4.0 * th1 - C) / 3.0 + g2 * f_, np.maximum(2.0 * th1 - C, 0.0))
        th3 = self._douglas(g2, (4.0 * th2 - th1) / 3.0 + g2 * f_, np.maximum(2.0 * th2 - th1, 0.0))
        # oqimlarni hisoblash uchun kichik qadamlar: (og'irlik, holat)
        return th3, [(0.5 / 3.0, C), (0.5 / 3.0, th1), (1.0 / 3.0, th2), (1.0 / 3.0, th3)]

    # ------------------------------------------------------------------
    def qadam(self, C, vx, vy, vz, dt, F_yuza=None, w_d=0.0, f=None):
        """Bitta makroqadam. C, vx, vy, vz — (N+1, M+1, L+1); F_yuza — (N+1, M+1);
        w_d — quruq cho'kish tezligi w_s + w_dt, m/s."""
        t = self.tor
        self.koeffitsiyentlar(vx, vy, vz)
        F = np.zeros((t.N + 1, t.M + 1)) if F_yuza is None else np.asarray(F_yuza, dtype=float)
        self._F = F[1:-1, 1:-1].reshape(-1)
        self._F2 = F
        self._wd = w_d
        Cn, holatlar = (self._tezkor if self.sxema == "tezkor" else self._aniq)(C, dt, f)
        self._oqimlar(holatlar, dt, F, w_d)
        manfiy = np.minimum(Cn, 0.0)
        self.kesilgan_massa = float(np.sum(-manfiy * t.yacheyka_hajmi()))
        return Cn - manfiy if self.manfiy_kesish else Cn

    def _oqimlar(self, holatlar, dt, F, w_d):
        """Chegaralar orqali oqimlar (massa balansi uchun), kg.

        Yon va yuqori chegaralarda oqim chegaraviy tugun va unga qo'shni ichki
        tugun orasidagi yuzadan, sxemaning o'zi bilan moslashgan ko'rinishda
        (upwind advektiv + diffuzion) olinadi; quyi chegarada F_e va w_d th.
        holatlar — [(og'irlik, th), ...], og'irliklar yig'indisi 1."""
        t = self.tor
        wy = t._trap(t.M) * t.dy; wx = t._trap(t.N) * t.dx
        ws = t.s_ogirligi()
        He = t.He
        S = t.yuza_ogirligi()
        # quyi chegaraviy shart faqat ichki ustunlarda qo'llaniladi (chetki ustunlar
        # yon chegaraviy shartlardan aniqlanadi), shuning uchun emissiya va cho'kish
        # ichki ustunlar bo'yicha yig'iladi
        Si = np.zeros_like(S); Si[1:-1, 1:-1] = S[1:-1, 1:-1]
        vxp, vxm = np.maximum(self.vx, 0), np.minimum(self.vx, 0)
        vyp, vym = np.maximum(self.vy, 0), np.minimum(self.vy, 0)
        Wpp, Wpm = np.maximum(self.Wp, 0), np.minimum(self.Wp, 0)
        Ax = He[0][:, None] * ws[None, :] * wy[:, None]           # x yuzalari maydoni
        Ax1 = He[-1][:, None] * ws[None, :] * wy[:, None]
        Ay0 = He[:, 0][:, None] * ws[None, :] * wx[:, None]
        Ay1 = He[:, -1][:, None] * ws[None, :] * wx[:, None]
        chok = 0.0; chiq = 0.0
        self.chokish_oqimi = np.zeros((t.N + 1, t.M + 1))
        for w, th in holatlar:
            # quyi chegara: (3.8) dagi w_d th_0 va advektiv tenglamadagi cho'kish
            # hadining 0- va 1-tugunlar orasidagi yuzadan o'tuvchi oqimi
            dep = w_d * th[:, :, 0] - (Wpp[:, :, 1] * th[:, :, 0] + Wpm[:, :, 1] * th[:, :, 1])
            self.chokish_oqimi += w * dep
            chok += w * float(np.sum(dep * Si))
            q = 0.0
            # x = 0: 0 va 1 tugunlar orasidagi yuza (tashqariga musbat)
            q += np.sum((-(vxp[1] * th[0] + vxm[1] * th[1]) - self.Kx * (th[1] - th[0]) / t.dx) * Ax)
            q += np.sum(((vxp[-2] * th[-2] + vxm[-2] * th[-1]) + self.Kx * (th[-2] - th[-1]) / t.dx) * Ax1)
            q += np.sum((-(vyp[:, 1] * th[:, 0] + vym[:, 1] * th[:, 1])
                         - self.Ky * (th[:, 1] - th[:, 0]) / t.dy) * Ay0)
            q += np.sum(((vyp[:, -2] * th[:, -2] + vym[:, -2] * th[:, -1])
                         + self.Ky * (th[:, -2] - th[:, -1]) / t.dy) * Ay1)
            hz = self._hz[:, :, -1]
            q += np.sum(((Wpp[:, :, -2] * th[:, :, -2] + Wpm[:, :, -2] * th[:, :, -1])
                         + self._Kz_p[:, :, -2] * (th[:, :, -2] - th[:, :, -1]) / hz) * S)
            chiq += w * float(q)
        self.chokish = chok * dt
        self.chiqish = chiq * dt
        self.emissiya = float(np.sum(F * Si)) * dt
