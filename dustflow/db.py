# -*- coding: utf-8 -*-
"""Ma'lumotlar bazasi moduli.

Hisoblash seanslari, kirish parametrlari, vaqt qatorlari va konsentratsiya
maydonlarining suratlari SQLite bazasida saqlanadi. Bu quyidagilarni
ta'minlaydi:
  - sutkalik hisoblashlarni bir-biri bilan solishtirish;
  - bajarilgan hisoblashni takrorlamaslik (parametrlar bo'yicha qidirish);
  - uzilgan hisoblashni oxirgi suratdan davom ettirish;
  - kuzatuv ma'lumotlari bilan solishtirish uchun arxiv yuritish.

Sxema:
  seanslar        — har bir hisoblash seansi va uning parametrlari
  maydonlar       — kirish maydonlarining jamlanma tavsifi
  qatorlar        — vaqt qatorlari (massa balansi, maksimal konsentratsiya)
  suratlar        — konsentratsiya maydonlarining siqilgan suratlari
  kuzatuvlar      — meteostansiyalardan olingan o'lchov ma'lumotlari
"""
import io
import json
import sqlite3
import hashlib
import datetime as dt
import numpy as np

SXEMA = """
CREATE TABLE IF NOT EXISTS seanslar (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nom          TEXT NOT NULL,
    yaratilgan   TEXT NOT NULL,
    barmoq_izi   TEXT UNIQUE,
    parametrlar  TEXT NOT NULL,
    holat        TEXT DEFAULT 'boshlandi',
    hisob_vaqti  REAL,
    izoh         TEXT
);
CREATE TABLE IF NOT EXISTS maydonlar (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    seans_id  INTEGER NOT NULL REFERENCES seanslar(id) ON DELETE CASCADE,
    nom       TEXT NOT NULL,
    manba     TEXT,
    birlik    TEXT,
    eng_kam   REAL, eng_kop REAL, ortacha REAL,
    UNIQUE(seans_id, nom)
);
CREATE TABLE IF NOT EXISTS qatorlar (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    seans_id  INTEGER NOT NULL REFERENCES seanslar(id) ON DELETE CASCADE,
    t         REAL NOT NULL,
    Q         REAL, Q_em REAL, Q_cho REAL, Q_chiq REAL, Q_yut REAL,
    C_max     REAL, C_ort REAL, nomuvofiqlik REAL
);
CREATE INDEX IF NOT EXISTS ix_qatorlar ON qatorlar(seans_id, t);
CREATE TABLE IF NOT EXISTS suratlar (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    seans_id  INTEGER NOT NULL REFERENCES seanslar(id) ON DELETE CASCADE,
    t         REAL NOT NULL,
    shakl     TEXT NOT NULL,
    malumot   BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_suratlar ON suratlar(seans_id, t);
CREATE TABLE IF NOT EXISTS kuzatuvlar (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    stansiya  TEXT NOT NULL,
    x         REAL, y REAL,
    sana      TEXT NOT NULL,
    C_pm10    REAL, C_pm25 REAL, U10 REAL, izoh TEXT
);
CREATE INDEX IF NOT EXISTS ix_kuzatuv ON kuzatuvlar(stansiya, sana);
"""


def _blob(arr: np.ndarray) -> bytes:
    """Massivni siqilgan ko'rinishda baytlarga aylantiradi."""
    buf = io.BytesIO()
    np.savez_compressed(buf, a=np.asarray(arr, dtype=np.float32))
    return buf.getvalue()


def _massiv(b: bytes) -> np.ndarray:
    return np.load(io.BytesIO(b))["a"]


class Baza:
    """DustFlow ma'lumotlar bazasi bilan ishlash."""

    def __init__(self, yol: str = "dustflow.db"):
        self.yol = yol
        self.kon = sqlite3.connect(yol)
        self.kon.row_factory = sqlite3.Row
        self.kon.execute("PRAGMA foreign_keys = ON")
        self.kon.executescript(SXEMA)
        self.kon.commit()

    # ---------------------------------------------------------
    @staticmethod
    def barmoq_izi(parametrlar: dict) -> str:
        """Parametrlar bo'yicha noyob identifikator."""
        s = json.dumps(parametrlar, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

    def seans_bormi(self, parametrlar: dict):
        """Xuddi shu parametrlar bilan hisoblash bajarilganmi?"""
        bi = self.barmoq_izi(parametrlar)
        r = self.kon.execute(
            "SELECT * FROM seanslar WHERE barmoq_izi = ? AND holat = 'tugadi'",
            (bi,)).fetchone()
        return dict(r) if r else None

    def seans_ochish(self, nom: str, parametrlar: dict, izoh: str = "") -> int:
        bi = self.barmoq_izi(parametrlar)
        cur = self.kon.execute(
            "INSERT OR REPLACE INTO seanslar (nom, yaratilgan, barmoq_izi, "
            "parametrlar, holat, izoh) VALUES (?,?,?,?,?,?)",
            (nom, dt.datetime.now().isoformat(timespec="seconds"), bi,
             json.dumps(parametrlar, ensure_ascii=False), "boshlandi", izoh))
        self.kon.commit()
        return cur.lastrowid

    def seans_yopish(self, seans_id: int, hisob_vaqti: float):
        self.kon.execute(
            "UPDATE seanslar SET holat='tugadi', hisob_vaqti=? WHERE id=?",
            (hisob_vaqti, seans_id))
        self.kon.commit()

    # ---------------------------------------------------------
    def maydon_yozish(self, seans_id: int, nom: str, arr, manba="", birlik=""):
        a = np.asarray(arr, dtype=float)
        self.kon.execute(
            "INSERT OR REPLACE INTO maydonlar (seans_id, nom, manba, birlik, "
            "eng_kam, eng_kop, ortacha) VALUES (?,?,?,?,?,?,?)",
            (seans_id, nom, manba, birlik,
             float(a.min()), float(a.max()), float(a.mean())))
        self.kon.commit()

    def qator_yozish(self, seans_id: int, t: float, **kw):
        ustunlar = ["Q", "Q_em", "Q_cho", "Q_chiq", "Q_yut",
                    "C_max", "C_ort", "nomuvofiqlik"]
        qiy = [kw.get(u) for u in ustunlar]
        self.kon.execute(
            f"INSERT INTO qatorlar (seans_id, t, {','.join(ustunlar)}) "
            f"VALUES (?,?,{','.join('?'*len(ustunlar))})",
            [seans_id, t] + qiy)
        self.kon.commit()

    def surat_yozish(self, seans_id: int, t: float, C: np.ndarray):
        self.kon.execute(
            "INSERT INTO suratlar (seans_id, t, shakl, malumot) VALUES (?,?,?,?)",
            (seans_id, t, json.dumps(list(C.shape)), _blob(C)))
        self.kon.commit()

    # ---------------------------------------------------------
    def qatorlar(self, seans_id: int):
        r = self.kon.execute(
            "SELECT * FROM qatorlar WHERE seans_id=? ORDER BY t", (seans_id,)).fetchall()
        return [dict(x) for x in r]

    def oxirgi_surat(self, seans_id: int):
        """Uzilgan hisoblashni davom ettirish uchun."""
        r = self.kon.execute(
            "SELECT * FROM suratlar WHERE seans_id=? ORDER BY t DESC LIMIT 1",
            (seans_id,)).fetchone()
        if r is None:
            return None, None
        return r["t"], _massiv(r["malumot"]).reshape(json.loads(r["shakl"]))

    def seanslar_royxati(self, n=20):
        r = self.kon.execute(
            "SELECT id, nom, yaratilgan, holat, hisob_vaqti FROM seanslar "
            "ORDER BY id DESC LIMIT ?", (n,)).fetchall()
        return [dict(x) for x in r]

    def solishtirish(self, seans_idlar):
        """Bir necha seansning yakuniy ko'rsatkichlarini solishtiradi."""
        natija = []
        for sid in seans_idlar:
            s = self.kon.execute("SELECT * FROM seanslar WHERE id=?", (sid,)).fetchone()
            q = self.kon.execute(
                "SELECT * FROM qatorlar WHERE seans_id=? ORDER BY t DESC LIMIT 1",
                (sid,)).fetchone()
            if s and q:
                natija.append(dict(id=sid, nom=s["nom"],
                                   parametrlar=json.loads(s["parametrlar"]),
                                   **{k: q[k] for k in q.keys() if k not in ("id", "seans_id")}))
        return natija

    # ---------------------------------------------------------
    def kuzatuv_yozish(self, stansiya, x, y, sana, C_pm10=None,
                       C_pm25=None, U10=None, izoh=""):
        self.kon.execute(
            "INSERT INTO kuzatuvlar (stansiya, x, y, sana, C_pm10, C_pm25, U10, izoh) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (stansiya, x, y, sana, C_pm10, C_pm25, U10, izoh))
        self.kon.commit()

    def kuzatuvlar(self, stansiya=None):
        if stansiya:
            r = self.kon.execute(
                "SELECT * FROM kuzatuvlar WHERE stansiya=? ORDER BY sana",
                (stansiya,)).fetchall()
        else:
            r = self.kon.execute("SELECT * FROM kuzatuvlar ORDER BY sana").fetchall()
        return [dict(x) for x in r]

    def yop(self):
        self.kon.close()
