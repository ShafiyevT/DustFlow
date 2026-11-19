# Oldindan qayd etish №2: stansiya kuzatuvlari bilan validatsiya

**Qayd sanasi:** 2026-yil 25-sentabr, model bilan kuzatuvni solishtirishdan oldin.

## 0. Ochiq bayonot

Kuzatuv maʼlumotlari (Oʻzgidromet «DigitalMeteo» portali, Horiba avtomatik stansiyalari)
ushbu qayddan **oldin** olingan va koʻrib chiqilgan: stansiya va CAMS taqqoslandi, fon va
boʻron qiymatlari hisoblandi. Model natijalari bilan soatlik taqqoslash **hali bajarilmagan**.
Qayd aynan shu taqqoslash usulini belgilaydi. Bitta istisno: DustFlow ning boʻrondagi
PM2.5/PM10 nisbati (0,13) oldingi hisobdan maʼlum edi va stansiyaniki (0,16) bilan solishtirildi —
bu natija oldindan qayd etilmagan deb belgilanadi.

**Kuzatuv fayli:** `portal_soatlik.csv`, SHA-256: `8e25ffaa1d6ad3eade88b9e3a2afac3e70c1c7cd2b498694caa88766068d6d2d`.
Manba tekshiruvi: 16.02.2026 06:00 (mahalliy) Buxoro qiymati Gazeta.uz da eʼlon qilingan
Oʻzgidromet maʼlumotiga toʻliq mos (PM2.5 87, PM10 362).

## 1. Model oʻzgarishi (yagona)

Meteorologik majburlash vaqt boʻyicha oʻzgaruvchan qilinadi: ERA5-Land dan har soatda
$U_{10}$, $V_{10}$, namlik va harorat yangilanadi, emissiya va tezliklar maydoni har soatda qayta
hisoblanadi. Boshqa hamma narsa oldingi qaydda muzlatilganidek qoladi (statik maydonlar,
ekinzorlar $A_{ef}=0$, toʻr 60×60×20, $\Delta t$ = 120 s).

**Texnik test (tajribadan oldin):** oʻzgarmas majburlash bilan yangi kod oldingi natijani
nisbiy farq < 10⁻⁶ bilan takrorlashi va massa balansi < 0,01 % boʻlishi kerak.

## 2. Tajriba A — 2025-yil aprel (asosiy)

- Hisoblash: 27.04.2025 00:00 UTC – 30.04.2025 23:00 UTC; birinchi 24 soat moslashish davri.
- Baholash oraligʻi: **28.04 00:00 – 30.04 23:00 UTC (72 soat)**.
- Stansiyalar: Buxoro (12), Navoiy (11), Qarshi (10) — `horiba.php` dagi aniq koordinatalar,
  model toʻrining eng yaqin katagi.
- Model PM10: 1- va 2-fraksiyalar yigʻindisi, yer sirti qatlami.
- Ikki variant, **ikkalasi ham hisobotga kiradi, tanlash taqiqlanadi:**
  - **A1 (asosiy):** $C_b$ CAMS EAC4 dan (boʻron minus 23.04 09:00 UTC), vaqt boʻyicha 3 soatlik
    qiymatlar orasida chiziqli, $H$ = 1500 m — oldingi qaydning asosiy varianti;
  - **A2:** $C_b = 0$ (faqat mahalliy emissiya).
  CAMS qiymatlarini kuzatuvga qarab masshtablash **amalga oshirilmaydi**.
- Stansiya foni: har bir stansiya uchun 20.04 00:00 – 26.04 23:00 UTC davridagi PM10 medianasi.
- **Asosiy maqsad:** soatlik ortiqcha konsentratsiya (kuzatuv − fon) va model PM10;
  uchala stansiya birlashtirilgan (≤ 216 juftlik). Manfiy ortiqcha qiymatlar kesilmaydi.
- **Qoʻshimcha:** kunlik oʻrtacha ortiqcha (3 stansiya × 3 kun); Buxorodagi choʻqqi vaqti.
- Mezonlar: FB, NMSE, FAC2, r, NMB; oʻtish sharti — Chang–Hanna (|FB|<0,3; NMSE<1,5; FAC2>0,5).

**Bashoratlar (A1):**
1. Buxorodagi model choʻqqisi 29.04 15:00 UTC dan ±3 soat ichida boʻladi.
2. Soatlik asosiy maqsad boʻyicha Chang–Hanna mezonlaridan **oʻtmaydi**: FAC2 0,25–0,5; r 0,2–0,6.
3. Kunlik oʻrtachalar boʻyicha FAC2 ≥ 0,5.
4. Buxorodagi model PM2.5/PM10 29.04 da 0,10–0,20 oraligʻida (kuzatuv 0,16).
5. A2 varianti A1 dan pastroq baholaydi (NMB A2 < NMB A1).

## 3. Tajriba B — 2026-yil fevral (mustaqil sinov)

- Xuddi shu muzlatilgan konfiguratsiya; ERA5-Land 13–17.02.2026 foydalanuvchi tomonidan yuklanadi.
- CAMS EAC4 bu davrni qamramasa, faqat $C_b = 0$ varianti bajariladi — bu oldindan belgilanadi.
- Baholash: 15.02 00:00 – 16.02 23:00 UTC; Buxoro va Qarshi (Navoiy — 40 % qamrov, chiqariladi).
- Fon: 14.02.2026 00:00 – 14.02 23:00 UTC medianasi.

**Bashoratlar:**
1. Model hodisani Buxoroda Qarshidan oldin koʻrsatadi (kechikish > 0 soat; kuzatuvda 4 soat).
2. Model Buxorodagi 4442 mkg/m³ choʻqqini **ikki barobardan koʻproq past** baholaydi
   (soatlik ERA5 kuchli shamol zarbalarini silliqlaydi, modelda shamol zarbasi parametrizatsiyasi yoʻq).
3. Agar qishki tuproq namligi tufayli model deyarli emissiya bermasa, bu natija
   modelning cheklovi sifatida shundayligicha yoziladi.

## 4. Qoidalar

Natijani koʻrgandan keyin kiritilgan har qanday oʻzgarish yangi qayd bilan belgilanadi va
eski natija bilan birga hisobotga kiradi.

---

## Qoʻshimcha A — texnik test va hisoblash jarayoni (qayddan keyin)

- Texnik test (qayd 1-boʻlimi): oʻzgarmas majburlash bilan 6 boʻlakli hisob uzluksiz hisobni
  **bit darajasida** takrorladi (maksimal nisbiy farq 0), balans 0,0044 %. **Oʻtdi.**
- Hisoblash vaqtida `stsenariy()` funksiyasidagi xato aniqlandi: ERA5 NetCDF fayli yopilmagan,
  17 soatdan keyin HDF5 kutubxonasi segmentatsiya xatosi bilan qulagan. Faylni yopish qoʻshildi.
  Bu tuzatish kirish maydonlarining qiymatlarini oʻzgartirmaydi.
- Vaqt moslashtirish: model \$H\$ soatdagi ERA5 bilan \$[H, H{+}1]\$ oraligʻini hisoblaydi va
  stansiyaning \$H\$ dan boshlanadigan soatlik qiymati bilan solishtiriladi.
- Balans: A1 — 0,0029 %, A2 — 0,0028 %.

## Qoʻshimcha B — natijalar (asl qism oʻzgartirilmagan)

**Soatlik, 3 stansiya birlashtirilgan (211 juftlik):**

| Variant | FB | NMSE | FAC2 | r | NMB | Chang–Hanna |
|---|---|---|---|---|---|---|
| A1 (CAMS chegarasi) | −0,48 | 2,71 | 0,23 | 0,28 | +62 % | oʻtmadi |
| A2 (faqat mahalliy) | +0,26 | 3,32 | 0,11 | 0,25 | −23 % | oʻtmadi |

**Stansiyalar boʻyicha (A1 / A2):** Buxoro r = 0,58 / 0,53, NMB = +230 % / +113 %;
Navoiy r = 0,33 / 0,48, NMB = +49 % / −96 %; Qarshi r = −0,07 / −0,07, NMB = −53 % / −89 %.

**Bashoratlar (A1):**

| № | Bashorat | Natija | |
|---|---|---|---|
| 1 | Buxoro choʻqqisi ±3 soat | 12:00 UTC (kuzatuv 15:00), farq 3 soat | bajarildi |
| 2a | Soatlik Chang–Hanna dan oʻtmaydi | oʻtmadi | bajarildi |
| 2b | Soatlik FAC2 0,25–0,5 | 0,23 | **bajarilmadi** |
| 2c | Soatlik r 0,2–0,6 | 0,28 | bajarildi |
| 3 | Kunlik FAC2 ≥ 0,5 | 0,33 | **bajarilmadi** |
| 4 | Buxoro PM2.5/PM10 0,10–0,20 | 0,226 | **bajarilmadi** |
| 5 | NMB(A2) < NMB(A1) | −23 % < +62 % | bajarildi |

**Xulosa.** Model Buxoroda boʻronning boshlanishini va vaqt dinamikasini qoniqarli takrorlaydi
(r ≈ 0,55, choʻqqi 3 soat oldin), lekin konsentratsiyani 2–3 barobar oshirib baholaydi va
30-aprelda changni kuzatuvdagidan sekinroq tarqatadi. Navoiy va Qarshida mahalliy emissiya
kuzatuvni tushuntirmaydi. Qarshida kuzatuvda har kuni kechqurun takrorlanadigan cho'qqilar bor —
ular boʻrondan mustaqil va modelda ifodalanmagan. 4-bashoratning bajarilmasligi tushunarli:
A1 da chegaradan CAMS changi kiradi, CAMS esa mayda fraksiyani oshirib beradi (0,47); faqat
mahalliy emissiyali A2 da nisbat 0,13. Hech bir oʻzgarish natijani koʻrgandan keyin kiritilmadi.

## Qoʻshimcha C — tajriba B natijalari (asl qism oʻzgartirilmagan)

CAMS EAC4 2026-yilni qamramagani uchun qaydga koʻra faqat \$C_b = 0\$ varianti bajarildi.
Balans 0,0000 % (massa yoʻq).

**Natija:** model 72 soat davomida **emissiya bermadi** — hudud boʻyicha \$u_*/u_{*t}\$ ning eng
katta qiymati 0,93 (15.02 09:00 UTC). Sabab — ERA5-Land boʻyicha choʻl tuprogʻi namligi
medianasi 22,5 % (aprel boʻronida 2,2 %), chegaraviy tezlik 0,91 m/s. Shamol esa aprelga
yaqin: hudud maksimumi 11,3 m/s (aprelda 12,9). Stansiyada ortiqcha PM10 4348 mkg/m³ gacha.
Chang–Hanna: oʻtmadi (FB = 2,0, FAC2 = 0).

**Bashoratlar:** 1 — **bajarilmadi** (model hodisani umuman koʻrsatmadi); 2 — rasman bajarildi
(model choʻqqini ikki barobardan koʻproq past baholadi — nol berdi); 3 — shu holat roʻy berdi
va modelning cheklovi sifatida yoziladi.

**Gipotezalar (tekshirilmagan):** (a) chang hududdan tashqaridan kelgan, chegaraviy shartsiz
variant uni koʻra olmaydi; (b) ERA5-Land ning 0–7 sm qatlam namligi eroziyani belgilaydigan
ustki millimetrlardagidan ancha yuqori; (c) soatlik ERA5 kuchli shamol zarbalarini silliqlaydi.
