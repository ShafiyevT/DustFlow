# -*- coding: utf-8 -*-
"""Hisoblash stsenariylarini sozlash moduli."""
import json
from dataclasses import dataclass, asdict, field


@dataclass
class Stsenariy:
    """Bitta hisoblash stsenariysining to'liq tavsifi."""
    nom: str = "buxoro_standart"
    # soha va to'r
    Lx: float = 380e3
    Ly: float = 390e3
    Hz: float = 5000.0
    N: int = 60
    M: int = 60
    L: int = 30
    beta_s: float = 8.0            # vertikal to'rni yer sirti yaqinida quyuqlashtirish
    relyef: str = "buxoro"
    # meteorologiya
    U10: float = 12.0
    yonalish: float = 40.0
    mavsum: str = "yoz"
    harorat: float = 293.15
    # hisoblash
    T: float = 12 * 3600.0
    dt: float = 120.0
    sxema: str = "aniq"            # "aniq" (III bob, 2-tartib) yoki "tezkor" (II bob, 1-tartib)
    qarshilik: str = "re"          # "re" — f(Re), "stoks" — Stoks qonuni
    sigma: float = 1e-6
    C_alpha: float = 1e-2          # emissiya kalibrlash koeffitsiyenti (2.12)
    K_h: float = 1.0e3             # gorizontal diffuziya koeffitsiyenti, m2/s
    h_s: float = 100.0             # yer usti qatlami balandligi (2.23)-(2.24), m
    h_0: float = 10.0              # (2.24) dagi masshtab parametri, m
    w_dt: float = 1.0e-3           # (2.22) dagi turbulent cho'kish tezligi, m/s
    xi_z: float = 1.0e-4           # yuqori chegaradagi almashinuv koeffitsiyenti, m/s
    # fraksiyalar
    chegaralar: list = field(default_factory=lambda:
                             [0.2e-6, 2.5e-6, 10e-6, 20e-6, 50e-6, 100e-6])
    # chiqish
    surat_qadam: int = 30          # necha qadamda bir surat saqlanadi
    baza: str = "dustflow.db"

    def saqla(self, yol):
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    @classmethod
    def yukla(cls, yol):
        with open(yol, encoding="utf-8") as f:
            d = json.load(f)
        d.pop("cheklovchi", None)          # 1.x versiya kalitlari
        return cls(**d)

    def model_parametrlari(self):
        """Model konstruktoriga uzatiladigan parametrlar."""
        return dict(sigma=self.sigma, sxema=self.sxema, qarshilik=self.qarshilik,
                    C_alpha=self.C_alpha, K_h=self.K_h, h_s=self.h_s, h_0=self.h_0,
                    w_dt=self.w_dt, xi_z=self.xi_z)

    def kalit(self):
        """Bazada qidirish uchun parametrlar to'plami."""
        d = asdict(self)
        d.pop("nom"); d.pop("baza"); d.pop("surat_qadam")
        return d
