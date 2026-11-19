# -*- coding: utf-8 -*-
"""DustFlow — buyruqlar qatori interfeysi."""
import argparse
import logging
import os
import sys

from .grid import Tor, relyef_yarat
from .data import buxoro_maydonlari
from .io_geo import stsenariy_yukla, stsenariylar_royxati
from .model import Model
from .db import Baza
from .config import Stsenariy
from . import __version__

BAR = "=" * 78


def royxat_korsat(katalog):
    r = stsenariylar_royxati(katalog)
    if not r:
        print(f"  '{katalog}' katalogida stsenariy topilmadi.")
        print("  Yaratish uchun:  python -m dustflow --stsenariy-yarat")
        return r
    print(BAR)
    print(f"  DustFlow v{__version__} — mavjud stsenariylar ({len(r)} ta)")
    print(BAR)
    print(f"{'№':>3}  {'identifikator':<22}{'nomi':<32}{'sana':<12}{'mavsum'}")
    print("-" * 78)
    for i, z in enumerate(r, 1):
        print(f"{i:>3}  {z['id']:<22}{z['nom']:<32}{z['sana']:<12}{z['mavsum']}")
    print("-" * 78)
    print("  Tanlash:  python -m dustflow --stsenariy <№ yoki identifikator>")
    return r


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="dustflow",
        description="Shamol eroziyasi va chang tarqalishini bashoratlash majmuasi")
    p.add_argument("-s", "--stsenariy", default=None,
                   help="stsenariy raqami yoki identifikatori")
    p.add_argument("-r", "--royxat", action="store_true",
                   help="mavjud stsenariylar roʻyxatini koʻrsatish")
    p.add_argument("--stsenariy-yarat", action="store_true",
                   help="namunaviy 10 ta stsenariyni yaratish")
    p.add_argument("-k", "--katalog", default="stsenariylar",
                   help="stsenariylar katalogi")
    p.add_argument("-T", "--vaqt", type=float, default=None, help="hisoblash davri, soat")
    p.add_argument("--dt", type=float, default=None, help="vaqt qadami, s")
    p.add_argument("-N", type=int, default=None, help="gorizontal toʻr oʻlchami")
    p.add_argument("--U10", type=float, default=None,
                   help="shamol tezligi (stsenariysiz ishlaganda)")
    p.add_argument("--yonalish", type=float, default=40.0, help="shamol yoʻnalishi, °")
    p.add_argument("--sxema", choices=["aniq", "tezkor"], default="aniq",
                   help="aniq — vaqt boʻyicha 2-tartibli (III bob), tezkor — 1-tartibli (II bob)")
    p.add_argument("--qarshilik", choices=["re", "stoks"], default="re",
                   help="choʻkish tezligi: re — f(Re) bilan (3.6), stoks — (2.13)")
    p.add_argument("-L", type=int, default=None, help="vertikal tugunlar soni")
    p.add_argument("--beta-s", type=float, default=None,
                   help="vertikal toʻrni quyuqlashtirish parametri (0 — tekis)")
    p.add_argument("--C-alpha", type=float, default=None,
                   help="emissiya kalibrlash koeffitsiyenti C_alpha (2.12)")
    p.add_argument("--baza", default="dustflow.db", help="maʼlumotlar bazasi fayli")
    p.add_argument("--eksport", default=None, help="natijalarni shu katalogga eksport qilish")
    p.add_argument("--gui", action="store_true", help="grafik interfeysni ishga tushirish")
    p.add_argument("--solishtir", nargs="+", type=int, default=None,
                   help="bazadagi seanslarni solishtirish")
    p.add_argument("-v", "--version", action="version", version=f"DustFlow {__version__}")
    a = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if a.stsenariy_yarat:
        from .stsenariy_yaratish import hammasini_yarat
        print(f"  '{a.katalog}' katalogida stsenariylar yaratilmoqda...")
        hammasini_yarat(a.katalog)
        return 0

    if a.royxat:
        royxat_korsat(a.katalog)
        return 0

    if a.gui:
        from .gui import ishga_tushir
        ishga_tushir(a.baza, a.katalog)
        return 0

    if a.solishtir:
        b = Baza(a.baza)
        print(f"{'id':>4}  {'nom':<24}{'chiqqan':>12}{'sohada':>12}{'C_max':>10}")
        print("-" * 66)
        for z in b.solishtirish(a.solishtir):
            print(f"{z['id']:>4}  {z['nom'][:24]:<24}"
                  f"{(z['Q_em'] or 0)/1e6:>12.1f}{(z['Q'] or 0)/1e6:>12.1f}"
                  f"{(z['C_max'] or 0)*1e9:>10.1f}")
        return 0

    # ---- stsenariyni tanlash ----
    st = Stsenariy()
    tanlangan = None
    if a.stsenariy is not None:
        r = stsenariylar_royxati(a.katalog)
        if not r:
            print("  stsenariylar topilmadi; --stsenariy-yarat bilan yarating")
            return 1
        if a.stsenariy.isdigit() and 1 <= int(a.stsenariy) <= len(r):
            tanlangan = r[int(a.stsenariy) - 1]
        else:
            mos = [z for z in r if z["id"] == a.stsenariy or
                   a.stsenariy.lower() in z["nom"].lower()]
            if not mos:
                print(f"  '{a.stsenariy}' stsenariysi topilmadi")
                royxat_korsat(a.katalog)
                return 1
            tanlangan = mos[0]
        tav = tanlangan.get("tavsiya", {})
        st.N = st.M = a.N or tav.get("N", 60)
        st.L = a.L or max(tav.get("L", 30), 30)
        st.T = (a.vaqt or tav.get("T_soat", 12)) * 3600.0
        st.dt = a.dt or tav.get("dt", 120.0)
        st.nom = tanlangan["id"]
    else:
        st.N = st.M = a.N or 60
        st.L = a.L or st.L
        st.T = (a.vaqt or 12) * 3600.0
        st.dt = a.dt or 120.0
        st.U10 = a.U10 or 12.0
        st.yonalish = a.yonalish
        st.nom = "qolda"

    st.sxema, st.qarshilik = a.sxema, a.qarshilik
    if a.beta_s is not None:
        st.beta_s = a.beta_s
    if a.C_alpha is not None:
        st.C_alpha = a.C_alpha
    print(BAR)
    print(f"  DustFlow v{__version__}")
    if tanlangan:
        print(f"  Stsenariy : {tanlangan['nom']}  ({tanlangan['id']})")
        print(f"  Tavsif    : {tanlangan['tavsif']}")
        print(f"  Sana      : {tanlangan['sana']},  mavsum: {tanlangan['mavsum']}")
    else:
        print(f"  Rejim     : qoʻlda berilgan parametrlar, U10 = {st.U10} m/s")
    print(f"  Toʻr      : {st.N}x{st.M}x{st.L} (beta_s = {st.beta_s}),  dt = {st.dt:.0f} s,  "
          f"davri = {st.T/3600:.0f} soat")
    nom = ("aniq: simmetrik (Krank–Nikolson) + 2 x uch qatlamli (BDF2), 2-tartib"
           if st.sxema == "aniq" else "tezkor: yoʻnalishlar boʻyicha ajratish, 1-tartib")
    print(f"  Sxema     : {nom}")
    print(f"  Choʻkish  : {'f(Re) = 1 + 0.15 Re^0.687' if st.qarshilik == 're' else 'Stoks'},"
          f"  C_alpha = {st.C_alpha:g}")
    print(BAR)

    t = Tor(Lx=st.Lx, Ly=st.Ly, Hz=st.Hz, N=st.N, M=st.M, L=st.L, beta_s=st.beta_s)
    if tanlangan:
        k, _ = stsenariy_yukla(tanlangan["yol"], t, jim=False)
        t.eta = k.eta; t.He = t.Hz - t.eta
    else:
        t.eta = relyef_yarat(t); t.He = t.Hz - t.eta
        k = buxoro_maydonlari(t, U10_qiymat=st.U10, yonalish=st.yonalish)
    xato = k.tekshir()
    if xato:
        print("  [xato] kirish maydonlari:", ", ".join(xato))
        return 1

    b = Baza(a.baza)
    kalit = st.kalit()
    if tanlangan:
        kalit["stsenariy"] = tanlangan["id"]
    mavjud = b.seans_bormi(kalit)
    if mavjud:
        print(f"  [eslatma] xuddi shu parametrlar bilan hisoblash bajarilgan "
              f"(seans {mavjud['id']}, {mavjud['hisob_vaqti']:.0f} s)")
    sid = b.seans_ochish(st.nom, kalit,
                         izoh=tanlangan["tavsif"] if tanlangan else "")
    for nm, arr, src in [("U10", k.U10, "ERA5"), ("namlik", k.w, "ERA5-Land"),
                         ("qoplam", k.lam, "MODIS"), ("relyef", k.eta, "SRTM")]:
        b.maydon_yozish(sid, nm, arr, src)

    m = Model(t, k, **st.model_parametrlari())
    print()
    m.ishga_tushir(T=st.T, dt=st.dt, baza=b, seans_id=sid,
                   surat_qadam=st.surat_qadam)

    bal = m.massa_balansi()
    y = m.yuza_konsentratsiya() * 1e9
    print(BAR)
    print(f"  {'chiqqan massa':<26}{bal['Q_em']/1e6:12.1f} ming tonna")
    print(f"  {'choʻkkan massa':<26}{bal['Q_cho']/1e6:12.1f} ming tonna")
    print(f"  {'chegaradan chiqqan':<26}{bal['Q_chiq']/1e6:12.1f} ming tonna")
    print(f"  {'sohada muallaq':<26}{bal['Q']/1e6:12.1f} ming tonna")
    print(f"  {'balans nomuvofiqligi':<26}{bal['nisbiy']:12.4f} %")
    print(f"  {'yuza konsentratsiyasi':<26}{y.mean():12.1f} mkg/m3 (oʻrtacha)")
    print(f"  {'':<26}{y.max():12.1f} mkg/m3 (maksimal)")
    print(f"  {'hisoblash vaqti':<26}{m.hisoblash_vaqti:12.1f} s")
    if m.iteratsiyalar:
        import numpy as _np
        print(f"  {'iteratsiyalar (3.43)':<26}{_np.mean(m.iteratsiyalar):12.2f} (oʻrtacha), "
              f"{max(m.iteratsiyalar)} (maks)")
    print(f"  {'bazadagi seans':<26}{sid:12d}")
    print(BAR)

    if a.eksport:
        from .eksport import csv_eksport, ascii_grid_eksport, npz_eksport, hisobot
        os.makedirs(a.eksport, exist_ok=True)
        ascii_grid_eksport(os.path.join(a.eksport, "konsentratsiya.asc"),
                           t, m.yuza_konsentratsiya())
        csv_eksport(os.path.join(a.eksport, "konsentratsiya.csv"),
                    t, m.yuza_konsentratsiya())
        npz_eksport(os.path.join(a.eksport, "natija.npz"), t, m)
        hisobot(os.path.join(a.eksport, "hisobot.txt"), m, st)
        print(f"  Eksport bajarildi: {a.eksport}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
