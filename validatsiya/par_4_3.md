# § 4.3. Modelning adekvatligini baholash

Oldingi paragraflarda ishlab chiqilgan matematik model va dasturiy majmuaning ishonchliligi uch darajada tekshirildi. Birinchi daraja — verifikatsiya, ya'ni sonli sxema tenglamalarni to'g'ri yechishini tekshirish — uchinchi bobda bajarilgan: sxemaning ikkinchi tartibli yaqinlashishi va massa balansining $10^{-2}$ % dan yuqori aniqlikda bajarilishi ko'rsatilgan. Ushbu paragrafda qolgan ikki daraja bayon etiladi: modelning kirish parametrlariga sezgirligini baholash va model natijalarini mustaqil kuzatuv ma'lumotlari bilan solishtirish (validatsiya).

## Baholash usuli

Model natijalari O'zgidromet avtomatik monitoring stansiyalarining o'lchovlari bilan solishtirildi. Stansiya o'lchaydigan konsentratsiya shamol eroziyasi hissasidan tashqari transport, qurilish va sanoat hissasini ham o'z ichiga oladi, model esa faqat shamol eroziyasi changini hisoblaydi. Shu sababli solishtirish fondan ortiqcha konsentratsiya bo'yicha olib borildi:

$$C_{\text{model}}(t) \;\leftrightarrow\; C_{\text{kuzatuv}}(t) - C_{\text{fon}}, \qquad (4.7)$$

bu yerda $C_{\text{fon}}$ — hodisadan oldingi sokin haftadagi kuzatuvlar medianasi.

Moslik uchta ko'rsatkich bilan baholandi. Korrelyatsiya koeffitsiyenti $r$ model va kuzatuvning vaqt bo'yicha birga o'zgarishini ko'rsatadi:

$$r = \frac{\sum_i (M_i - \overline{M})(O_i - \overline{O})}{\sqrt{\sum_i (M_i - \overline{M})^2 \, \sum_i (O_i - \overline{O})^2}}. \qquad (4.8)$$

Normallashtirilgan o'rtacha siljish model qanchalik yuqori yoki past baholashini foizda beradi:

$$\mathrm{NMB} = \frac{\sum_i (M_i - O_i)}{\sum_i O_i} \cdot 100\,\%. \qquad (4.9)$$

FAC2 ko'rsatkichi model qiymatlarining qancha qismi kuzatuvdan ikki barobardan ortiq farq qilmasligini ko'rsatadi:

$$\mathrm{FAC2} = \frac{1}{n}\,\#\left\{ i : 0{,}5 \leq \frac{M_i}{O_i} \leq 2 \right\}. \qquad (4.10)$$

Bu yerda $M_i$ va $O_i$ — model va kuzatuv qiymatlari. Mos yozuv sifatida atmosfera modellarini baholashda xalqaro amaliyotda qabul qilingan Chang–Hanna chegaralari [Chang, Hanna, 2004] qo'llanildi: FAC2 > 0,5, fraksion siljish $|\mathrm{FB}| < 0{,}3$ va normallashtirilgan o'rtacha kvadratik xatolik NMSE < 1,5. To'liq mezonlar to'plami ilovada keltirilgan; ular DustFlow majmuasining `validatsiya` modulida amalga oshirilgan.

Tajribalardan oldin sozlamalar, baholash usuli va kutilayotgan natijalar hujjatga yozib qo'yildi va keyin o'zgartirilmadi [Nosek va boshq., 2018]. Hujjatlarning raqamli izi SHA-256 algoritmi bilan olingan. Bu natijaga moslab qaror qabul qilish ehtimolini bartaraf etadi; barcha natijalar, jumladan salbiylari ham, keltirildi.

## Modelning parametrlarga sezgirligi

Sezgirlik tahlili 2025-yil 29-aprel 09:00 UTC dagi chang bo'roni uchun haqiqiy kirish maydonlarida (4.9-rasm) bajarildi. Har bir parametr bazaviy qiymatidan $\pm 25$ % ga o'zgartirilib, yer sirtidagi o'rtacha konsentratsiyaning nisbiy o'zgarishi o'lchandi. Sezgirlik indeksi quyidagicha aniqlandi:

$$S_p = \frac{\max\left( |\Delta C^{+}|,\, |\Delta C^{-}| \right) / \overline{C}}{|\Delta p| / p}. \qquad (4.11)$$

**4.9-jadval.** Modelning kirish parametrlariga sezgirligi

| Parametr | $-25$ % | $+25$ % | $S_p$ |
|---|---|---|---|
| Shamol tezligi $U_{10}$ | −76,4 % | +150,0 % | 6,00 |
| Gil ulushi $m_{cl}$ | −66,8 % | +109,9 % | 4,40 |
| Tuproq namligi $w$ | +29,0 % | −29,0 % | 1,16 |
| Eroziyaga beriluvchan yuza $A_{ef}$ | −25,0 % | +25,0 % | 1,00 |
| G'adir-budurlik uzunligi $z_0$ | −22,0 % | +20,7 % | 0,88 |
| O'simlik qoplami $\lambda$ | +11,6 % | −11,7 % | 0,47 |
| Relyef balandligi $\eta$ | +0,1 % | +0,3 % | 0,01 |

![](/mnt/user-data/outputs/rasm_4_20_sezgirlik.png){width=15.5cm}

**4.16-rasm.** Modelning kirish parametrlariga sezgirligi.

Jadvalning ikkinchi va uchinchi ustunlarida konsentratsiyaning o'zgarishi keltirilgan: musbat qiymat konsentratsiyaning oshishini, manfiy — kamayishini bildiradi. Shamol tezligi, gil ulushi, $A_{ef}$ va $z_0$ uchun belgilar parametrning o'zgarishi bilan bir xil — bu to'g'ri bog'liqlik. Tuproq namligi va o'simlik qoplami uchun belgilar teskari: ular eroziya chegarasini oshirib, emissiyani kamaytiradi. $S_p$ esa ta'sirning kuchini ko'rsatadi va doim musbat.

Natijaga ikki parametr hal qiluvchi ta'sir ko'rsatadi. Shamol tezligining 25 % ga oshishi konsentratsiyani 2,5 barobar oshiradi — bu gorizontal oqimdagi kubik bog'liqlik va emissiyaning chegaraviy xususiyati birgalikdagi ta'siridir. Gil ulushining ta'siri ($S_p = 4{,}4$) dezagregatsiya koeffitsiyentining unga eksponensial bog'liqligidan kelib chiqadi. $A_{ef}$ uchun $S_p$ aniq birga teng, bu emissiyaning shu parametrga chiziqli bog'liqligini tasdiqlovchi nazorat natijasidir. Relyef ta'siri amalda yo'q, bu hududning tekisligi bilan izohlanadi.

## Kirish va kuzatuv ma'lumotlari

Barcha kirish maydonlari ochiq xalqaro ma'lumotlar bazalaridan olindi; ularni yuklab olish va hisoblash to'riga keltirish usullari § 4.2 da bayon etilgan.

**4.10-jadval.** Kirish va kuzatuv ma'lumotlarining manbalari

| Maydon | Manba | Aniqlik |
|---|---|---|
| Shamol, harorat, tuproq namligi | ERA5-Land [Muñoz-Sabater va boshq., 2021] | 0,1°, soatlik |
| Gil ulushi, tuproq zichligi | SoilGrids 2.0 [Poggio va boshq., 2021] | 250 m |
| Relyef | Copernicus DEM GLO-90 | 90 m |
| Yer qoplami → $z_0$, $\lambda$, $A_{ef}$ | ESA WorldCover 2021 [Zanaga va boshq., 2022] | 10 m |
| Chang, PM10, PM2.5 (reanaliz) | CAMS EAC4 [Inness va boshq., 2019] | 0,75°, 3 soatlik |
| PM10, PM2.5 (kuzatuv) | O'zgidromet avtomatik stansiyalari | nuqta, soatlik |

ERA5-Land hajmiy namlikni $\theta$ beradi, emissiya sxemasi esa og'irlik namligini talab qiladi; o'tkazish tuproq zichligi $\rho_b$ orqali bajarildi:

$$w = \theta \, \frac{\rho_{\text{suv}}}{\rho_b} \cdot 100\,\%. \qquad (4.12)$$

Ma'lumotlarni tayyorlashda ikki muhim masala aniqlandi. Birinchisi — SoilGrids ning ishonchliligi (4.11-jadval).

**4.11-jadval.** SoilGrids 2.0 bo'yicha 0–5 sm qatlam tavsiflari (medianalar, %)

| Yer qoplami sinfi | Maydon ulushi | Qum | Gil | Gil, 5 % kvantil | Gil, 95 % kvantil |
|---|---|---|---|---|---|
| Yalang'och va siyrak o'simlikli | 71,7 % | 25,3 | 30,5 | 1,8 | 80,7 |
| O'tloq | 15,4 % | 30,5 | 29,4 | 2,3 | 78,6 |
| Ekinzor | 9,0 % | 31,1 | 29,4 | 1,9 | 79,6 |
| Butazor | 2,1 % | 28,7 | 30,6 | 1,7 | 81,4 |
| Qurilgan hudud | 0,7 % | 31,8 | 29,0 | 2,1 | 78,7 |

SoilGrids Qizilqum cho'liga 25 % qum va 30 % gil beradi — bu qumli cho'lga emas, og'ir qumoq tuproqqa mos. U barcha sinflarga deyarli bir xil qiymat beradi, gil ulushining 90 % bashorat oralig'i esa 2 % dan 80 % gacha, ya'ni bu hududda ma'lumot amalda yo'q. Gil ulushi eng sezgir parametrlardan biri bo'lgani uchun aralash yondashuv qabul qilindi: yalang'och yuzalar uchun 0,05, butazor va o'tloq uchun 0,08 (Qizilqum qumli tuproqlari uchun adabiyotdagi 2–10 % oralig'i asosida), boshqa sinflar uchun SoilGrids qiymatlari. Tanlangan qiymat SoilGrids'ning o'z 90 % oralig'i ichida yotadi.

Ikkinchi masala — sug'oriladigan yerlar. ERA5-Land modelida sug'orish ifodalanmagan, shu sababli vohadagi tuproq namligi haqiqatdagidan past chiqadi va birinchi hisoblashda hududning 8 % ini egallagan ekinzorlar emissiyaning 56 % ini bergan. Chang modellarida qabul qilinganidek, sug'oriladigan ekinzorlar vegetatsiya mavsumida eroziya manbalari tarkibidan chiqarildi. Bu qaror fizik asos bo'yicha qabul qilingan: u keyinchalik reanaliz bilan moslik ko'rsatkichlarini hatto yomonlashtirdi.

Kuzatuv ma'lumotlari sifatida hisoblash hududi ichidagi uchta avtomatik stansiyaning soatlik o'lchovlari olindi (4.12-jadval). Ular O'zgidromet «DigitalMeteo» portalining arxividan yuklab olindi. Manba mustaqil tekshirildi: portal arxividagi qiymatlar O'zgidromet ma'lumotlariga tayangan holda ommaviy axborot vositalarida e'lon qilingan qiymatlarga to'liq mos keldi.

**4.12-jadval.** Hisoblash hududidagi avtomatik stansiyalar

| Stansiya | Kenglik | Uzunlik | Qamrov, 2025-yil aprel |
|---|---|---|---|
| Buxoro | 39,7762° N | 64,4197° E | 100 % |
| Navoiy | 40,0824° N | 65,3751° E | 98 % |
| Qarshi | 38,8239° N | 65,7658° E | 99 % |

Taqqoslash uchun 2025-yil 28–30-aprel chang bo'roni tanlandi. U CAMS reanalizida mart–may davridagi eng kuchli hodisa bo'lgan va O'zgidromet xabarlari bilan tasdiqlangan. Stansiyalar va CAMS ning ushbu davrdagi qiymatlari 4.17-rasmda keltirilgan.

![](/mnt/user-data/outputs/rasm_4_25_kuzatuvlar.png){width=16cm}

**4.17-rasm.** Avtomatik stansiyalar kuzatuvlari va CAMS reanalizi: a — Buxoro; b — uchta stansiya; c — PM2.5/PM10 nisbati; d — 2026-yil fevral hodisasi.

## Stansiya, DustFlow va CAMS taqqoslanishi

Modelning natijalari kuzatuv bilan bir vaqtda xalqaro CAMS reanalizi bilan ham solishtirildi. CAMS — Yevropa Ittifoqi Kopernik dasturining operativ atmosfera tarkibi tizimi bo'lib, sun'iy yo'ldosh kuzatuvlarini o'zlashtiradi; u bu yerda muqobil model sifatida qaraladi. Taqqoslash adolatli bo'lishi uchun uchala manba bir xil asosga keltirildi: bir xil davr (28-aprel 00:00 – 30-aprel 21:00 UTC), bir xil vaqt nuqtalari (CAMS ning 3 soatlik vaqtlari) va fonni ayirishning bir xil qoidasi (kuzatuv va CAMS uchun alohida, 20–26-aprel medianasi). DustFlow vaqt bo'yicha o'zgaruvchan ERA5-Land majburlashi bilan ikki variantda hisoblandi: yon chegaralarda CAMS dan olingan fon konsentratsiyasi bilan va faqat mahalliy emissiya bilan. Natijalar 4.13-jadval va 4.18-rasmda keltirilgan.

**4.13-jadval.** Stansiya kuzatuvlari bilan taqqoslash (3 stansiya, 71 juftlik)

| Ko'rsatkich | DustFlow, chegara bilan | DustFlow, mahalliy | CAMS |
|---|---|---|---|
| Korrelyatsiya $r$ | 0,22 | 0,20 | 0,20 |
| NMB | +46 % | −32 % | +26 % |
| FAC2 | 0,27 | 0,11 | 0,24 |
| $\lvert\mathrm{FB}\rvert$ | 0,37 | 0,38 | 0,23 |
| NMSE | 2,94 | 4,22 | 2,52 |
| Buxoro: $r$ | 0,56 | 0,50 | 0,64 |
| Bo'ron kunidagi ortiqcha PM10, Buxoro (kuzatuv 300), µg/m³ | 662 | 427 | 516 |
| Bo'ron kunidagi ortiqcha PM10, Navoiy (kuzatuv 112), µg/m³ | 253 | 8 | 285 |
| Bo'ron kunidagi ortiqcha PM10, Qarshi (kuzatuv 190), µg/m³ | 62 | 6 | 34 |
| Bo'rondagi PM2.5/PM10, Buxoro (kuzatuv 0,16) | 0,23 | 0,13 | 0,48 |

![](/mnt/user-data/outputs/rasm_4_uch_tomonlama.png){width=16cm}

**4.18-rasm.** Stansiya kuzatuvlari, DustFlow va CAMS: a–c — Buxoro, Navoiy, Qarshi; d — umumiy ko'rsatkichlar va Chang–Hanna chegaralari; e — bo'rondagi zarracha o'lchami.

Natijalardan uchta asosiy xulosa kelib chiqadi.

Birinchidan, shahar stansiyalaridagi soatlik chang konsentratsiyasini takrorlash — operativ xalqaro tizim uchun ham qiyin vazifa. Bir xil asosda CAMS ham Chang–Hanna mezonlarini bajarmaydi (FAC2 = 0,24; NMSE = 2,52). DustFlow ning chegaraviy shartli varianti ko'rsatkichlari CAMS bilan bir tartibda: korrelyatsiya va FAC2 bo'yicha biroz yuqori, o'rtacha siljish bo'yicha biroz past. Ya'ni DustFlow chang tarqalishini mintaqaviy miqyosdagi xalqaro operativ tizim darajasida baholaydi.

Ikkinchidan, zarrachalar o'lchami tarkibi bo'yicha DustFlow CAMS dan aniqroq. Bo'ron kuni Buxoro stansiyasida PM2.5/PM10 nisbati soatlar bo'yicha 0,13–0,21 oralig'ida bo'lgan. Faqat mahalliy emissiyali DustFlow (0,13) shu oraliq ichida, CAMS (0,48) esa undan ikki barobardan ko'proq yuqori. Kuzatuv ko'rsatadiki, mintaqadagi chang yirik mineral zarrachalardan iborat, CAMS esa mayda fraksiyani ortiqcha beradi. Chegaraviy shartli variantda nisbat 0,23 ga oshadi — chegaradan CAMS changi kiradi.

Uchinchidan, Buxoroda ikkala model ham bo'ronning vaqtini yaxshi takrorlaydi ($r$ = 0,56 va 0,64) va konsentratsiyani oshirib baholaydi. Bo'ron kunida faqat mahalliy emissiyali DustFlow kuzatuvdan 1,4 barobar, CAMS 1,7 barobar, chegaraviy shartli DustFlow 2,2 barobar yuqori. Qarshi stansiyasida esa hech bir model kuzatuvni takrorlamaydi: u yerda bo'rondan mustaqil ravishda har kuni kechqurun takrorlanadigan cho'qqilar bor, bu mahalliy shahar manbalariga ishora qiladi.

Oldindan qayd etilgan soatlik baholashda (211 juftlik) ham shu manzara olindi: chegaraviy shartli variant uchun $r$ = 0,28, NMB = +62 %, FAC2 = 0,23, Chang–Hanna mezonlari bajarilmadi; oldindan yozilgan yettita bashoratdan to'rttasi bajarildi. To'liq natijalar ilovada (I-2 va I-3-jadvallar).

## Hudud bo'yicha taqqoslash va tashqaridan kiruvchi chang

Model CAMS bilan fazoviy maydon bo'yicha ham solishtirildi (29-aprel 09:00 UTC, CAMS ning $0{,}75^\circ$ li to'rida). Yon chegaralarda fon konsentratsiyasi nolga teng bo'lgan birinchi hisoblashda model hudud bo'yicha o'rtacha 68 % past baholadi. Sabab aniqlandi: shamol shimoldan esgan va CAMS ma'lumotlarida chang hududning shimoliy chegarasidan kirib kelmoqda, modelda esa chegaradan kirish bo'lmagan (4.19-rasm).

![](/mnt/user-data/outputs/rasm_4_23_taqqoslash.png){width=16cm}

**4.19-rasm.** 2025-yil 29-aprel 09:00 UTC: a — CAMS bo'yicha fondan ortiqcha PM10; b — DustFlow (chegaradan kirishsiz), CAMS to'riga o'rtalangan; c — DustFlow, to'liq aniqlik. Strelkalar — ERA5-Land shamoli.

Shu sababli yechuvchi yon chegaralarda joy bo'yicha o'zgaruvchan fon konsentratsiyasini (2.31 shartidagi $C_b$) qabul qiladigan qilib kengaytirildi, massa balansi esa chegara orqali sof oqimni hisobga oladigan qilib tuzatildi (test masalasida balans 0,0026 %). $C_b$ CAMS dan olinganda o'rtacha siljish −68 % dan −29 % ga, FAC2 0,20 dan 0,53 ga yaxshilandi; bu yaxshilanish chegara qatlami balandligining sinalgan uchala qiymatida ham kuzatildi (I-1-jadval). Natijadan muhim xulosa kelib chiqadi: bu bo'ron paytida viloyat ustidagi changning taxminan yarmi (45–52 %) mahalliy emissiyadan, qolgan qismi hududdan tashqaridan kelgan.

## Natijalarning kattalik tartibi bo'yicha tekshiruvi

O'zbekiston Statistika agentligi ma'lumotlariga ko'ra, Buxoro viloyatida atmosferaga chiqarilgan ifloslantiruvchi moddalar 2010-yildagi 75,5 ming tonnadan 2025-yilda 27,1 ming tonnagacha kamaygan. Bu ko'rsatkich gazsimon moddalarni ham o'z ichiga oladi; qattiq zarrachalar ulushini 15 % deb baholasak, u yiliga taxminan 4 ming tonnani tashkil etadi.

Hisoblash sohasi Buxoro viloyati bilan birga unga tutash hududlarni ham qamraydi (taxminan 153 ming km², viloyat — 40 ming km²), shu sababli taqqoslash uchun emissiya viloyat chegarasi ichida alohida hisoblandi. 2025-yil 28–29-aprel bo'roni davomida viloyat hududidan model bo'yicha 532 ming tonna chang ko'tarilgan (butun sohadan — 976 ming tonna), uning 38 % i PM10 fraksiyasiga to'g'ri keladi. Birlik maydonga hisoblaganda bu taxminan 13 t/km² ni tashkil etadi — Orolqumning yillik o'rtacha jadalligining (~450 t/km²) 3 % i atrofida, ya'ni kuchli bo'ron uchun fizik jihatdan mumkin bo'lgan kattalik. Buxoroda model konsentratsiyani oshirib baholashini hisobga olib, pastki chegara sifatida uning uchdan bir qismi — 177 ming tonna olinadi. Hatto shu chegarada ham bitta bo'ron viloyat sanoatining yillik qattiq zarracha chiqindisidan 40 barobardan ko'p modda atmosferaga kiritadi (4.20-rasm).

![](/mnt/user-data/outputs/rasm_4_21_statistika.png){width=15.5cm}

**4.20-rasm.** Buxoro viloyatida qayd etilgan emissiya va viloyat hududidagi shamol eroziyasi emissiyasining kattalik tartibi bo'yicha taqqoslanishi.

Sanoat chiqindisi yil davomida uzluksiz, shamol eroziyasi esa epizodik bo'lgani va changning katta qismi manba yaqinida qayta cho'kkani sababli gap zararning emas, atmosferaga kiritiladigan modda miqdorining taqqoslanishi haqida bormoqda. Shunga qaramay natija amaliy ahamiyatga ega: ekologik nazorat tizimi hisobga olinadigan statsionar manbalarga yo'naltirilgan, kattaligi bo'yicha ulardan ancha ustun turuvchi tabiiy manba esa e'tibordan chetda qolmoqda. Taqqoslash uchun, mintaqadagi eng yirik antropogen chang manbai — Orolqumdan yiliga taxminan 27 mln tonna chang ko'tariladi [Banks va boshq., 2022].

## Modelning cheklovlari

Birinchidan, Buxoro stansiyasida model konsentratsiyani oshirib baholaydi (bo'ron kunida 1,4–2,2 barobar), Navoiy stansiyasida esa xatolik ancha kichik (+47 %). Bu xatolikning fazoviy sababi 4.11-rasmdan ko'rinadi: hududdagi eng faol emissiya manbalari Buxoro vohasining shimoliy chekkasida, stansiyaning shamol yo'nalishidagi bevosita yuqori oqimida joylashgan, shu sababli Buxoro yacheykasidagi natija bir necha manbaning emissiya bahosiga eng sezgir. Bundan tashqari, stansiya shahar ichida joylashgan, model esa cho'l yerlarini ham o'z ichiga olgan 6 km li yacheykaning o'rtacha qiymatini beradi. Shunga o'xshash oshirib baholash CAMS da ham kuzatiladi (1,7 barobar). Bu xatolikni emissiya koeffitsiyentini mustaqil hodisalar bo'yicha kalibrlash va stansiya atrofida hisoblash to'rini maydalash orqali kamaytirish mumkin.

Ikkinchidan, bo'ron tugagach model changni kuzatuvdagidan sekinroq tarqatadi, bu chegara qatlamining sutkalik o'zgarishi va cho'kish jarayonlarining soddalashtirilgan ifodalanishiga ishora qiladi.

Uchinchidan, hududdan tashqaridan keluvchi chang natijaga sezilarli hissa qo'shadi. U CAMS orqali hisobga olinishi mumkin, lekin CAMS ning o'zi bu hududda fonni ikki barobar past va mayda fraksiyani ortiqcha beradi.

To'rtinchidan, ERA5-Land ning tuproq namligi va shamol maydonlari eroziya uchun hal qiluvchi ko'rsatkichlarni — ustki qatlam namligini va shamol zarbalarini — yetarli aniqlikda bermaydi. Qo'shimcha tekshiruv ko'rsatdiki, qishki sharoitda (2026-yil fevral) ERA5-Land bo'yicha cho'l tuprog'ining namligi 22,5 % bo'lganda model emissiya bermaydi, Buxoro stansiyasida esa bu vaqtda kuchli chang hodisasi qayd etilgan. Bu tekshiruv oldindan qayd etish hujjatida to'liq keltirilgan.

Beshinchidan, cho'l tuproqlaridagi gil ulushi adabiyot ma'lumotlari asosida qabul qilingan, u esa sezgirligi eng yuqori parametrlardan biri. Oltinchidan, shahar ichidagi mahalliy chang manbalari — transport, qurilish, yopilmagan yuzalar — modelda ifodalanmagan.

Shunday qilib, ushbu paragrafda modelning adekvatligi sezgirlik tahlili, stansiya kuzatuvlari va CAMS reanalizi bilan taqqoslash hamda rasmiy statistika bilan kattalik tartibi bo'yicha solishtirish orqali baholandi. Sezgirlik tahlili natijaga shamol tezligi va tuproqdagi gil ulushi hal qiluvchi ta'sir ko'rsatishini aniqladi. Global tuproq ma'lumotlar bazasi Markaziy Osiyo cho'llarida ishonchsiz ekanligi ko'rsatildi va aralash yondashuv asoslandi. Bir xil asosdagi taqqoslash ko'rsatdiki, shahar stansiyalaridagi soatlik chang konsentratsiyasini na DustFlow, na operativ CAMS tizimi Chang–Hanna mezonlari darajasida takrorlamaydi, DustFlow ning ko'rsatkichlari esa CAMS bilan bir tartibda. Model chang bo'ronining paydo bo'lishini, vaqtini va zarrachalar o'lchami tarkibini to'g'ri takrorlaydi, zarracha tarkibi bo'yicha esa CAMS dan aniqroq. Bo'ron paytida hudud ustidagi changning taxminan yarmi tashqaridan kelishi aniqlandi. Modelning cheklovlari va ularni bartaraf etish yo'llari ko'rsatildi.

## § 4.3 ga ilova

**To'liq baholash mezonlari.** Asosiy matndagi (4.8)–(4.10) ko'rsatkichlardan tashqari quyidagilar hisoblandi:

$$\mathrm{MB} = \overline{M - O}, \qquad \mathrm{NMSE} = \frac{\overline{(M - O)^2}}{\overline{M}\;\overline{O}}, \qquad \mathrm{FB} = \frac{2\,(\overline{O} - \overline{M})}{\overline{O} + \overline{M}}, \qquad (\mathrm{I}.1)$$

$$d = 1 - \frac{\sum_i (M_i - O_i)^2}{\sum_i \left( |M_i - \overline{O}| + |O_i - \overline{O}| \right)^2}. \qquad (\mathrm{I}.2)$$

$\mathrm{FB} > 0$ bo'lganda model past baholaydi, $\mathrm{FB} < 0$ bo'lganda — yuqori. Chang–Hanna shartlari: $|\mathrm{FB}| < 0{,}3$, $\mathrm{NMSE} < 1{,}5$, $\mathrm{FAC2} > 0{,}5$ (bir vaqtda).

**I-1-jadval.** CAMS bilan fazoviy taqqoslash, 15 ta ichki yacheyka (oldindan qayd etilgan № 1)

| Variant | FB | NMSE | FAC2 | $r$ | NMB |
|---|---|---|---|---|---|
| $C_b = 0$ | 1,02 | 1,97 | 0,20 | 0,07 | −68 % |
| $H$ = 1000 m | 0,47 | 0,53 | 0,47 | 0,06 | −38 % |
| $H$ = 1500 m (asosiy) | 0,34 | 0,38 | 0,53 | 0,07 | −29 % |
| $H$ = 2500 m | 0,32 | 0,37 | 0,67 | 0,08 | −28 % |

**I-2-jadval.** Stansiyalar bilan soatlik taqqoslash (oldindan qayd etilgan № 2, 211 juftlik)

| | FB | NMSE | FAC2 | $r$ | NMB |
|---|---|---|---|---|---|
| Chegara bilan, uchala stansiya | −0,48 | 2,71 | 0,23 | 0,28 | +62 % |
| — Buxoro | −1,07 | 2,95 | 0,16 | 0,58 | +230 % |
| — Navoiy | −0,39 | 1,84 | 0,23 | 0,33 | +49 % |
| — Qarshi | 0,71 | 2,93 | 0,29 | −0,07 | −53 % |
| Mahalliy, uchala stansiya | 0,26 | 3,32 | 0,11 | 0,25 | −23 % |
| — Buxoro | −0,72 | 1,74 | 0,23 | 0,53 | +113 % |
| — Navoiy | 1,86 | 51,6 | 0,00 | 0,48 | −96 % |
| — Qarshi | 1,60 | 16,1 | 0,10 | −0,07 | −89 % |

**I-3-jadval.** Oldindan qayd etilgan bashoratlar (chegaraviy shartli variant)

| Bashorat | Natija | |
|---|---|---|
| Buxorodagi maksimum kuzatuvdagidan ±3 soat ichida | 12:00 UTC (kuzatuv 15:00) | bajarildi |
| Soatlik taqqoslash Chang–Hanna mezonlaridan o'tmaydi | o'tmadi | bajarildi |
| Soatlik FAC2 = 0,25–0,5 | 0,23 | bajarilmadi |
| Soatlik $r$ = 0,2–0,6 | 0,28 | bajarildi |
| Kunlik o'rtachalar bo'yicha FAC2 ≥ 0,5 | 0,33 | bajarilmadi |
| Buxorodagi PM2.5/PM10 = 0,10–0,20 | 0,226 | bajarilmadi |
| Mahalliy variantning siljishi chegaraviy variantnikidan kichik | −23 % < +62 % | bajarildi |

## § 4.3 uchun yangi adabiyotlar

*Umumiy ro'yxatga raqamlab kiritiladi; bibliografik ma'lumotlar asl manba bilan solishtirilishi kerak.*

- Chang J.C., Hanna S.R. Air quality model performance evaluation // Meteorology and Atmospheric Physics. — 2004. — Vol. 87. — P. 167–196.
- Nosek B.A., Ebersole C.R., DeHaven A.C., Mellor D.T. The preregistration revolution // Proceedings of the National Academy of Sciences. — 2018. — Vol. 115, No. 11. — P. 2600–2606.
- Willmott C.J. On the validation of models // Physical Geography. — 1981. — Vol. 2, No. 2. — P. 184–194.
- Muñoz-Sabater J. et al. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications // Earth System Science Data. — 2021. — Vol. 13. — P. 4349–4383.
- Poggio L. et al. SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty // SOIL. — 2021. — Vol. 7. — P. 217–240.
- Zanaga D. et al. ESA WorldCover 10 m 2021 v200. — 2022. — DOI: 10.5281/zenodo.7254221.
- Inness A. et al. The CAMS reanalysis of atmospheric composition // Atmospheric Chemistry and Physics. — 2019. — Vol. 19. — P. 3515–3556.
- Banks J.R., Heinold B., Schepanski K. Impacts of the desiccation of the Aral Sea on the Central Asian dust life-cycle // Journal of Geophysical Research: Atmospheres. — 2022. — Vol. 127.
- European Space Agency. Copernicus DEM GLO-90. — 2021.
- O'zbekiston Respublikasi Statistika agentligi. Atmosferaga chiqarilgan ifloslantiruvchi moddalar (1569-ko'rsatkich). — siat.stat.uz.
- O'zbekiston Respublikasi Gidrometeorologiya xizmati agentligi. «DigitalMeteo» yagona iqlim ma'lumotlari portali. — air-uzbekistan.uz.
