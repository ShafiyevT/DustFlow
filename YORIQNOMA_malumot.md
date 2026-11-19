# Haqiqiy maʼlumotlarni yuklab olish boʻyicha yoʻriqnoma

Ushbu yoʻriqnoma DustFlow majmuasidagi sintetik kirish maydonlarini haqiqiy geofazoviy maʼlumotlar bilan almashtirish tartibini bayon etadi. Barcha manbalar bepul. Ishni oʻz kompyuteringizda bajarasiz — internet aloqasi talab qilinadi.

Umumiy vaqt: roʻyxatdan oʻtish 20–30 daqiqa, maʼlumot yuklash 30–90 daqiqa (Copernicus navbatiga bogʻliq).

---

## 1. Qaysi maʼlumot qayerdan olinadi

| Maydon | Manba | Aniqlik | Kalit |
|---|---|---|---|
| Shamol $u_{10}$, $v_{10}$ | ERA5-Land (Copernicus CDS) | 0,1°, soatlik | kerak |
| Harorat $T_{2m}$ | ERA5-Land | 0,1°, soatlik | kerak |
| Tuproq namligi | ERA5-Land, `swvl1` | 0,1°, soatlik | kerak |
| Gil ulushi $m_{cl}$ | SoilGrids 2.0 (ISRIC) | 250 m | shart emas |
| Tuproq zichligi | SoilGrids 2.0 | 250 m | shart emas |
| Relyef $\eta$ | Copernicus DEM GLO-90 | 90 m | shart emas |
| Yer qoplami → $z_0$, $\lambda$, $A_{ef}$ | ESA WorldCover 2021 | 10 m | shart emas |
| Chang, PM10 (validatsiya uchun) | CAMS EAC4 (Copernicus ADS) | 0,75°, 3 soatlik | kerak |

Statik maydonlar (relyef, tuproq, yer qoplami) bir marta yuklanadi. Meteorologiya esa har bir sana uchun alohida.

---

## 2. Dasturlarni oʻrnatish

**Python 3.9 yoki undan yuqori** kerak. Tekshirish:

```
python --version
```

Kutubxonalarni oʻrnatish:

```
pip install numpy rasterio netCDF4 cdsapi scipy matplotlib
```

Windows'da `rasterio` oʻrnatishda xato chiqsa, uni conda orqali oʻrnating:

```
conda install -c conda-forge rasterio netcdf4
```

---

## 3. Copernicus'da roʻyxatdan oʻtish

ERA5 va CAMS ikkalasi ham **bitta ECMWF hisobi va bitta token** orqali olinadi.

**3.1. Hisob ochish.** `https://cds.climate.copernicus.eu` saytiga kirib, «Login / Register» tugmasi orqali roʻyxatdan oʻting. Elektron pochtangizni tasdiqlang.

**3.2. CDS kalitini olish.** Tizimga kirgach, `https://cds.climate.copernicus.eu/how-to-api` sahifasini oching. U yerda quyidagi koʻrinishdagi ikki qator chiqadi:

```
url: https://cds.climate.copernicus.eu/api
key: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**3.3. Kalitni faylga yozish.** Windows'da `C:\Users\<foydalanuvchi_nomi>\.cdsapirc` faylini yarating (nomi nuqta bilan boshlanadi, kengaytmasiz) va yuqoridagi ikki qatorni unga koʻchiring.

Bloknot bunday nomli faylni saqlashga ruxsat bermasa, PowerShell'da:

```
notepad $env:USERPROFILE\.cdsapirc
```

**3.4. ADS (CAMS uchun).** Alohida kalit kerak emas: shaxsiy token ECMWF hisobiga bogʻlangan va CDS hamda ADS uchun bir xil. Skript CAMS soʻrovida `.cdsapirc` dagi tokenni avtomatik oladi va faqat manzilni `ads.atmosphere.copernicus.eu/api` ga almashtiradi. Faqat ADS saytiga bir marta oʻsha hisob bilan kirib, CAMS litsenziyasini qabul qilish kifoya (3.5-band).

**3.5. Litsenziyalarni qabul qilish — muhim.** Bu qadam tushib qolsa, soʻrov xato bilan qaytadi. Quyidagi sahifalarni oching, pastga tushib «Licence» boʻlimida **Accept** tugmasini bosing:

- `https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land`
- `https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4`

---

## 4. Oʻrnatishni tekshirish

DustFlow katalogida:

```
python malumot_yuklash.py tekshir
```

Barcha kutubxonalar «ok» va CDS sozlamasi «bor» deb koʻrsatilishi kerak.

---

## 5. Maʼlumotlarni yuklash

Buyruqlarni **shu tartibda** bajaring.

**5.1. Statik maydonlar** (bir marta, kalitsiz):

```
python malumot_yuklash.py statik
```

Relyef, gil ulushi, tuproq zichligi va yer qoplami yuklanadi. Oxirida yer qoplami sinflarining taqsimoti chiqadi — Buxoro viloyati uchun «yalangʻoch / siyrak» va «ekinzor» sinflari ustun boʻlishi kerak. Shu orqali natija toʻgʻriligini tekshirasiz.

**5.2. Meteorologiya** — tanlangan kunlar uchun:

```
python malumot_yuklash.py era5 --dan 2025-07-28 --gacha 2025-07-30
```

Soʻrov Copernicus navbatiga tushadi. Ekranda «queued», keyin «running» holatlari chiqadi. Kutish bir necha daqiqadan bir soatgacha davom etishi mumkin — dasturni yopmang.

**5.3. Validatsiya maʼlumoti:**

```
python malumot_yuklash.py cams --dan 2025-07-28 --gacha 2025-07-30
```

**5.4. Stsenariy yigʻish** — kerakli soatni tanlab:

```
python malumot_yuklash.py stsenariy --vaqt "2025-07-29 09:00" --nom boron_20250729
```

Vaqt **UTC** boʻyicha beriladi. Oʻzbekiston vaqti UTC+5, yaʼni Toshkent vaqti bilan 14:00 — bu UTC boʻyicha 09:00.

**5.5. Hisoblash:**

```
python -m dustflow --katalog haqiqiy_malumot/stsenariylar --stsenariy boron_20250729
```

---

## 6. Qaysi sanalarni tanlash kerak

Validatsiya uchun ikki xil kun kerak:

**Changli kun** — shamol kuchli, havo quruq. Bunday kunlarni topishning eng oson yoʻli: avval CAMS maʼlumotini uzunroq davr uchun yuklab (masalan, bir oy), unda chang optik qalinligi (`duaod550`) eng yuqori boʻlgan kunlarni aniqlash.

**Sokin kun** — shamol kuchsiz. U fon konsentratsiyasini ajratish uchun kerak: kuzatilgan PM10 ning bir qismi transport va sanoatdan keladi, model esa faqat shamol eroziyasi hissasini hisoblaydi. Shuning uchun solishtirish **ortiqcha qiymat** boʻyicha olib boriladi:

$$C_{\text{model}} \approx C_{\text{kuzatuv}}(\text{changli kun}) - C_{\text{kuzatuv}}(\text{sokin kun})$$

Ikki kun bir-biriga yaqin boʻlishi kerak — bir haftadan oshmasin, aks holda fon oʻzgarib ketadi.

---

## 7. Eʼtibor berish kerak boʻlgan jihatlar

**7.1. ERA5-Land sugʻorishni hisobga olmaydi.** Bu eng muhim cheklov. ERA5-Land yer usti modelida sugʻorish jarayoni yoʻq, shuning uchun Zarafshon vohasidagi tuproq namligi haqiqatdagidan past chiqadi. Natijada model vohada ortiqcha emissiya berishi mumkin.

Qisman kompensatsiya allaqachon mavjud: ESA WorldCover'da ekinzorlar (40-sinf) uchun $A_{ef} = 0{,}05$ qabul qilingan, yaʼni namlik past boʻlsa ham emissiya cheklangan boʻladi. Lekin dissertatsiyada bu cheklovni ochiq yozish kerak.

**7.2. Namlik birliklari.** ERA5-Land hajmiy namlikni beradi (m³/m³), model esa ogʻirlik namligini (%) talab qiladi. Skript avtomatik oʻtkazadi:

$$w = \theta \cdot \frac{\rho_{\text{suv}}}{\rho_{\text{tuproq}}} \cdot 100\ \%$$

bu yerda tuproq zichligi $\rho_{\text{tuproq}}$ SoilGrids'dan olinadi. Masalan, $\theta = 0{,}08$ va $\rho = 1{,}45$ g/sm³ boʻlsa, $w = 5{,}5$ %.

**7.3. SoilGrids choʻlda ishonchsiz.** Buxoro viloyati boʻyicha tekshiruvda SoilGrids barcha yer qoplami sinflariga deyarli bir xil gil ulushini berdi (~0,30), jumladan yalangʻoch choʻlga ham. Qizilqum qumlari uchun bu haqiqatdan uch-olti barobar yuqori. Dezagregatsiya koeffitsiyenti gil ulushiga eksponensial bogʻliq boʻlgani uchun bu emissiyani 200 barobardan ortiq oshirib yuborardi. Shu sababli skript choʻl sinflari uchun adabiyotdagi qiymatlarni (yalangʻoch — 0,05, butazor va oʻtloq — 0,08) oladi, voha uchun SoilGrids saqlanadi. Bu qiymatlarni dala namunalari bilan aniqlashtirish maqsadga muvofiq.

**7.4. Yer qoplami statik.** ESA WorldCover 2021 yil holatini koʻrsatadi va mavsumiy oʻzgarishni bermaydi. Oʻsimlik qoplami $\lambda$ sinflar boʻyicha jadvaldan olinadi. Bitta boʻron hodisasini tekshirish uchun bu yetarli.

**7.5. CAMS — bu ham model.** U sunʼiy yoʻldosh kuzatuvlarini assimilyatsiya qiladi va xalqaro amaliyotda mos yozuvli maʼlumot sifatida keng qoʻllaniladi. Biroq dissertatsiyada buni «kuzatuv bilan validatsiya» emas, «modellararo taqqoslash» deb yozish kerak. Haqiqiy kuzatuv — `monitoring.meteo.uz` dagi Buxoro stansiyasi.

**7.6. Vaqt zonalari.** ERA5 va CAMS — UTC. `monitoring.meteo.uz` — mahalliy vaqt (UTC+5). Solishtirishda besh soatlik farqni unutmang.

---

## 8. Dissertatsiya matnida nimani oʻzgartirish kerak

Haqiqiy maʼlumotlar bilan hisoblashlarni qayta bajargach, quyidagilarni yangilash kerak:

§ 4.2 dagi 4.9-rasm ostidagi manba: «ERA5-Land, SoilGrids 2.0, Copernicus DEM GLO-90 va ESA WorldCover 2021 maʼlumotlari asosida».

Relyef manbasi: SRTM oʻrniga **Copernicus DEM GLO-90**.

Oʻsimlik qoplami manbasi: MODIS oʻrniga **ESA WorldCover 2021**.

Adabiyotlar roʻyxatiga qoʻshiladigan manbalar:

- Muñoz-Sabater J. et al. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications // Earth System Science Data. — 2021. — Vol. 13. — P. 4349–4383.
- Poggio L. et al. SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty // SOIL. — 2021. — Vol. 7. — P. 217–240.
- Zanaga D. et al. ESA WorldCover 10 m 2021 v200. — 2022. — DOI: 10.5281/zenodo.7254221.
- Inness A. et al. The CAMS reanalysis of atmospheric composition // Atmospheric Chemistry and Physics. — 2019. — Vol. 19. — P. 3515–3556.

---

## 9. Muammolar va yechimlar

| Xabar | Sababi | Yechim |
|---|---|---|
| `401 Unauthorized` | kalit notoʻgʻri | `.cdsapirc` ni tekshiring, kalit `UID:` prefiksisiz boʻlishi kerak |
| `403 Forbidden` / `required licences not accepted` | litsenziya qabul qilinmagan | 3.5-bandni bajaring |
| `kalit topilmadi` | `.cdsapirc` yoʻq | 3.3-bandni bajaring |
| `... faylda yoʻq` (stsenariy) | tanlangan soat yuklanmagan | `era5` ni kerakli sana bilan qayta ishga tushiring |
| rasterio oʻrnatilmaydi | Windows'da GDAL muammosi | `conda install -c conda-forge rasterio` |
| plitka «oʻtkazildi» | suv ustidagi plitka yoki tarmoq uzilishi | bir nechtasi normal; hammasi boʻlsa — internetni tekshiring |
| soʻrov soatlab «queued» | Copernicus navbati band | kuting yoki sanalar oraligʻini qisqartiring |

---

## 10. Katalog tuzilishi

Yuklangandan keyin:

```
haqiqiy_malumot/
├── statik/
│   ├── relyef.tif      Copernicus DEM
│   ├── tuproq.tif      SoilGrids, gil ulushi
│   ├── bdod.tif        SoilGrids, tuproq zichligi
│   ├── sinf.tif        ESA WorldCover sinflari
│   ├── z0.tif, qoplam.tif, A_ef.tif
├── era5/               ERA5-Land soatlik fayllar
├── cams/               CAMS validatsiya fayllari
└── stsenariylar/
    └── boron_20250729/ DustFlow uchun tayyor katalog
```
