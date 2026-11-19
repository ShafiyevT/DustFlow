# § 4.4. Hisoblash tajribasi: Buxoro shahridagi qurilish maydoni

Oldingi paragrafda modelning cheklovlaridan biri sifatida shahar ichidagi mahalliy chang manbalari — transport, qurilish, yopilmagan yuzalar — mintaqaviy hisoblashda ifodalanmasligi qayd etildi. Ushbu paragrafda DustFlow majmuasining shunday lokal manbaga qo'llanilishi ko'rsatiladi. Hisoblash tajribasi uchun Buxoro shahridagi yirik qurilish maydoni tanlandi. Maydon 39,7682° N, 64,4252° E nuqtada joylashgan, uning maydoni 22,7 ga (226 915 m²). U O'zgidromet Buxoro avtomatik stansiyasidan taxminan 1 km janubi-sharqda joylashgan, bu esa hisoblash natijalarini kuzatuv tarmog'i bilan bog'lash imkonini beradi.

Tajribaning maqsadi uchta savolga javob berish: haqiqiy chang bo'roni sharoitida qurilish maydoni qancha chang chiqaradi; bu chang qanday masofaga tarqaladi va sanitariya me'yorlari qayerda buziladi; qanday tadbirlar emissiyani kamaytiradi.

## Kirish ma'lumotlari

Meteorologik sharoit sifatida § 4.3 da tahlil qilingan 2025-yil 28–29-aprel chang bo'roni olindi. Shamol, harorat va tuproq namligi ERA5-Land reanalizidan maydonning o'z koordinatasiga ikki chiziqli interpolyatsiya yo'li bilan soatma-soat olindi. Bo'ron davomida maydonda shamol tezligi 10,3 m/s gacha yetgan (29-aprel 11:00 UTC), 29-aprelda shamol asosan shimoli-shimoli-sharqdan (medianasi 14°) o'rtacha 9,0 m/s tezlikda esgan.

Maydon tuprog'ining tarkibi bo'yicha muhim masala aniqlandi. SoilGrids ma'lumotlar bazasi shahar hududlarini maskalaydi, shu sababli maydon nuqtasi uchun gil ulushining ishonchli qiymati mavjud emas. Sezgirlik tahlili (4.9-jadval) gil ulushini eng ta'sirchan parametrlardan biri ekanini ko'rsatgani uchun u noaniq parametr sifatida qaraldi va hisoblash Buxoro vohasining qumoq tuproqlari uchun xos bo'lgan 0,05–0,20 oralig'ida bajarildi. Qurilish maydoni sirtining holati ham noma'lum, u tadbirlarga bog'liq; shu sababli uchta holat qaraldi: quruq buzilgan grunt (namlik 1 %), ERA5-Land bo'yicha tuproq namligi (4,8–14 %) va chang bostirish maqsadida namlangan sirt (15 %). Kirish parametrlari va ularning manbalari 4.14-jadvalda keltirilgan.

**4.14-jadval.** Qurilish maydoni uchun kirish parametrlari

| Parametr | Qiymat | Manba |
|---|---|---|
| Joylashuvi, maydoni | 39,7682° N, 64,4252° E; 22,7 ga | xarita bo'yicha o'lchangan |
| Shamol $U_{10}$, yo'nalish | 0,2–10,3 m/s, soatlik | ERA5-Land |
| Tuproq namligi $w$ | 1 %; 4,8–14 %; 15 % | uch holat: quruq, ERA5-Land, namlangan |
| Gil ulushi $m_{cl}$ | 0,05; 0,10; 0,15; 0,20 | noaniq parametr, oraliq |
| Tuproq zichligi $\rho_b$ | 1,43 g/sm³ | SoilGrids 2.0 |
| Eroziyaga beriluvchan ulush $A_{ef}$ | 0,8 | qabul qilingan (buzilgan yuza) |
| G'adir-budurlik uzunligi $z_0$ | $10^{-3}$ m | qabul qilingan (yalang'och grunt) |

## Emissiya

Emissiya oqimi ikkinchi bobdagi sxema bo'yicha har bir soat uchun hisoblandi. Bo'ron davomida (28-aprel 16:00 – 29-aprel 23:00 UTC, 32 soat) maydondan ko'tarilgan chang massasi 4.15-jadval va 4.21-rasmda keltirilgan.

**4.15-jadval.** Bo'ron davomida qurilish maydonidan ko'tarilgan chang, t

| Gil ulushi | Quruq grunt | ERA5-Land namligi | Namlangan sirt |
|---|---|---|---|
| 0,05 | 1,5 | 0 | 0 |
| 0,10 | 8,1 | 0 | 0 |
| 0,15 | 38,0 | 2,1 | 0 |
| 0,20 | 177,5 | 70,4 | 0 |

![](/mnt/user-data/outputs/rasm_4_21_qurilish_emissiya.png){width=16cm}

**4.21-rasm.** Qurilish maydonidan chang emissiyasi: a — soatlik emissiya va ERA5-Land shamoli; b — bo'ron davomidagi emissiyaning gil ulushi va sirt holatiga bog'liqligi.

Natijalardan uchta xulosa kelib chiqadi.

Birinchidan, emissiya gil ulushiga juda kuchli bog'liq: 0,05 dan 0,20 gacha oraliqda u yuz barobardan ko'proq o'zgaradi. Bu dezagregatsiya koeffitsiyentining gil ulushiga eksponensial bog'liqligidan kelib chiqadi va sezgirlik tahlili natijasini aniq amaliy misolda tasdiqlaydi. Demak qurilish maydonlarining changlanish xavfini baholashda tuproq namunasini olib, uning mexanik tarkibini aniqlash zarur.

Ikkinchidan, sirtni namlash emissiyani barcha holatlarda to'liq bartaraf etadi. Namlik 15 % bo'lganda chegaraviy dinamik tezlik bo'ron davomidagi eng kuchli shamolda ham yetib bo'lmaydigan darajaga ko'tariladi. ERA5-Land bo'yicha tabiiy namlik (4,8–14 %) ham emissiyani quruq gruntga nisbatan 3–18 barobar kamaytiradi. Bu natija qurilish maydonlarida chang bostirish tadbirining samaradorligini miqdoriy asoslaydi.

Uchinchidan, emissiya shamol tezligiga kuchli bog'liq: markaziy holatda (quruq grunt, gil 0,15) eroziya 32 soatdan 28 tasida sodir bo'lgan, emissiyaning maksimumi 2,1 t/soat shamol eng kuchli bo'lgan 29-aprel 11:00 UTC ga to'g'ri keladi. Agar shahar qurilmalari shamolni 30 % ga pasaytirsa, markaziy holatdagi emissiya 38,0 tonnadan 5,9 tonnagacha kamayadi.

## Changning tarqalishi

Changning maydon atrofida tarqalishi markaziy holat — quruq grunt, gil ulushi 0,15 — uchun hisoblandi. Maydon markazida $20 \times 20$ km li lokal hisoblash sohasi qurildi: gorizontal to'r $64 \times 64$ ($\Delta x = \Delta y = 312{,}5$ m), vertikal bo'yicha 2 km balandlik 12 qatlamga bo'lindi, vaqt qadami $\Delta t = 25$ s. Shamol maydoni har soatda ERA5-Land ning maydon nuqtasidagi qiymati bo'yicha yangilandi. Manba sifatida faqat qurilish maydoni olindi. Uning maydoni to'rning $n = 4$ ta yacheykasiga to'g'ri keladi; umumiy emissiya saqlanishi uchun ulardagi eroziyaga beriluvchan ulush quyidagicha olindi:

$$A_{ef}^{\text{kat}} = A_{ef} \, \frac{S}{n \, \Delta x \, \Delta y}, \qquad (4.13)$$

bu yerda $S$ — qurilish maydonining maydoni. Hisoblashda massa balansi 0,0006 % aniqlikda bajarildi. Natijalar 4.16-jadval va 4.22-rasmda keltirilgan.

**4.16-jadval.** Qurilish maydonidan tarqalgan chang (markaziy holat, 32 soat)

| Ko'rsatkich | Qiymat |
|---|---|
| Ko'tarilgan chang | 38,0 t |
| Sohada cho'kkan | 8,9 t (23 %) |
| Sohadan tashqariga olib ketilgan | 28,9 t (76 %) |
| 32 soatlik o'rtacha PM10, maksimum | 116 µg/m³ |
| O'rtacha PM10 > 75 µg/m³ hududi | 0,39 km², manbadan 0,4 km gacha |
| Soatlik PM10 > 75 µg/m³ hududi | 0,78 km², manbadan 0,6 km gacha |
| Soatlik PM10 > 25 µg/m³ hududi | 4,9 km², manbadan 2,5 km gacha |
| Cho'kma qalinligi, maksimum | 2,3 µm |
| Cho'kma > 0,1 µm hududi | 12,6 km², manbadan 4,7 km gacha |
| Buxoro stansiyasi nuqtasida o'rtacha PM10 | 2 µg/m³ |

![](/mnt/user-data/outputs/rasm_4_22_qurilish_tarqalish.png){width=16cm}

**4.22-rasm.** Qurilish maydonidan changning tarqalishi (markaziy holat): a — 32 soatlik o'rtacha PM10; b — soatlik maksimum PM10; c — cho'kma qalinligi. Izoliniyalar raqamlari — mos birliklarda.

Chang shlyuzi shamol yo'nalishi bo'yicha maydondan janubga cho'ziladi. Maydonning o'zi hissasi bilan o'rtacha PM10 konsentratsiyasi O'zgidromet ekologik byulletenida keltirilgan o'rtacha sutkalik ruxsat etilgan maksimal konsentratsiyadan (75 µg/m³) faqat maydon atrofidagi 0,4 km lik zonada oshadi; soatlik cho'qqilarda bu zona 0,6 km gacha kengayadi. 25 µg/m³ dan yuqori soatlik qo'shimcha ifloslanish 2,5 km gacha kuzatiladi. Ko'tarilgan changning to'rtdan uch qismi 20 km li sohadan tashqariga olib ketiladi, ya'ni maydon nafaqat mahalliy, balki shahar miqyosidagi fon ifloslanishga ham hissa qo'shadi.

Muhim natija — Buxoro monitoring stansiyasi maydonga yaqin bo'lsa-da (1 km), 29-apreldagi shimoli-sharqiy shamolda u maydonning shamol yuqori tomonida qolgan va maydon hissasi u yerda atigi 2 µg/m³ ni tashkil etgan. Demak stansiya o'lchovlari shamol yo'nalishiga qarab mahalliy manbalarning ta'sirini sezilarli darajada qayd etishi ham, qayd etmasligi ham mumkin. Bu shahar sharoitida monitoring tarmog'ini loyihalashda va o'lchovlarni talqin qilishda hisobga olinishi kerak.

## Amaliy xulosalar

Hisoblash tajribasi natijalari quyidagi amaliy tavsiyalarga asos bo'ladi.

Qurilish maydonlarida sirtni namlash chang bostirishning samarali usuli hisoblanadi: ko'rilgan bo'ron sharoitida u emissiyani to'liq bartaraf etadi. Tadbir birinchi navbatda kuchli shamol bashorat qilingan kunlarda qo'llanilishi kerak; DustFlow ERA5 yoki meteorologik bashorat ma'lumotlari bilan shunday kunlarni oldindan aniqlash imkonini beradi.

Qurilish maydoni atrofida me'yor buziladigan zona bo'ron sharoitida 0,4–0,6 km ni tashkil etadi va shamol yo'nalishi bo'ylab cho'ziladi. Turar-joy va ijtimoiy obyektlarga nisbatan qurilish maydonlarini joylashtirishda va vaqtinchalik himoya choralarini rejalashtirishda bu masofani hisobga olish tavsiya etiladi.

Changlanish xavfini ishonchli baholash uchun maydon tuprog'ining mexanik tarkibini aniqlash zarur: gil ulushining noaniqligi emissiya bahosida ikki tartibgacha farq beradi.

Shunday qilib, DustFlow majmuasi mintaqaviy hisoblashlar bilan bir qatorda lokal manbalarni ham haqiqiy meteorologik sharoitda baholash imkonini beradi. Buxoro shahridagi qurilish maydoni misolida emissiyaning tuproq tarkibi va sirt holatiga bog'liqligi, chang bostirish tadbirining samaradorligi hamda sanitariya me'yorlari buziladigan zona miqdoriy baholandi. Noaniq parametrlar yashirilmay, ularning oralig'i bo'yicha hisoblash natijalari keltirildi, bu esa xulosalarning qaysi qismi ishonchli va qaysi qismi qo'shimcha o'lchovlarni talab qilishini aniq ko'rsatadi.
