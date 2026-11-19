# Oldindan qayd etish: CAMS chegaraviy shartlari bilan validatsiya tajribasi

**Qayd etilgan sana:** 2026-yil 21-sentabr, hisoblash boshlanishidan oldin.
**Maqsad:** hisoblash natijasini koʻrgandan keyin sozlamalarni oʻzgartirish imkoniyatini yopish.
Quyida yozilgan hamma narsa natija qanday chiqishidan qatʼi nazar oʻzgartirilmaydi.

## 1. Ushbu tajribadan oldingi holat (allaqachon olingan natijalar)

Yon chegaralarda $C_b = 0$ boʻlgan model 29.04.2025 09:00 UTC boʻroni uchun CAMS
EAC4 reanalizi bilan 35 yacheykada solishtirilganda Chang–Hanna mezonlaridan oʻtmadi:
NMB = −68 %, FB = 1,03, NMSE = 2,29, FAC2 = 0,14, r = 0,23.
Bu natija § 4.3 ga oʻzgartirilmasdan kiritiladi.

Aniqlangan sabab: shamol shimoldan esgan (3–15°), CAMS da shimoliy chegara boʻylab
226–604 mkg/m³ chang mavjud, modelda esa kirish oqimi yoʻq.

## 2. Oʻzgartiriladigan yagona narsa

Yon chegaralardagi fon konsentratsiyasi $C_b$ CAMS EAC4 dan olinadi.
Boshqa hech narsa oʻzgarmaydi.

**$C_b$ ni qurish qoidasi:**

- manba: CAMS EAC4, `pm10` va `pm2p5`;
- qiymat: boʻron vaqti (29.04 09:00 UTC) minus sokin kun (23.04 09:00 UTC) — model faqat chang hissasini hisoblagani uchun;
- fazoviy interpolyatsiya: CAMS toʻridan chegara tugunlariga ikki chiziqli;
- fraksiyalar: PM2.5 → 1-fraksiya; (PM10 − PM2.5) → 2-fraksiya; 10 mkm dan yirik fraksiyalar uchun $C_b = 0$ (yirik zarrachalar uzoq masofaga yetib kelmaydi);
- vertikal profil: yer sirtidan **1500 m** gacha bir tekis, undan yuqorida 0;
- manfiy qiymatlar (sokin kun boʻrondan changliroq boʻlgan joylar) 0 ga tenglashtiriladi.

**Aralashish qatlami balandligi 1500 m** — bu erkin parametr. U asosiy natija sifatida qabul qilinadi.
Sezgirlik uchun 1000 m va 2500 m bilan qoʻshimcha hisoblar bajariladi va **uchalasi ham** hisobotga kiritiladi;
ulardan eng yaxshisini tanlash taqiqlanadi.

## 3. Muzlatilgan sozlamalar

| Parametr | Qiymat |
|---|---|
| Statik maydonlar | Copernicus DEM, ESA WorldCover 2021, SoilGrids 2.0 + choʻl uchun adabiyot qiymatlari |
| Ekinzorlar (sinf 40) | $A_{ef} = 0$ (vegetatsiya mavsumi, sugʻoriladigan) |
| Meteorologiya | ERA5-Land, 29.04.2025 09:00 UTC, hisoblash davomida oʻzgarmas |
| Toʻr | 60 × 60 × 20, $\Delta t = 120$ s |
| Hisoblash davri | 12 soat |
| $\xi$ | model standarti: $\overline{|U|} + \overline{|V|}$ |
| Emissiya sxemasi | oʻzgarishsiz |

## 4. Baholash usuli

- Taqqoslash: model PM10 (1- va 2-fraksiyalar yigʻindisi, yer sirti qatlami), CAMS 0,75° yacheykalariga oʻrtalangan.
- Mos yozuv: CAMS, boʻron minus sokin kun.
- **Faqat 15 ta ichki yacheyka** (chegara halqasi chiqarib tashlanadi), chunki chegaradagi qiymatlar CAMS dan olingan — ularni baholashga kiritish natijani sunʼiy yaxshilaydi.
- Mezonlar: MB, NMB, RMSE, NMSE, r, FAC2, FB, Willmott $d$.
- Oʻtish sharti (Chang va Hanna, 2004): $|FB| < 0{,}3$, $NMSE < 1{,}5$, $FAC2 > 0{,}5$ — uchalasi bir vaqtda.
- Qoʻshimcha: Buxoro yacheykasidagi qiymat alohida koʻrsatiladi.
- Mahalliy emissiya hissasi: $C_b$ li va $C_b = 0$ li hisoblar farqi boʻyicha baholanadi.

## 5. Bashorat

- Ichki 15 yacheyka boʻyicha oʻrtacha model PM10: **450–750 mkg/m³** (CAMS: 618).
- FAC2 > 0,5 va |FB| < 0,3 boʻladi.
- Mahalliy emissiyaning ulushi ichki hududda 25–50 % oraligʻida boʻladi.

Agar oʻtish sharti bajarilmasa, natija shundayligicha yoziladi va modelning cheklovlari
sifatida muhokama qilinadi. Sozlamalarni natijaga moslab oʻzgartirish amalga oshirilmaydi.

## 6. Hisoblashdan oldin bajariladigan texnik tekshiruv

Chegara orqali kiruvchi oqimni hisobga oladigan massa balansi tuzatiladi va quyidagi test
bilan tekshiriladi: emissiyasiz, faqat $C_b > 0$ boʻlgan holatda balans nomuvofiqligi
0,01 % dan kichik boʻlishi kerak. Test oʻtmasa, tajriba boshlanmaydi.

---

## Qoʻshimcha A — texnik test natijasi (tajribadan oldin)

**Birinchi urinish oʻtmadi** (qoldiq 0,54 %). Sabab — test skriptidagi xato: qoʻlda yozilgan
balans formulasida manfiy qiymatlarni kesish tuzatmasi (`kesilgan`) hisobga olinmagan edi.
Modelning rasmiy balans formulasi bu hadni oʻz ichiga oladi. Test mezoni (0,01 %) oʻzgartirilmadi;
faqat qoldiq rasmiy formula boʻyicha va umumiy kirgan massaga nisbatan hisoblandi
(emissiyasiz holatda emissiyaga boʻlish nolga boʻlishga olib keladi).

**Tuzatilgan test oʻtdi:** qoldiq 0,0026 %. Regressiya testi ($C_b = 0$): 0,0065 %.

**Aniqlangan sonli xususiyat:** kirish frontida sxema manfiy tebranishlar beradi; ularni kesish
kirgan massaning **0,54 %** ini sunʼiy qoʻshadi. Balans buni aniq hisobga oladi, biroq bu
kichik musbat siljish sifatida natijalarda qayd etiladi.

---

## Qoʻshimcha B — natijalar (hisoblashdan keyin; yuqoridagi boʻlimlar oʻzgartirilmagan)

Asl qayd (1–6-boʻlimlar) raqamli izi: `1ac343034b61fab97d199dc84bfe6097bbb9072203608461ef929ebf757f23b3`,
qayd vaqti 2026-09-21 17:40:35 UTC.

**Baholash: 15 ta ichki yacheyka, CAMS (boʻron − sokin kun).**

| Variant | FB | NMSE | FAC2 | r | NMB | Ichki oʻrtacha | Chang–Hanna |
|---|---|---|---|---|---|---|---|
| $C_b = 0$ | 1,02 | 1,97 | 0,20 | 0,07 | −68 % | 201 | oʻtmadi |
| $H$ = 1000 m | 0,47 | 0,53 | 0,47 | 0,06 | −38 % | 383 | oʻtmadi |
| **$H$ = 1500 m (asosiy)** | **0,34** | **0,38** | **0,53** | **0,07** | **−29 %** | **438** | **oʻtmadi** |
| $H$ = 2500 m | 0,32 | 0,37 | 0,67 | 0,08 | −28 % | 446 | oʻtmadi |
| CAMS | | | | | | 618 | |

**Bashoratlar bilan solishtirish:**

- ichki oʻrtacha 450–750 — **bajarilmadi** (438);
- FAC2 > 0,5 — bajarildi (0,53);
- |FB| < 0,3 — **bajarilmadi** (0,34);
- mahalliy emissiya ulushi 25–50 % — bajarildi (46 %).

**Xulosa.** Asosiy variant Chang–Hanna mezonlaridan oʻtmadi (FB chegaradan biroz oshdi).
Chegaradan kirishni hisobga olish barcha siljish koʻrsatkichlarini sezilarli yaxshiladi va bu
yaxshilanish uchala $H$ qiymatida ham kuzatiladi, yaʼni erkin parametr tanlovidan bogʻliq emas.
Fazoviy korrelyatsiya barcha variantlarda nolga yaqin (r ≈ 0,07): model changning umumiy
miqdorini qoniqarli tartibda bersa-da, uning fazoviy taqsimotini takrorlamaydi — Buxoro yacheykasida
2,3 barobar ortiq, gʻarbiy qismda past. Mahalliy emissiya ulushi barcha variantlarda 45–52 %.

Qoʻshimcha tajriba sifatida vaqt boʻyicha oʻzgaruvchan ERA5 majburlashini qoʻshish rejalashtirilgan;
u ham alohida oldindan qayd etiladi.
