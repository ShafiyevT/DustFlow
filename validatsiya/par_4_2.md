# § 4.2. Dasturiy majmuaning arxitekturasi va kirish ma'lumotlarini tayyorlash

Oldingi paragrafda zarrachalarning harakat tezliklarini hisoblovchi
dasturiy vosita bayon etilgan edi. Ushbu paragrafda ikkinchi va uchinchi
boblarda ishlab chiqilgan barcha matematik modellar va sonli
algoritmlarni birlashtiruvchi dasturiy majmua --- DustFlow keltiriladi.
Majmuaning vazifasi chang zarrachalarining atmosferadagi
konsentratsiyasini real hudud uchun hisoblash, ya'ni xalqaro ma'lumotlar
bazalaridan geofazoviy ma'lumotlarni yuklab olishdan tortib natijalarni
saqlash, kuzatuvlar bilan solishtirish va karta ustida
vizuallashtirishgacha bo'lgan butun jarayonni qamrab olishdir.
Paragrafda keltirilgan barcha hisoblash natijalari haqiqiy kirish
ma'lumotlari --- 2025-yil 28--29-aprel chang bo'roni uchun ERA5-Land
reanalizi va global tuproq hamda yer qoplami ma'lumotlari --- asosida
olingan.

## Majmuaga qo'yiladigan talablar

Majmuani loyihalashda quyidagi talablar asos qilib olindi.

Birinchidan, hisoblash yadrosi foydalanuvchi interfeysidan mustaqil
bo'lishi kerak. Bu matematik modelning biror qismi o'zgartirilganda
faqat tegishli modulni qayta yozish imkonini beradi va har bir modulni
alohida sinovdan o'tkazishga yo'l ochadi.

Ikkinchidan, majmua haqiqiy geofazoviy ma'lumotlar bilan ishlashi shart.
Meteorologik maydonlar, relyef, yer qoplami va tuproq xaritalari xalqaro
ma'lumotlar bazalarida turli formatlarda va turli fazoviy aniqlikda
saqlanadi; ularni qo'lda tayyorlash amaliy foydalanishni imkonsiz
qiladi.

Uchinchidan, meteorologik majburlash vaqt bo'yicha o'zgaruvchan bo'lishi
kerak. Chang bo'roni bir necha soat davomida rivojlanadi, uning davomida
shamol tezligi va yo'nalishi sezilarli o'zgaradi; bitta vaqt momentidagi
meteorologik holat bilan butun hodisani ifodalash yetarli emas.

To'rtinchidan, hisoblash natijalari saqlanishi va kuzatuv ma'lumotlari
bilan solishtirilishi kerak. Buning uchun ma'lumotlar bazasi va
statistik baholash vositalari zarur.

Beshinchidan, natijalar geoaxborot tizimlarida ishlatilishi mumkin
bo'lgan formatlarda eksport qilinishi va karta ustida ko'rsatilishi
kerak.

## Majmuaning qatlamli arxitekturasi

Sanab o'tilgan talablarni qondirish uchun majmua besh qatlamli
arxitektura asosida qurildi. Har bir qatlam faqat o'zidan pastdagi
qatlamga murojaat qiladi, teskari bog'lanish yo'q. Bunday tashkil etish
modullar orasidagi bog'liqlikni kamaytiradi va ularni mustaqil
rivojlantirish imkonini beradi. Majmuaning tuzilishi 4.7-rasmda
keltirilgan.

![](media/rId21.png){width="5.833333333333333in"
height="4.013001968503937in"}

**4.7-rasm.** DustFlow majmuasining qatlamli arxitekturasi.

**Birinchi, foydalanuvchi qatlami** uch xil ishlash usulini qamrab
oladi. `dustflow.gui` moduli interaktiv grafik interfeysni ta'minlaydi.
`dustflow.cli` moduli buyruqlar qatori orqali ishlashni va ommaviy
hisoblashlarni ta'minlaydi. `dustflow.config` moduli hisoblash
stsenariysini JSON faylida saqlash va qayta yuklash imkonini beradi, bu
esa natijalarning takrorlanuvchanligini kafolatlaydi.

**Ikkinchi, boshqaruv qatlami** hisoblash jarayonini tashkil etadi.
`dustflow.model` moduli fraksiyalar va makroqadamlar sikllarini
boshqaradi hamda meteorologik majburlashni hisoblash davomida yangilash
imkonini beradi. `dustflow.balance` moduli har bir qadamda massa
balansini, jumladan yon chegaralar orqali sof oqimni nazorat qiladi.
`dustflow.validatsiya` moduli hisoblash natijalarini kuzatuvlar bilan
solishtiruvchi statistik mezonlarni amalga oshiradi (§ 4.3).

**Uchinchi, hisoblash qatlami** matematik yadroni tashkil etadi.
`dustflow.solver` moduli uchinchi bobda qurilgan sxemani amalga
oshiradi, `dustflow.emission` ikkinchi bobdagi emissiya sxemasini,
`dustflow.velocity` esa § 4.1 dagi DustVel yadrosiga asoslangan
tezliklar maydonini hisoblaydi.

**To'rtinchi, ma'lumot tuzilmalari qatlami** hisoblashda ishlatiladigan
barcha kattaliklarni saqlaydi va ular ustida amallar bajaradi. Asosiy
tuzilmalar 4.2-jadvalda keltirilgan.

**4.2-jadval.** Majmuaning asosiy ma'lumot tuzilmalari

  ------------------------------------------------------------------------------------------------------
  Tuzilma              Modul             Tarkibi                                Asosiy usullari
  -------------------- ----------------- -------------------------------------- ------------------------
  `Tor`                `grid`            $L_{x},L_{y},H_{z},N,M,L,\eta,H_{e}$   `balandlik()`,
                                                                                `yacheyka_hajmi()`,
                                                                                `metrik()`

  `KirishMaydonlari`   `data`            $U_{10}$, yo'nalish, $w$, $m_{cl}$,    `tekshir()`
                                         $\lambda$, $z_{0}$, $A_{ef}$, $\eta$   

  `Model`              `model`           $C$, $F$, $U$, $V$, $W$, $K$, $v_{t}$, `qadam()`,
                                         $\beta_{i}$, cho'kindi                 `ishga_tushir()`,
                                                                                `majburlash_yangila()`

  `Balans`             `balance`         $Q_{em}$, $Q_{cho}$, $Q_{chiq}$,       `massa()`,
                                         $Q_{yut}$                              `nomuvofiqlik()`

  `Stsenariy`          `config`          barcha hisoblash parametrlari          `saqla()`, `yukla()`,
                                                                                `kalit()`
  ------------------------------------------------------------------------------------------------------

`Tor` tuzilmasi relyefga moslashgan koordinatalar bilan bog'liq barcha
hisoblashlarni o'z ichiga oladi: (3.57) bo'yicha $H_{e}$ kattaligini,
(3.61) bo'yicha metrik ko'paytuvchilarni va yacheyka hajmlarini. Bu
hisoblash moduli geometriyaning tafsilotlariga bog'liq bo'lmasligini
ta'minlaydi.

**Beshinchi, saqlash va kirish-chiqish qatlami** geofazoviy
ma'lumotlarni yuklab olish va o'qish, natijalarni saqlash, eksport
qilish va vizuallashtirishni qamrab oladi. U quyida batafsil bayon
etiladi.

## Geofazoviy ma'lumotlarni yuklab olish va hisoblash to'riga keltirish

Model uchun zarur maydonlar besh xil xalqaro manbadan olinadi
(4.10-jadval, § 4.3): shamol, harorat va tuproq namligi --- ERA5-Land
reanalizidan, gil ulushi va tuproq zichligi --- SoilGrids 2.0 dan,
relyef --- Copernicus DEM dan, yer qoplami --- ESA WorldCover 2021 dan.
Ularning formatlari va aniqligi keng oraliqda o'zgaradi: ERA5-Land
NetCDF formatida $0,1^{\circ}$ aniqlikda, yer qoplami GeoTIFF formatida
10 m aniqlikda beriladi. Ma'lumotlarni tayyorlash ikki bosqichda
bajariladi.

**Birinchi bosqich --- yuklab olish** (`malumot_yuklash` moduli). Modul
har bir manbaga uning dasturiy interfeysi orqali murojaat qiladi va
faqat hisoblash hududiga (61,5--66,0° E, 38,5--42,0° N) tegishli qismni
oladi. ERA5-Land ma'lumotlari Copernicus Climate Data Store dan soatlik
qatorlar ko'rinishida yuklanadi. Statik maydonlar $0,01^{\circ}$
($\approx 1$ km) li oraliq to'rga keltiriladi. Katta hajmli manbalar
uchun (masalan, 10 m li yer qoplami) fayl ichidagi tayyor
kichraytirilgan qatlamlardan foydalaniladi, bu yuklanadigan ma'lumot
hajmini ming barobardan ko'proq kamaytiradi. Yer qoplami sinflari jadval
bo'yicha g'adir-budurlik uzunligi $z_{0}$, o'simlik qoplami indeksi
$\lambda$ va eroziyaga beriluvchan yuza ulushi $A_{ef}$ ga
aylantiriladi. Modul tanlangan soat uchun hisoblash stsenariysi
katalogini ham yig'adi: kerakli soatni barcha yuklangan ERA5 fayllari
ichidan topadi, hajmiy tuproq namligini og'irlik namligiga o'tkazadi va
barcha maydonlarni tavsif fayli bilan bitta katalogga joylaydi.

Ma'lumotlarni tayyorlash jarayonida aniqlangan sifat muammolari ---
SoilGrids ning cho'l hududlaridagi ishonchsizligi va ERA5-Land da
sug'orishning hisobga olinmasligi --- hamda ularni hal qilish usullari §
4.3 da batafsil keltirilgan.

**Ikkinchi bosqich --- hisoblash to'riga keltirish** (`io_geo` moduli).
Geografik koordinatalar ekvivalent proyeksiya yordamida metrik
koordinatalarga o'tkaziladi:

$$x = \left( \text{lon} - \text{lon}_{0} \right) \cdot 111320\cos\varphi_{ref},\quad\quad y = \left( \text{lat} - \text{lat}_{0} \right) \cdot 110574,\quad\quad(4.4)$$

bu yerda $\varphi_{ref}$ --- sohaning o'rtacha kengligi. Buxoro viloyati
kabi $4^{\circ}$ dan kichik hududlar uchun bunday soddalashtirish
keltirib chiqaradigan xatolik $0,1$ % dan oshmaydi.

Maydonlar hisoblash to'riga ikki usulda keltiriladi, usul manba
to'rining qadamini hisoblash to'rining qadami bilan solishtirish orqali
avtomatik tanlanadi. Manba aniqroq bo'lsa, **yacheyka bo'yicha
o'rtalash** qo'llaniladi; aks holda --- **ikki chiziqli
interpolyatsiya**. Aniqroq maydonni interpolyatsiya qilish axborotning
yo'qolishiga olib keladi: tugun nuqtalaridagi tasodifiy qiymatlar
yacheykaning o'rtacha tavsifini aks ettirmaydi. Qo'polroq maydonni
o'rtalash esa ma'nosiz, chunki ko'p yacheykalarga umuman manba nuqtasi
tushmaydi. Buxoro viloyati uchun 60 × 60 li hisoblash to'riga keltirish
natijalari 4.3-jadvalda keltirilgan.

**4.3-jadval.** Kirish maydonlarini hisoblash to'riga keltirish

  -----------------------------------------------------------------------------
  Maydon         Asl manba      Oraliq to'r    Usul              Hisoblash
                                                                 to'ri
  -------------- -------------- -------------- ----------------- --------------
  $U_{10}$,      ERA5-Land,     46 × 36        interpolyatsiya   61 × 61
  $V_{10}$,      0,1°                                            
  harorat                                                        

  Tuproq namligi ERA5-Land,     46 × 36        interpolyatsiya   61 × 61
                 0,1°                                            

  Relyef $\eta$  Copernicus     450 × 350      o'rtalash         61 × 61
                 DEM, 90 m                                       

  Gil ulushi,    SoilGrids 2.0, 450 × 350      o'rtalash         61 × 61
  tuproq         250 m                                           
  zichligi                                                       

  $z_{0}$,       ESA            450 × 350      o'rtalash         61 × 61
  $\lambda$,     WorldCover, 10                                  
  $A_{ef}$       m                                               
  -----------------------------------------------------------------------------

Maydonlar o'qilgandan keyin `tekshir()` usuli yordamida ularning fizik
chegaralari nazorat qilinadi: shamol tezligi va namlik manfiy emasligi,
gil ulushi hamda eroziyaga beriluvchan yuza ulushi $\lbrack 0,1\rbrack$
oralig'ida yotishi, g'adir-budurlik uzunligi qat'iy musbat ekanligi
tekshiriladi. Chegaradan chiqqan qiymat aniqlangan holda hisoblash
boshlanmaydi.

## Haqiqiy ma'lumotlar asosidagi stsenariylar

Majmua bilan ishlashni soddalashtirish uchun haqiqiy ma'lumotlar asosida
beshta hisoblash stsenariysi tayyorlandi. Ular kuzatuvlar bilan
tasdiqlangan ikki chang hodisasini va ularga yaqin sokin holatni qamrab
oladi. Stsenariylarning tavsifi va emissiya sxemasi bo'yicha asosiy
ko'rsatkichlari 4.4-jadvalda keltirilgan.

**4.4-jadval.** Haqiqiy ma'lumotlar asosidagi stsenariylar

  ----------------------------------------------------------------------------------
  №          Holat         Vaqt, UTC    $U_{10}$   Cho'l      Eroziya    Emissiya,
                                        maks., m/s tuprog'i   maydoni, % t/soat
                                                   namligi, %            
  ---------- ------------- ------------ ---------- ---------- ---------- -----------
  1          Sokin kun     23.04.2025   5,8        2,4        0          0
                           09:00                                         

  2          Bo'ron        28.04.2025   12,3       2,2        46,5       27 800
             boshlanishi   21:00                                         

  3          Bo'ron        29.04.2025   12,2       2,2        73,6       42 900
                           09:00                                         

  4          Bo'ron        29.04.2025   12,7       2,2        43,5       34 700
             cho'qqisi     15:00                                         

  5          Qishki hodisa 15.02.2026   11,3       22,5       0          0
                           09:00                                         
  ----------------------------------------------------------------------------------

Jadvaldan uchta xulosa kelib chiqadi. Birinchidan, sokin kunda hududning
hech bir nuqtasida eroziya sharti bajarilmaydi --- emissiya sxemasidagi
chegaraviy shart haqiqiy ma'lumotlarda ham to'g'ri ishlaydi.
Ikkinchidan, bo'ron davomida eroziya maydoni soatlar bo'yicha keskin
o'zgaradi (44--74 %), bu vaqt bo'yicha o'zgaruvchan majburlashning
zarurligini asoslaydi. Uchinchidan, 5-stsenariyda shamol bo'ron holatiga
yaqin bo'lsa-da (11,3 m/s), ERA5-Land bo'yicha qishki tuproq namligi o'n
barobar yuqori bo'lgani sababli emissiya umuman yo'q. Bu natija § 4.3 da
kuzatuvlar bilan solishtiriladi.

Majmua tarkibida, bundan tashqari, sintetik sinov ma'lumotlari
generatori ham mavjud. U faqat dasturiy ta'minotni sinash uchun
mo'ljallangan va dissertatsiyada keltirilgan natijalarni olishda
foydalanilmagan.

Stsenariyni tanlash uchta usulda amalga oshiriladi: buyruqlar qatorida
raqami yoki nomi bo'yicha, grafik interfeysda surgich orqali, hamda
dasturda `stsenariylar_royxati()` va `stsenariy_yukla()` funksiyalari
yordamida.

## Ma'lumotlar bazasi

Majmuada SQLite bazasidan foydalaniladi. Uning tanlanishi ikki sabab
bilan izohlanadi: baza alohida server talab qilmaydi va butun ma'lumot
bitta faylda saqlanadi, bu esa natijalarni boshqa tadqiqotchiga
uzatishni osonlashtiradi. Bazaning sxemasi 4.8-rasmda keltirilgan.

![](media/rId27.png){width="5.833333333333333in"
height="3.3396937882764655in"}

**4.8-rasm.** Ma'lumotlar bazasining sxemasi.

Baza beshta jadvaldan iborat, ularning vazifalari 4.5-jadvalda
keltirilgan.

**4.5-jadval.** Ma'lumotlar bazasining jadvallari

  -----------------------------------------------------------------------
  Jadval                  Vazifasi                Asosiy maydonlari
  ----------------------- ----------------------- -----------------------
  `seanslar`              har bir hisoblash       `barmoq_izi`,
                          seansi va uning         `parametrlar`, `holat`,
                          parametrlari            `hisob_vaqti`

  `maydonlar`             kirish maydonlarining   `nom`, `manba`,
                          jamlanma tavsifi        `eng_kam`, `eng_kop`,
                                                  `ortacha`

  `qatorlar`              vaqt qatorlari: massa   `t`, $Q$, $Q_{em}$,
                          balansi, konsentratsiya $Q_{cho}$, $Q_{chiq}$,
                                                  $Q_{yut}$

  `suratlar`              konsentratsiya          `t`, `shakl`, `malumot`
                          maydonlarining siqilgan 
                          suratlari               

  `kuzatuvlar`            monitoring              `stansiya`, `sana`,
                          stansiyalarining        `C_pm10`, `C_pm25`
                          o'lchovlari             
  -----------------------------------------------------------------------

Har bir seans uchun parametrlar to'plamidan SHA-256 algoritmi yordamida
noyob identifikator --- barmoq izi hisoblanadi:

$$\text{barmoq izi} = SHA256\left( \text{parametrlar} \right)_{1\ldots 16}.\quad\quad(4.5)$$

Yangi hisoblash boshlanishidan oldin majmua bazada shu barmoq iziga ega
yakunlangan seans mavjudligini tekshiradi; u topilsa, natijalar bazadan
olinadi va takroriy hisoblash bajarilmaydi. `suratlar` jadvalida
konsentratsiya maydonlari siqilgan ko'rinishda saqlanadi va uzilgan
hisoblash oxirgi suratdan davom ettiriladi.

`kuzatuvlar` jadvaliga O'zgidromet avtomatik monitoring stansiyalarining
soatlik PM10 va PM2.5 qiymatlari yoziladi. Buning uchun majmua tarkibida
ikkita yordamchi modul yaratildi: biri O'zgidromet «DigitalMeteo»
portalining arxividan istalgan davr uchun soatlik ma'lumotlarni yuklab
oladi, ikkinchisi monitoring platformasidan joriy qiymatlarni har soatda
yig'ib boradi. Bu ma'lumotlar § 4.3 dagi validatsiyada ishlatiladi.

## Buxoro viloyati uchun kirish maydonlari

Yuqorida bayon etilgan modullar yordamida tayyorlangan statik kirish
maydonlari 4.9-rasmda keltirilgan.

![](media/rId31.png){width="5.833333333333333in"
height="3.786081583552056in"}

**4.9-rasm.** Buxoro viloyati uchun haqiqiy kirish maydonlari: a ---
relyef; b --- yer qoplami; c --- gil ulushi; d --- tuproq zichligi; e
--- eroziyaga beriluvchan yuza ulushi; f --- g'adir-budurlik uzunligi.

Maydonlar hududning haqiqiy geografiyasini aniq aks ettiradi. Hududning
72 % ini yalang'och va siyrak o'simlikli yuzalar --- asosan Qizilqum
cho'li --- egallaydi, 15 % i siyrak dasht o'tloqlari, 9 % i Zarafshon
vohasi va Amudaryo vodiysidagi sug'oriladigan ekinzorlar. Relyef 21 m
dan 1802 m gacha o'zgaradi: hududning katta qismi 200--400 m
balandlikdagi tekislik, shimoli-sharqda Nurota tog'lari joylashgan. Gil
ulushi vohada 0,29 atrofida, cho'lda 0,05; eroziyaga beriluvchan yuza
ulushi yalang'och yuzalarda 0,25, o'tloqlarda 0,10, ekinzorlar va shahar
hududlarida nolga teng. Tuproq zichligining medianasi 1,43 g/sm³.

## Hisoblash yadrosining unumdorligi

Uchinchi bobning oxirida ta'kidlanganidek, verifikatsiya uchun
ishlatilgan dastlabki dasturiy amalga oshirishning unumdorligi yetarli
emas edi, chunki progonka usulining ichki sikli interpretatsiyalanuvchi
tilda bajarilgan. Mazkur majmuada bu masala vektorlashtirish orqali hal
qilingan.

Dekompozitsiyaning har bir bosqichida ko'p sonli bir o'lchovli masalalar
yechiladi: masalan, $Ox$ bosqichida $M \cdot L$ ta mustaqil uch
diagonalli sistema hosil bo'ladi. Vektorlashtirilgan amalga oshirishda
barcha sistemalar bir vaqtda qaraladi: progonka koeffitsiyentlari
(3.83)--(3.84) massiv amallari ko'rinishida hisoblanadi va sikl faqat
yugurish yo'nalishi bo'yicha, ya'ni $N$ marta bajariladi. Natijada
interpretatsiyalanuvchi tildagi sikllar soni

$$M \cdot L \cdot N\mspace{6mu} \rightarrow \mspace{6mu} N\quad\quad(4.6)$$

ga qisqaradi, asosiy hisoblashlar esa kompilyatsiyalangan kutubxona
darajasida bajariladi.

## Vaqt bo'yicha o'zgaruvchan meteorologik majburlash

Haqiqiy chang bo'ronini modellashtirish uchun `Model` tuzilmasiga
`majburlash_yangila()` usuli qo'shildi. U meteorologik majburlashga
bog'liq barcha maydonlarni --- shamol va zarrachalar tezliklarini,
turbulent diffuziya koeffitsiyentlarini, emissiya oqimini, quruq
cho'kish tezligini va yon chegaralardagi almashinuv koeffitsiyentini ---
yangi kirish maydonlari bo'yicha qayta hisoblaydi. Konsentratsiya,
cho'kindi, massa balansi va vaqt esa saqlanadi, ya'ni hisoblash uzluksiz
davom etadi. Hisoblash soatlik bo'laklar ketma-ketligi sifatida tashkil
etiladi: har bir soat boshida ERA5-Land ning shu soatdagi maydonlari
yuklanadi va keyingi bir soat davomida integrallash bajariladi.

Amalga oshirishning to'g'riligi quyidagi test bilan tekshirildi:
o'zgarmas majburlash bilan bir soatlik bo'laklardan iborat hisoblash
uzluksiz hisoblashni bit darajasida takrorladi (maksimal nisbiy farq 0),
massa balansi 0,0044 % aniqlikda bajarildi.

## Hisoblash to'ri va fraksiyalar

Hisoblash quyidagi parametrlarda o'tkazildi. Soha $380 \times 390$ km
maydonni egallaydi va $60 \times 60$ gorizontal tugun bilan qoplanadi
($\Delta x = 6,3$ km, $\Delta y = 6,5$ km). Vertikal bo'yicha
$H_{z} = 5$ km balandlik 20 ta qatlamga bo'linadi. Vaqt qadami
$\Delta t = 120$ s. Hisoblash davri 2025-yil 28-aprel 00:00 dan 29-aprel
24:00 UTC gacha, 48 soat; meteorologik majburlash har soatda
yangilanadi, yon chegaralarda fon konsentratsiyasi nolga teng (faqat
mahalliy emissiya).

Chang zarrachalari beshta fraksiyaga ajratildi, ularning parametrlari
4.6-jadvalda keltirilgan.

**4.6-jadval.** Hisoblashda qaralgan fraksiyalar va ularning
parametrlari

  ----------------------------------------------------------------------------------------
  Fraksiya     Chegaralar,   $\rho_{p}$,   Massa       $\tau$, ms  $v_{t}$, m/s
               µm            kg/m³         ulushi                  
  ------------ ------------- ------------- ----------- ----------- -----------------------
  PM2.5        0,2--2,5      1500          0,049       0,0023      $2,26 \cdot 10^{- 5}$

  PM10         2,5--10       2000          0,327       0,153       $1,51 \cdot 10^{- 3}$

  Yirik        10--20        2200          0,088       1,351       $1,32 \cdot 10^{- 2}$
  dispers                                                          

  Juda yirik   20--50        2400          0,327       7,366       $7,23 \cdot 10^{- 2}$

  Saltatsion   50--100       2600          0,208       39,902      $3,91 \cdot 10^{- 1}$
  ----------------------------------------------------------------------------------------

Massa ulushlari (2.15)--(2.17) uch modali lognormal taqsimot bo'yicha
hisoblangan. Jadvaldagi $\tau$ va $v_{t}$ qiymatlari har bir fraksiya
chegaralarining geometrik o'rtachasi $\bar{d} = \sqrt{d_{i - 1}d_{i}}$
uchun berilgan; shu sababli ular § 4.1 dagi 4.1-jadvaldan farq qiladi, u
yerda fraksiyaning yuqori chegarasiga teng diametrlar (2,5; 10 va 50 µm)
qaralgan. Masalan, PM10 fraksiyasi uchun $\bar{d} = 5$ µm da
$\tau = 0,153$ ms, $d = 10$ µm da esa $\tau = 0,613$ ms. Relaksatsiya
vaqti fraksiyalar bo'yicha to'rt tartibdan ko'proq farqlanadi, bu esa
uchinchi bobda ko'rsatilgan qattiqlik muammosining amaliy tasdig'idir.

## Emissiya sxemasining ishlashi

Bo'ronning eng faol soatlaridan biri --- 29-aprel 12:00 UTC uchun
emissiya sxemasining natijalari 4.10-rasmda keltirilgan.

![](media/rId38.png){width="5.833333333333333in"
height="2.0169313210848645in"}

**4.10-rasm.** Emissiya sxemasining natijalari, 29.04.2025 12:00 UTC: a
--- dinamik tezlik; b --- samarali chegaraviy tezlik; c --- emissiya
oqimi.

Dinamik tezlik $u_{*}$ hudud bo'ylab 0,26 dan 1,58 m/s gacha o'zgaradi.
Uning taqsimoti shamol tezligi va g'adir-budurlik uzunligi bilan
belgilanadi: voha va shahar hududlarida $z_{0}$ katta bo'lgani uchun
$u_{*}$ ham yuqori. Samarali chegaraviy tezlik $u_{*t}^{ef}$ esa ancha
kengroq oraliqda --- 0,24 dan 2,4 m/s gacha o'zgaradi: cho'lda namlik va
o'simlik qoplami tuzatmalari birga yaqin, vohada va tog'larda ular
chegaraviy tezlikni bir necha barobar oshiradi. Natijada eroziya
hududning 70 % ida sodir bo'ladi, emissiya oqimining maksimumi
$9,7 \cdot 10^{- 6}$ kg/(m²·s).

Emissiya fazoviy jihatdan juda notekis: eng faol manbalar alohida
uchastkalarda, xususan Buxoro vohasining shimoliy chekkasida --- cho'l
va voha chegarasida joylashgan. Bu yerda shamol tezligi yuqori, yuza esa
yalang'och. Emissiyaning hududning tabiiy sharoitiga qarab o'z-o'zidan
tanlab sodir bo'lishi modelning muhim xususiyati: manbalarni qo'lda
belgilash talab qilinmaydi, sug'orish va o'simlik qoplamini tiklash kabi
tadbirlar esa modelda bevosita aks etadi.

## Hisoblash natijalari

Yer sirtiga yaqin qatlamdagi chang konsentratsiyasi 4.11-rasmda
keltirilgan.

![](media/rId42.png){width="5.1181091426071745in"
height="4.6895395888013995in"}

**4.11-rasm.** Yer sirtiga yaqin qatlamdagi chang konsentratsiyasi,
29.04.2025 12:00 UTC.

Rasmdan chang shlyuzlarining shakllanishi yaqqol ko'rinadi.
Shimoli-sharqdan esayotgan shamol har bir faol manbadan changni
janubi-g'arbga cho'zilgan tor shlyuz ko'rinishida olib ketadi. Eng
yuqori konsentratsiyalar Buxoro vohasining shimoliy chekkasidagi
manbalardan janubda --- Buxoro shahri va undan janubdagi hududlarda ---
kuzatiladi. Yer sirtidagi konsentratsiyaning (barcha fraksiyalar) hudud
bo'yicha o'rtacha qiymati 513 µg/m³, medianasi 221 µg/m³, 99-protsentili
3756 µg/m³; PM10 ning o'rtacha qiymati 235 µg/m³.

Vertikal profillar va fraksiyalar bo'yicha taqsimot 4.12-rasmda
keltirilgan.

![](media/rId45.png){width="5.833333333333333in"
height="2.373477690288714in"}

**4.12-rasm.** Vertikal profillar va fraksiyalar bo'yicha taqsimot,
29.04.2025 12:00 UTC.

Buxoro stansiyasi joylashgan yacheykada konsentratsiya yer sirtida
maksimal bo'lib, balandlik bo'yicha kamayadi va 2 km atrofida fon
qiymatiga yetadi --- chang faol turbulent aralashish qatlamida
to'plangan. Faol manbalardan tashqaridagi cho'l nuqtasida esa
konsentratsiya past, bu emissiyaning fazoviy notekisligini tasdiqlaydi.

Sohadagi massaning asosiy qismi PM10 (34,3 ming tonna) va 20--50 µm
(25,7 ming tonna) fraksiyalariga to'g'ri keladi. 50--100 µm li fraksiya
emissiyada 20,8 % ulushga ega bo'lsa-da, sohada atigi 4,6 ming tonna
qolgan --- cho'kish tezligi 0,39 m/s bo'lgani uchun u tez orada yerga
qaytadi.

## Massa balansi

Massa balansi har bir vaqt qadamida nazorat qilinadi, uning o'zgarishi
4.13-rasmda, 48 soatlik yakuniy qiymatlari 4.7-jadvalda keltirilgan.

![](media/rId49.png){width="5.833333333333333in"
height="2.1926706036745407in"}

**4.13-rasm.** Massa balansining tashkil etuvchilari va bajarilish
aniqligi, 28--29.04.2025.

**4.7-jadval.** Massa balansining tashkil etuvchilari (48 soat)

  -----------------------------------------------------------------------
  Tashkil etuvchi         Massa, ming tonna       Ulush, %
  ----------------------- ----------------------- -----------------------
  Yer sirtidan chiqqan    1000,8                  100,0

  Yer sirtiga cho'kkan    372,6                   37,2

  Soha chegaralaridan     621,2                   62,1
  chiqib ketgan                                   

  Atmosferada yutilgan    5,9                     0,6

  Manfiy qiymatlarni      +20,7                   2,1
  kesish tuzatmasi                                

  Sohada muallaq qolgan   21,8                    2,2

  **Balansning                                    **0,0029**
  nomuvofiqligi**                                 
  -----------------------------------------------------------------------

Massa balansi 0,0029 % aniqlikda bajariladi, bu § 3.2 da qurilgan
sxemaning konservativligini haqiqiy ma'lumotlar bilan o'tkazilgan
hisoblashda tasdiqlaydi. Vaqt bo'yicha o'zgaruvchan majburlash tufayli
jarayon barqaror holatga chiqmaydi: sohadagi massa bo'ron rivojlanishi
bilan o'sib, 29-aprel 13:00 UTC da 78,7 ming tonnaga yetadi, keyin
shamol susayishi bilan kamayadi. Chiqqan changning qariyb uchdan ikki
qismi hisoblash sohasi chegaralaridan tashqariga olib ketilgan --- bu
kuchli shamolda chang ko'chishining mintaqaviy miqyosini ko'rsatadi.
Hisoblash sohasi Buxoro viloyati bilan birga unga tutash hududlarni ham
qamraydi (taxminan 153 ming km², viloyat --- 40 ming km²); viloyat
chegarasi ichidan ko'tarilgan chang 537,6 ming tonnani, ya'ni umumiy
emissiyaning 54 % ini tashkil etadi.

Jadvalda alohida qayd etilgan kesish tuzatmasi sonli sxemaning
xususiyatidir: keskin gradientlarda sxema kichik manfiy tebranishlar
beradi, ularni nolga tenglashtirish sohaga chiqqan massaning taxminan 2
% ini sun'iy qo'shadi. Balans bu hadni aniq hisobga oladi, biroq uni
kamaytirish sxemani rivojlantirishning bir yo'nalishi hisoblanadi.

## Grafik foydalanuvchi interfeysi

Majmua bilan interaktiv ishlash uchun grafik interfeys yaratilgan
(4.14-rasm).

![](media/rId53.png){width="5.833333333333333in"
height="3.3561636045494314in"}

**4.14-rasm.** DustFlow majmuasining asosiy oynasi (3-stsenariy:
29.04.2025 09:00 UTC).

Boshqaruv panelining yuqori qismida stsenariy tanlash bo'limi
joylashgan. Surgich stsenariylar katalogidagi barcha stsenariylarni
ko'rsatadi; tanlangan stsenariyning nomi, ma'lumot manbalari va sanasi
darhol chiqariladi. «Stsenariy ma'lumotlari» katagi belgilanganda
hisoblash haqiqiy NetCDF va GeoTIFF fayllaridan o'qilgan maydonlar
asosida bajariladi, belgi olib tashlansa --- qo'lda berilgan parametrlar
ishlatiladi. Undan pastda hisoblash parametrlari va sozlamalar
joylashgan.

Oynaning o'ng qismida to'rtta grafik maydoni joylashgan: asosiy maydonda
tanlangan rejimga qarab konsentratsiya, emissiya oqimi yoki kirish
maydonlari; yuqori o'ng burchakda Qizilqum va Buxoro nuqtalari uchun
vertikal profillar; undan pastda fraksiyalar bo'yicha taqsimot; pastki
qismda massa balansining vaqt bo'yicha o'zgarishi. Boshqaruv panelining
quyi qismida massa balansi, konsentratsiya statistikasi va hisoblash
vaqti raqamli ko'rinishda chiqariladi.

Emissiya ko'rinish rejimi 4.15-rasmda keltirilgan. U eroziya sodir
bo'ladigan hududlarni aniqlash va tabiatni muhofaza qilish tadbirlarini
rejalashtirish uchun ishlatiladi.

![](media/rId56.png){width="5.833333333333333in"
height="3.3561636045494314in"}

**4.15-rasm.** Emissiya oqimini ko'rsatish rejimi.

## Natijalarni eksport qilish va karta ustida ko'rsatish

`dustflow.eksport` moduli natijalarni to'rtta formatda saqlash imkonini
beradi: CSV --- jadval ko'rinishidagi ma'lumot bilan ishlash uchun, ESRI
ASCII Grid --- geoaxborot tizimlarida (QGIS, ArcGIS) qatlam sifatida
ochish uchun, NumPy arxivi --- keyingi tahlil uchun, matnli hisobot ---
natijalarni qisqacha bayon etish uchun.

`dustflow.karta` moduli natijalarni karta asosida chizadi. Hisoblash
to'rining metrik koordinatalari Web Mercator proyeksiyasiga o'tkaziladi,
karta asosi OpenStreetMap plitkalaridan olinadi. Konsentratsiya maydoni
diskret sinflarga ajratilib, yarim shaffof qatlam sifatida karta ustiga
qo'yiladi, ruxsat etilgan maksimal konsentratsiya darajasi alohida
izoliniya bilan ajratiladi.

## Hisoblash samaradorligi

Majmuaning unumdorligi ikki xil rejimda o'lchandi (4.8-jadval).

**4.8-jadval.** Hisoblash vaqti

  --------------------------------------------------------------------------------------
  Rejim          To'r                       Hisoblash      Vaqt, s        Model soati
                                            davri                         uchun, s
  -------------- -------------------------- -------------- -------------- --------------
  O'zgarmas      $40 \times 40 \times 15$   6 soat         5,8            1,0
  majburlash                                                              
  (GUI)                                                                   

  Soatlik ERA5   $60 \times 60 \times 20$   48 soat        228            4,7
  majburlashi                                                             
  --------------------------------------------------------------------------------------

Asosiy to'rda bir model soati 4,7 soniyada hisoblanadi, jumladan
majburlashni yangilash ham. Sutkalik bashorat uchun taxminan 2 daqiqa
talab qilinadi, bu operativ rejimda ishlash uchun to'liq maqbul.
Taqqoslash uchun, § 3.4 da keltirilgan dastlabki dasturiy amalga
oshirishda 12 soatlik hisoblash uchun 17 soat talab qilinar edi.

## Majmuaning cheklovlari

Majmuaning texnik cheklovlari quyidagilardan iborat. Birinchidan,
geografik koordinatalardan metrik koordinatalarga o'tishda (4.4)
ekvivalent proyeksiya qo'llaniladi; respublika miqyosidagi
hisoblashlarda aniqroq proyeksiyaga o'tish talab qilinadi. Ikkinchidan,
metrik hadlar oshkor aproksimatsiyalangani sababli keskin relyefli
hududlarda vaqt qadamiga cheklov qo'yilishi mumkin. Uchinchidan, manfiy
qiymatlarni kesish sohaga massaning taxminan 2 % ini qo'shadi.
To'rtinchidan, yer qoplami statik va mavsumiy o'zgarishni aks
ettirmaydi. Modelning fizik cheklovlari --- kirish ma'lumotlarining
sifati, emissiyaning fazoviy taqsimoti va hududdan tashqaridan keluvchi
chang bilan bog'liq masalalar --- kuzatuvlar bilan taqqoslash natijalari
asosida § 4.3 da muhokama qilinadi.

Shunday qilib, ushbu paragrafda ikkinchi va uchinchi boblarda ishlab
chiqilgan modellar va algoritmlarni birlashtiruvchi dasturiy majmua
yaratildi. Majmua besh qatlamli arxitektura asosida qurilib, uning har
bir tarkibiy qismi alohida sinovdan o'tkazilishi mumkin. Xalqaro
ma'lumotlar bazalaridan geofazoviy ma'lumotlarni yuklab olish va ularni
yagona hisoblash to'riga keltirish modullari yaratildi; ular manba
aniqligiga qarab o'rtalash yoki interpolyatsiya usulini avtomatik
tanlaydi. Model vaqt bo'yicha o'zgaruvchan meteorologik majburlash bilan
ishlaydigan qilib kengaytirildi va uning to'g'riligi test bilan
tasdiqlandi. Haqiqiy ma'lumotlar asosida beshta stsenariy tayyorlandi.
Ma'lumotlar bazasi, O'zgidromet stansiyalari ma'lumotlarini yuklash
vositalari, grafik interfeys, eksport va karta ustida vizuallashtirish
vositalari yaratildi. 2025-yil 28--29-aprel chang bo'roni uchun
o'tkazilgan hisoblash emissiyaning hududning tabiiy sharoitiga qarab
tanlab sodir bo'lishini, chang shlyuzlarining shamol yo'nalishi bo'ylab
shakllanishini va chiqqan changning uchdan ikki qismi hisoblash
sohasidan tashqariga olib ketilishini ko'rsatdi; viloyat hududidan 48
soatda 537,6 ming tonna chang ko'tarilgan. Massa balansi 0,0029 %
aniqlikda bajarildi. Keyingi paragrafda modelning adekvatligi mustaqil
kuzatuvlar asosida baholanadi.
