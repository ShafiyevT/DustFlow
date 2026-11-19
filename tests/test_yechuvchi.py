# -*- coding: utf-8 -*-
"""DustFlow 2.0 testlari: emissiya sxemasi, cho'kish tezligi va yechuvchi."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dustflow.grid import Tor, relyef_yarat
from dustflow.solver import Yechuvchi, progonka, uch_nuqta
from dustflow import emission as E
from dustflow.velocity import chokish_tezligi, stoks_tezligi, TezlikMaydoni
from dustflow.model import STANDART_CHEGARALAR, FRAKSIYA_ZICHLIGI

SXEMALAR = ("tezkor", "aniq")


def _tor(relyefli=True, L=12, beta_s=4.0):
    t = Tor(Lx=1e5, Ly=1e5, Hz=2000.0, N=12, M=12, L=L, beta_s=beta_s)
    if relyefli:
        t.eta = relyef_yarat(t, amplituda=300.0); t.He = t.Hz - t.eta
    return t


# ------------------------------------------------------------------ emissiya
def test_emissiya_formulalari():
    assert abs(E.kritik_tezlik(100e-6) - 0.237) < 2e-3                 # (2.3), 2.1-rasm
    assert abs(E.sandblast_koeffitsiyenti(10.0) - 100 * 10 ** (1.34 - 6)) < 1e-12   # (2.11)
    assert float(E.namlik_tuzatmasi(1.0, 10.0)) == 1.0                  # w < w'
    assert float(E.namlik_tuzatmasi(6.0, 10.0)) > 1.0
    assert abs(float(E.qoplam_tuzatmasi(0.0)) - 1.0) < 1e-12
    assert E.gadir_tuzatmasi(None) == 1.0
    p = E.fraksiya_ulushlari(STANDART_CHEGARALAR)
    assert np.allclose(p, [0.049, 0.327, 0.088, 0.327, 0.208], atol=1e-3)   # (2.25)


def test_emissiya_chiziqliligi():
    """F_e ~ C_alpha (1 - C_v); kritik tezlikdan pastda F_e = 0."""
    a = lambda x: np.array([[x]])
    F1, _ = E.emissiya_maydoni(a(15.0), a(1e-4), a(1.0), a(0.1), a(0.0), a(1.0),
                               chegaralar=STANDART_CHEGARALAR, C_alpha=1e-2)
    F2, _ = E.emissiya_maydoni(a(15.0), a(1e-4), a(1.0), a(0.1), a(0.0), a(1.0),
                               chegaralar=STANDART_CHEGARALAR, C_alpha=2e-2)
    assert abs(F2.sum() / F1.sum() - 2.0) < 1e-12
    F0, _ = E.emissiya_maydoni(a(4.0), a(1e-4), a(1.0), a(0.1), a(0.0), a(1.0),
                               chegaralar=STANDART_CHEGARALAR)
    assert F0.sum() == 0.0


# ------------------------------------------------------------------ tezliklar
def test_chokish_tezliklari():
    """(3.6) yechimi; Stoks qonuni 50-100 mkm uchun ~17 % ga oshirib baholaydi."""
    d = [np.sqrt(STANDART_CHEGARALAR[i] * STANDART_CHEGARALAR[i + 1]) for i in range(5)]
    kut = [2.26e-5, 1.504e-3, 1.315e-2, 6.945e-2, 0.3253]
    for di, r, w in zip(d, FRAKSIYA_ZICHLIGI, kut):
        assert abs(chokish_tezligi(di, r) - w) / w < 3e-3
    farq = 1 - chokish_tezligi(d[4], 2600.0) / stoks_tezligi(d[4], 2600.0)
    assert 0.16 < farq < 0.18


def test_tezlik_maydoni_muvozanat():
    """Katta makroqadamda zarracha tezligi v = u, v_z = w - w_s ga intiladi (L-turg'unlik)."""
    sh = (4, 4, 4)
    U = np.full(sh, 12.0); V = np.full(sh, 3.0); W = np.zeros(sh)
    tm = TezlikMaydoni(70.7e-6, 2600.0)
    tm.v = [np.zeros(sh), np.zeros(sh), np.zeros(sh)]
    for _ in range(3):
        vx, vy, vz = tm.qadam(U, V, W, 120.0)
    assert np.allclose(vx, 12.0) and np.allclose(vy, 3.0)
    assert np.allclose(vz, -tm.w_s, rtol=1e-8)
    assert max(tm.iteratsiyalar) < 50


# ------------------------------------------------------------------ progonka
def test_progonka_tekis_tor_formulalari():
    """Umumiy formulalar tekis to'rda dissertatsiyadagi alpha_0, beta_0, y_N ga teng."""
    rng = np.random.default_rng(1)
    n, h = 10, 0.3
    a = rng.uniform(1, 2, (n + 1, 1)); c = rng.uniform(1, 2, (n + 1, 1))
    b = a + c + 3.0; d = rng.uniform(-1, 1, (n + 1, 1))
    K, xi, g = 2.0, 0.7, 0.4
    p = uch_nuqta(h, h); q = tuple(-v for v in p)
    y = progonka(a, b, c, d, (K, xi, g) + p, (K, xi, g) + q)
    al0 = K * (4 * c[1] - b[1]) / (3 * K * c[1] - K * a[1] + 2 * h * xi * c[1])
    be0 = (K * d[1] + 2 * h * c[1] * g) / (3 * K * c[1] - K * a[1] + 2 * h * xi * c[1])
    assert abs(y[0, 0] - (al0 * y[1, 0] + be0)) < 1e-12
    assert abs(K * (-3 * y[0] + 4 * y[1] - y[2]) / (2 * h) - (xi * y[0] - g)) < 1e-12
    assert abs(-K * (y[-3] - 4 * y[-2] + 3 * y[-1]) / (2 * h) - (xi * y[-1] - g)) < 1e-12


# ------------------------------------------------------------------ yechuvchi
def test_statik_holat():
    t = _tor(); Z = np.zeros(t.shakl)
    for sx in SXEMALAR:
        y = Yechuvchi(t, 1e3, 1e3, 10.0, sigma=0.0, sxema=sx, xi=1e-3, xi_z=1e-4, th_E=1.0)
        C = np.ones(t.shakl)
        for _ in range(10):
            C = y.qadam(C, Z, Z, Z, 120.0)
        assert np.max(np.abs(C - 1.0)) < 1e-9, sx


def test_massa_saqlanishi():
    """Yopiq sohada (xi = xi_z = 0, w_d = 0) massa saqlanadi."""
    t = _tor(); Z = np.zeros(t.shakl); dV = t.yacheyka_hajmi()
    for sx in SXEMALAR:
        y = Yechuvchi(t, 1e3, 1e3, 10.0, sigma=0.0, sxema=sx, xi=0.0, xi_z=0.0)
        C = np.zeros(t.shakl); C[4:8, 4:8, 4:8] = 1.0
        C = y.chegara_tuzat(C); Q0 = float((C * dV).sum())
        for _ in range(20):
            C = y.qadam(C, Z, Z, Z, 120.0)
        assert abs(float((C * dV).sum()) / Q0 - 1.0) < 1e-3, sx


def test_emissiya_massasi():
    """Yer sirtidan kiritilgan massa sohada to'planadi."""
    t = _tor(relyefli=False, L=20, beta_s=5.0); Z = np.zeros(t.shakl); dV = t.yacheyka_hajmi()
    # chetki ustunlar yon chegaraviy shartdan aniqlanadi, massa ichki ustunlar bo'yicha olinadi
    dV[0] = dV[-1] = 0.0; dV[:, 0] = dV[:, -1] = 0.0
    F = np.full((t.N + 1, t.M + 1), 1e-6)
    for sx in SXEMALAR:
        y = Yechuvchi(t, 1e3, 1e3, 10.0, sigma=0.0, sxema=sx, xi=0.0, xi_z=0.0)
        C = np.zeros(t.shakl); em = 0.0
        for _ in range(20):
            C = y.qadam(C, Z, Z, Z, 120.0, F_yuza=F); em += y.emissiya
        assert abs(float((C * dV).sum()) / em - 1.0) < 0.02, sx


def test_balans_chokish_va_oqib_chiqish():
    """Cho'kish, advektiv oqib chiqish va massa yig'indisi emissiyaga teng."""
    t = _tor(relyefli=False, L=20, beta_s=5.0); dV = t.yacheyka_hajmi()
    U = np.full(t.shakl, 8.0); V = np.full(t.shakl, 3.0); W = np.full(t.shakl, -0.07)
    F = np.zeros((t.N + 1, t.M + 1)); F[3:9, 3:9] = 1e-6
    for sx in SXEMALAR:
        y = Yechuvchi(t, 1e3, 1e3, 10.0, sigma=0.0, sxema=sx, xi=11.0, xi_z=1e-4)
        C = np.zeros(t.shakl); em = dep = out = 0.0
        for _ in range(30):
            C = y.qadam(C, U, V, W, 120.0, F_yuza=F, w_d=0.071)
            em += y.emissiya; dep += y.chokish; out += y.chiqish
        Q = float((C * dV).sum())
        assert abs(em - dep - out - Q) / em < 0.02, sx


def test_yutilish():
    t = _tor(relyefli=False); Z = np.zeros(t.shakl)
    sig = 1e-4
    for sx, tol in (("tezkor", 3e-3), ("aniq", 1e-6)):
        y = Yechuvchi(t, 10.0, 10.0, 1.0, sigma=sig, sxema=sx, xi=0.0, xi_z=0.0)
        C = np.ones(t.shakl); T, dt = 3600.0, 120.0
        for _ in range(int(T / dt)):
            C = y.qadam(C, Z, Z, Z, dt)
        assert abs(C[5, 5, 5] - np.exp(-sig * T)) < tol, (sx, C[5, 5, 5])


def test_vaqt_boyicha_tartib():
    """aniq — ikkinchi, tezkor — birinchi tartib (silliq boshlang'ich holat)."""
    t = Tor(Lx=2e4, Ly=2e4, Hz=500.0, N=20, M=20, L=10)
    X, Y, Zc = np.meshgrid(t.x, t.y, t.s * t.Hz, indexing="ij")
    C0 = np.exp(-((X - 8e3) ** 2 + (Y - 1e4) ** 2) / 3e3 ** 2 - (Zc - 200) ** 2 / 150 ** 2)
    U = np.full(t.shakl, 5.0); Z = np.zeros(t.shakl); T = 960.0

    def yech(sx, dt):
        y = Yechuvchi(t, 2e3, 2e3, 20.0, sigma=1e-4, sxema=sx, xi=0.0, xi_z=0.0, eps=1e-10,
                      manfiy_kesish=False)
        C = y.chegara_tuzat(C0.copy())
        for _ in range(int(round(T / dt))):
            C = y.qadam(C, U, Z, Z, dt)
        return C

    ref = yech("aniq", 7.5)
    for sx, p_min, p_max in (("aniq", 1.7, 2.4), ("tezkor", 0.8, 1.2)):
        e = [np.max(np.abs(yech(sx, dt) - ref)) for dt in (120.0, 60.0)]
        p = np.log2(e[0] / e[1])
        assert p_min < p < p_max, (sx, p)


def test_monotonlik_tezkor():
    t = _tor(relyefli=False); Z = np.zeros(t.shakl)
    U = np.full(t.shakl, 10.0)
    y = Yechuvchi(t, 10.0, 10.0, 1.0, sigma=0.0, sxema="tezkor", xi=10.0, xi_z=0.0,
                  manfiy_kesish=False)
    C = np.zeros(t.shakl); C[3:5, 4:8, 3:6] = 1.0
    for _ in range(30):
        C = y.qadam(C, U, Z, Z, 200.0)
    # ichki tugunlarda sxema monoton; chegaraviy tugunlarda uch nuqtali formula
    # juda kichik manfiy qiymat berishi mumkin
    assert C[1:-1, 1:-1, 1:-1].min() >= -1e-12
    assert C.min() >= -1e-5 * C.max()


if __name__ == "__main__":
    for nm, f in sorted(globals().items()):
        if nm.startswith("test_"):
            f(); print(f"  OK  {nm}")
    print("Barcha testlar muvaffaqiyatli o'tdi.")
