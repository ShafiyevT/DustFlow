# -*- coding: utf-8 -*-
"""DustFlow — grafik foydalanuvchi interfeysi."""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons

from .grid import Tor, relyef_yarat
from .data import buxoro_maydonlari
from .model import Model
from .db import Baza
from .config import Stsenariy
from .io_geo import stsenariy_yukla, stsenariylar_royxati
from . import __version__

KM = 1e-3


class Oyna:
    """DustFlow asosiy ish oynasi."""

    def __init__(self, baza_yoli="dustflow.db", stsenariy_katalogi="stsenariylar"):
        plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
        self.baza = Baza(baza_yoli)
        self.model = None
        self.stsenariylar = stsenariylar_royxati(stsenariy_katalogi)
        self.stsenariy = Stsenariy(N=40, M=40, L=15, T=6 * 3600)

        self.fig = plt.figure(figsize=(14.6, 8.4))
        self.fig.canvas.manager.set_window_title(
            f"DustFlow {__version__} — chang tarqalishini bashoratlash")
        self.fig.patch.set_facecolor("#f4f6f8")

        # ---- sarlavha ----
        self.fig.text(0.011, 0.965, "DustFlow", fontsize=18,
                      fontweight="bold", color="#14507d")
        self.fig.text(0.011, 0.938,
                      "Shamol eroziyasi va atmosferaning changlanishini bashoratlash majmuasi",
                      fontsize=9.5, color="#333")
        self.fig.text(0.011, 0.918, "Buxoro davlat universiteti",
                      fontsize=8.5, color="#666", style="italic")
        self.fig.patches.append(plt.Rectangle(
            (0, 0.908), 1, 0.003, transform=self.fig.transFigure,
            color="#14507d", zorder=0.5))

        # ---- boshqaruv paneli ----
        self.fig.patches.append(plt.Rectangle(
            (0.007, 0.018), 0.213, 0.876, transform=self.fig.transFigure,
            facecolor="white", edgecolor="#c8d2da", zorder=0))

        self.fig.text(0.017, 0.874, "STSENARIY", fontsize=9,
                      fontweight="bold", color="#14507d")
        ns = max(1, len(self.stsenariylar))
        self.s_st = Slider(self._ax([0.052, 0.846, 0.148, 0.015]),
                           "№", 1, ns, valinit=1, valstep=1, valfmt="%d",
                           color="#c0392b")
        self.st_nom = self.fig.text(0.017, 0.822, "", fontsize=8.4,
                                    color="#263238", fontweight="bold")
        self.st_tav = self.fig.text(0.017, 0.806, "", fontsize=7.0, color="#607d8b")
        self.st_san = self.fig.text(0.017, 0.792, "", fontsize=7.0, color="#607d8b")
        ax_qo = self._ax([0.026, 0.756, 0.176, 0.026])
        ax_qo.set_facecolor("#fbfcfd")
        self.chk_st = CheckButtons(ax_qo, ["stsenariy maʼlumotlari"], [True])
        self.s_st.on_changed(lambda v: self._stsenariy_korsat())

        self.fig.text(0.017, 0.730, "QOʻLDA BERISH", fontsize=9,
                      fontweight="bold", color="#14507d")
        self.s_u = Slider(self._ax([0.052, 0.700, 0.148, 0.015]),
                          "$U_{10}$, m/s", 3.0, 25.0, valinit=12.0,
                          valfmt="%.1f", color="#1f6fb2")
        self.s_dir = Slider(self._ax([0.052, 0.664, 0.148, 0.015]),
                            "yoʻnalish, °", 0.0, 360.0, valinit=40.0,
                            valfmt="%.0f", color="#2c7a4b")

        self.fig.text(0.017, 0.636, "HISOBLASH", fontsize=9,
                      fontweight="bold", color="#14507d")
        self.s_T = Slider(self._ax([0.052, 0.606, 0.148, 0.015]),
                          "davri, soat", 1.0, 48.0, valinit=6.0,
                          valfmt="%.0f", color="#d77a3a")
        self.s_dt = Slider(self._ax([0.052, 0.570, 0.148, 0.015]),
                           "$\\Delta t$, s", 30.0, 600.0, valinit=120.0,
                           valfmt="%.0f", color="#8e44ad")
        self.s_N = Slider(self._ax([0.052, 0.534, 0.148, 0.015]),
                          "toʻr $N$", 20, 80, valinit=40, valfmt="%.0f",
                          color="#607d8b")

        self.fig.text(0.017, 0.506, "SOZLAMALAR", fontsize=9,
                      fontweight="bold", color="#14507d")
        ax_ch = self._ax([0.026, 0.424, 0.176, 0.074])
        ax_ch.set_facecolor("#fbfcfd")
        self.chk = CheckButtons(ax_ch, ["aniq sxema (2-tartib)", "bazaga yozish",
                                        "yozgi mavsum"], [True, True, True])

        self.fig.text(0.017, 0.396, "KOʻRINISH", fontsize=9,
                      fontweight="bold", color="#14507d")
        ax_rb = self._ax([0.026, 0.288, 0.176, 0.100])
        ax_rb.set_facecolor("#fbfcfd")
        self.rb = RadioButtons(ax_rb, ["Konsentratsiya", "Emissiya",
                                       "Kirish maydonlari", "Balans"], active=0)

        self.b_hisob = Button(self._ax([0.026, 0.238, 0.084, 0.032]),
                              "Hisoblash", color="#1f6fb2", hovercolor="#155a92")
        self.b_hisob.label.set_color("white"); self.b_hisob.label.set_fontweight("bold")
        self.b_eksport = Button(self._ax([0.118, 0.238, 0.084, 0.032]),
                                "Eksport", color="#e8eef3", hovercolor="#d3dde5")

        self.fig.text(0.017, 0.196, "NATIJALAR", fontsize=9,
                      fontweight="bold", color="#14507d")
        self.txt = self.fig.text(0.019, 0.186, "", fontsize=6.0, va="top",
                                 family="DejaVu Sans Mono", color="#222")

        # ---- grafik maydonlari ----
        self.ax_main = self.fig.add_axes([0.275, 0.335, 0.385, 0.545])
        self.ax_prof = self.fig.add_axes([0.715, 0.605, 0.255, 0.275])
        self.ax_frak = self.fig.add_axes([0.715, 0.335, 0.255, 0.200])
        self.ax_bal = self.fig.add_axes([0.275, 0.075, 0.695, 0.195])
        self.cb = None

        self.status = self.fig.text(0.275, 0.022, "tayyor", fontsize=8.5,
                                    color="#2c7a4b")

        self.b_hisob.on_clicked(self.hisobla)
        self.b_eksport.on_clicked(self.eksport)
        self.rb.on_clicked(lambda l: self._chiz())

        self._stsenariy_korsat()
        self._bosh_holat()

    # ------------------------------------------------------------------
    def _ax(self, rect, z=3):
        a = self.fig.add_axes(rect)
        a.set_zorder(z)
        return a

    def _stsenariy_korsat(self):
        if not self.stsenariylar:
            self.st_nom.set_text("(stsenariylar topilmadi)")
            return
        r = self.stsenariylar[int(self.s_st.val) - 1]
        self.st_nom.set_text(r["nom"][:32])
        t = r["tavsif"]
        self.st_tav.set_text(t[:46] + ("…" if len(t) > 46 else ""))
        self.st_san.set_text(f"{r['sana']}  ·  {r['mavsum']}  ·  {r['id']}")
        self.fig.canvas.draw_idle()

    def _bosh_holat(self):
        for a in (self.ax_main, self.ax_prof, self.ax_frak, self.ax_bal):
            a.clear(); a.set_xticks([]); a.set_yticks([])
        self.ax_main.text(0.5, 0.5, "Hisoblash uchun «Hisoblash» tugmasini bosing",
                          ha="center", va="center", fontsize=11, color="#90a4ae",
                          transform=self.ax_main.transAxes)
        self._seanslar()

    def _seanslar(self):
        r = self.baza.seanslar_royxati(6)
        s = [f"{'BAZADAGI SEANSLAR':<34}", "-" * 34]
        if not r:
            s.append("  (bo'sh)")
        for z in r:
            v = f"{z['hisob_vaqti']:.0f}s" if z["hisob_vaqti"] else "—"
            s.append(f"{z['id']:>3} {z['nom'][:16]:<16} {z['holat'][:8]:<8}{v:>6}")
        self.txt.set_text("\n".join(s))

    # ------------------------------------------------------------------
    def hisobla(self, event):
        st = self.stsenariy
        st.U10 = self.s_u.val
        st.yonalish = self.s_dir.val
        st.T = self.s_T.val * 3600.0
        st.dt = self.s_dt.val
        st.N = st.M = int(self.s_N.val)
        st.L = max(st.L, 30)
        aniq, bazaga, yoz = self.chk.get_status()
        st.sxema = "aniq" if aniq else "tezkor"
        st.mavsum = "yoz" if yoz else "qish"

        kalit = st.kalit()
        if self.chk_st.get_status()[0] and self.stsenariylar:
            kalit["stsenariy"] = self.stsenariylar[int(self.s_st.val) - 1]["id"]
        self._kalit = kalit
        mavjud = self.baza.seans_bormi(kalit)
        if mavjud:
            self.status.set_text(
                f"Xuddi shu parametrlar bilan hisoblash bajarilgan "
                f"(seans {mavjud['id']}, {mavjud['hisob_vaqti']:.0f} s). "
                f"Natijalar bazadan olindi.")

        self.status.set_text("hisoblanmoqda...")
        self.fig.canvas.draw_idle()

        t = Tor(Lx=st.Lx, Ly=st.Ly, Hz=st.Hz, N=st.N, M=st.M, L=st.L, beta_s=st.beta_s)
        if self.chk_st.get_status()[0] and self.stsenariylar:
            r = self.stsenariylar[int(self.s_st.val) - 1]
            k, _tav = stsenariy_yukla(r["yol"], t)
            t.eta = k.eta; t.He = t.Hz - t.eta
            st.nom = r["id"]
        else:
            t.eta = relyef_yarat(t); t.He = t.Hz - t.eta
            k = buxoro_maydonlari(t, U10_qiymat=st.U10, yonalish=st.yonalish,
                                  mavsum=st.mavsum)
            st.nom = "qolda"
        self.tor, self.kirish = t, k
        m = Model(t, k, **st.model_parametrlari())

        sid = None
        if bazaga:
            sid = self.baza.seans_ochish(st.nom, self._kalit)
            for nm, arr, src, un in [("U10", k.U10, "ERA5", "m/s"),
                                     ("namlik", k.w, "ERA5-Land, SMAP", "%"),
                                     ("qoplam", k.lam, "MODIS", "-"),
                                     ("gil", k.m_cl, "SoilGrids", "-"),
                                     ("relyef", t.eta, "SRTM", "m")]:
                self.baza.maydon_yozish(sid, nm, arr, src, un)
        m.ishga_tushir(T=st.T, dt=st.dt, jim=True, baza=self.baza if bazaga else None,
                       seans_id=sid, surat_qadam=st.surat_qadam)
        self.model = m
        self.seans_id = sid
        self._chiz()
        self._natijalar()
        b = m.massa_balansi()
        self.status.set_text(
            f"Yakunlandi: {m.hisoblash_vaqti:.1f} s  |  "
            f"balans nomuvofiqligi {b['nisbiy']:.4f} %  |  "
            f"seans {sid if sid else '—'}")
        self.fig.canvas.draw_idle()

    # ------------------------------------------------------------------
    def _chiz(self):
        if self.model is None:
            return
        m, t = self.model, self.tor
        X, Y = t.x * KM, t.y * KM
        rejim = self.rb.value_selected
        self.ax_main.clear()
        if self.cb:
            try: self.cb.remove()
            except Exception: pass
            self.cb = None

        if rejim == "Konsentratsiya":
            d = m.yuza_konsentratsiya() * 1e9
            vmax = float(np.percentile(d, 99.5)) or 1.0
            im = self.ax_main.pcolormesh(X, Y, d.T, cmap="YlOrRd",
                                         shading="auto", vmin=0, vmax=vmax)
            self.cb = self.fig.colorbar(im, ax=self.ax_main, fraction=0.046, pad=0.02)
            self.cb.set_label("mkg/m³", fontsize=8)
            self.ax_main.contour(X, Y, t.eta.T, levels=4, colors="#5d4037",
                                 linewidths=0.6, alpha=0.5)
            sk = max(1, t.N // 12)
            self.ax_main.quiver(X[::sk], Y[::sk], m.U[::sk, ::sk, 1].T,
                                m.V[::sk, ::sk, 1].T, color="#1a237e",
                                alpha=0.5, scale=280, width=0.003)
            self.ax_main.set_title(f"Yuza konsentratsiyasi,  $t$ = {m.vaqt/3600:.1f} soat",
                                   fontsize=10)
        elif rejim == "Emissiya":
            d = m.F.sum(axis=0) * 1e9
            im = self.ax_main.pcolormesh(X, Y, d.T, cmap="YlOrBr", shading="auto")
            self.cb = self.fig.colorbar(im, ax=self.ax_main, fraction=0.046, pad=0.02)
            self.cb.set_label("$10^{-9}$ kg/(m²·s)", fontsize=8)
            self.ax_main.set_title("Emissiya oqimi $F$", fontsize=10)
        elif rejim == "Kirish maydonlari":
            im = self.ax_main.pcolormesh(X, Y, self.kirish.w.T, cmap="YlGnBu",
                                         shading="auto")
            self.cb = self.fig.colorbar(im, ax=self.ax_main, fraction=0.046, pad=0.02)
            self.cb.set_label("namlik, %", fontsize=8)
            self.ax_main.contour(X, Y, self.kirish.lam.T, levels=5,
                                 colors="#2c7a4b", linewidths=0.8)
            self.ax_main.set_title("Tuproq namligi va oʻsimlik qoplami", fontsize=10)
        else:
            self.ax_main.axis("off")
            self.ax_main.text(0.5, 0.5, "Balans grafigi pastda keltirilgan",
                              ha="center", va="center", color="#90a4ae",
                              transform=self.ax_main.transAxes)
        if rejim != "Balans":
            self.ax_main.set_xlabel("$x$, km", fontsize=9)
            self.ax_main.set_ylabel("$y$, km", fontsize=9)
            self.ax_main.set_aspect("equal")

        # vertikal profil
        self.ax_prof.clear()
        # profil nuqtalari geografik koordinata boʻyicha (Buxoro viloyati hududi):
        # Qizilqum ichidagi nuqta va Oʻzgidromet Buxoro stansiyasi
        lon = 61.5 + t.x / (111320 * np.cos(np.deg2rad(40.25)))
        lat = 38.5 + t.y / 110574
        def _ij(la, lo):
            return int(np.argmin(np.abs(lon - lo))), int(np.argmin(np.abs(lat - la)))
        (i1, j1), (i2, j2) = _ij(40.80, 63.50), _ij(39.7762, 64.4197)
        for ii, jj, nom, c in [(i1, j1, "Qizilqum", "#c0392b"),
                               (i2, j2, "Buxoro", "#2c7a4b")]:
            z = t.balandlik()[ii, jj, :] * KM
            self.ax_prof.plot(m.C[:, ii, jj, :].sum(axis=0) * 1e9, z, lw=1.9,
                              color=c, label=nom)
        self.ax_prof.set_xlabel("mkg/m³", fontsize=8)
        self.ax_prof.set_ylabel("$z$, km", fontsize=8)
        self.ax_prof.set_title("Vertikal profil", fontsize=9.5)
        self.ax_prof.grid(alpha=0.3); self.ax_prof.legend(fontsize=7)
        self.ax_prof.set_ylim(0, 3.0)

        # fraksiyalar
        self.ax_frak.clear()
        nomlar = ["PM2.5", "PM10", "10-20", "20-50", "50-100"]
        massa = [m.balans[i].massa(m.C[i]) / 1e6 for i in range(m.Nf)]
        self.ax_frak.bar(nomlar, massa,
                         color=["#1f6fb2", "#2c7a4b", "#d77a3a", "#c0392b", "#8e44ad"],
                         edgecolor="k", lw=0.5)
        self.ax_frak.set_ylabel("ming tonna", fontsize=8)
        self.ax_frak.set_title("Fraksiyalar", fontsize=9.5)
        self.ax_frak.tick_params(labelsize=7)
        self.ax_frak.grid(alpha=0.3, axis="y")

        # balans
        self.ax_bal.clear()
        tar = m.balans[0].tarix
        if tar:
            tt = np.array([z["t"] for z in tar]) / 3600.0
            def sr(key):
                return np.array([sum(b.tarix[i][key] for b in m.balans)
                                 for i in range(len(tar))]) / 1e6
            self.ax_bal.plot(tt, sr("Q_em"), lw=1.9, color="#c0392b", label="chiqqan")
            self.ax_bal.plot(tt, sr("Q_cho"), lw=1.9, color="#2c7a4b", label="choʻkkan")
            self.ax_bal.plot(tt, sr("Q_chiq"), lw=1.9, color="#d77a3a", label="chegaradan")
            self.ax_bal.plot(tt, sr("Q"), lw=1.9, color="#1f6fb2", label="sohada")
            self.ax_bal.legend(fontsize=7.5, ncol=4, loc="upper left")
        self.ax_bal.set_xlabel("$t$, soat", fontsize=8.5)
        self.ax_bal.set_ylabel("ming tonna", fontsize=8.5)
        self.ax_bal.set_title("Massa balansi", fontsize=9.5)
        self.ax_bal.grid(alpha=0.3)

    # ------------------------------------------------------------------
    def _natijalar(self):
        m = self.model
        b = m.massa_balansi()
        y = m.yuza_konsentratsiya() * 1e9
        s = ["MASSA BALANSI, ming tonna", "-" * 34,
             f"{'chiqqan':<20}{b['Q_em']/1e6:>13.1f}",
             f"{'choʻkkan':<20}{b['Q_cho']/1e6:>13.1f}",
             f"{'chegaradan':<20}{b['Q_chiq']/1e6:>13.1f}",
             f"{'yutilgan':<20}{b['Q_yut']/1e6:>13.2f}",
             f"{'sohada':<20}{b['Q']/1e6:>13.1f}",
             "-" * 34,
             f"{'nomuvofiqlik, %':<20}{b['nisbiy']:>13.4f}", "",
             "KONSENTRATSIYA, mkg/m3", "-" * 34,
             f"{'oʻrtacha':<20}{y.mean():>13.1f}",
             f"{'mediana':<20}{np.median(y):>13.1f}",
             f"{'maksimal':<20}{y.max():>13.1f}", "",
             f"sxema: {m.sxema},  hisoblash: {m.hisoblash_vaqti:.1f} s"]
        self.txt.set_text("\n".join(s))

    def eksport(self, event):
        if self.model is None:
            self.status.set_text("avval hisoblashni bajaring"); return
        from .eksport import csv_eksport, ascii_grid_eksport, npz_eksport, hisobot
        os.makedirs("natijalar", exist_ok=True)
        y = self.model.yuza_konsentratsiya()
        csv_eksport("natijalar/konsentratsiya.csv", self.tor, y)
        ascii_grid_eksport("natijalar/konsentratsiya.asc", self.tor, y)
        npz_eksport("natijalar/natija.npz", self.tor, self.model)
        hisobot("natijalar/hisobot.txt", self.model, self.stsenariy)
        self.status.set_text("Eksport bajarildi: natijalar/ katalogiga saqlandi")
        self.fig.canvas.draw_idle()


def ishga_tushir(baza="dustflow.db", stsenariylar="stsenariylar"):
    o = Oyna(baza, stsenariylar)
    plt.show()
    return o


if __name__ == "__main__":
    ishga_tushir()
