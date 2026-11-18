# ════════════════════════════════════════════════════════════════════════
#  "Moliya va intellektual texnologiyalar" jurnali maqolalarini kompyuterga yuklab olish
#  Natija:  <Hujjatlar papkangiz>\Jurnallar\Moliya jurnali\<YYYY-yil N-son>\
#           "NN. Mualliflar - Maqola nomi.pdf"  +  "00. Toʻliq son ....pdf"  +  "Mundarija.csv"
#  Manba: https://tift-fintech.uz (rasmiy fayllar)
#  Qayta ishga tushirilsa, yuklab olingan fayllar o'tkazib yuboriladi.
# ════════════════════════════════════════════════════════════════════════
param([string]$Root = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Jurnallar'))

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'

$Journal = Join-Path $Root 'Moliya jurnali'
New-Item -ItemType Directory -Force -Path $Journal | Out-Null

function Clean-Name([string]$s, [int]$max) {
    $s = ($s -replace '[<>:"/\\|?*\x00-\x1F]', ' ') -replace '\s+', ' '
    $s = $s.Trim(' ', '.')
    if ($s.Length -gt $max) { $s = $s.Substring(0, $max).Trim(' ', '.') + '…' }
    return $s
}

$items = @'
[
{
"f": "2025-yil 1-son",
"n": 1,
"full": false,
"t": "Татқиқотчи ва муштарийлар илмий фаолиятга ривож!",
"a": "Бош муҳаррир, TIFT университети Ректори А. Нодиров",
"c": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%98%D0%B7%D0%BB%D0%B0%D0%BD%D1%83%D0%B2%D1%87%D0%B8_%D0%B2%D0%B0_%D0%BC%D1%83%D1%88%D1%82%D0%B0%D1%80%D0%B8%D0%B8%D0%BB%D0%B0%D1%80_%D0%B8%D0%BB%D0%BC%D0%B8%D0%B8_%D1%84%D0%B0%D0%BE%D0%BB%D0%B8%D1%8F%D1%82%D0%B3%D0%B0_%D1%80%D0%B8%D0%B2%D0%BE%D0%B6.pdf"
},
{
"f": "2025-yil 1-son",
"n": 2,
"full": false,
"t": "MAHALLIY BYUDJET DAROMADLARINI SHAKLLANTIRISHNING AMALDAGI HOLATI TAHLILI",
"a": "Tursunova Zulayxo Abdujobir qizi",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/3._Tursunova_Z._maqola__TIFT_jurnal_1-son_2.pdf"
},
{
"f": "2025-yil 1-son",
"n": 3,
"full": false,
"t": "“YASHIL” IQTISODIYOTGA O‘TISH DAVRIDA HUDUDLAR SOLIQ SALOHIYATINI OSHIRISHNING ASOSIY YO‘NALISHLARI.",
"a": "Baxtiyorov Umid Qaxramon o’g’li.",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/4._Baxtiyorov_U._maqola__TIFT_jurnal_1-son_2.pdf"
},
{
"f": "2025-yil 1-son",
"n": 4,
"full": false,
"t": "O‘ZBEKISTONDA DAVLAT BYUDJETI DAROMAD VA XARAJATLARINING TARKIBI VA DINAMIKASI TAHLILI",
"a": "Abduraximova Saida Axmadjanovna G‘ulomjonov Farruxbek Doniyorjon o‘g‘li",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/2_%D0%90%D0%B1%D0%B4%D1%83%D1%80%D0%B0%D1%85%D0%B8%D0%BC%D0%BE%D0%B2%D0%B0_%D0%A1_maqola_TIFT_jurnal_1_son_2.pdf"
},
{
"f": "2025-yil 1-son",
"n": 5,
"full": false,
"t": "МОЛИЯВИЙ ФАНЛАР ТАРАҚҚИЁТИНИ ҲАМ, АВВАЛО, ҲАР БИР ТУШУНЧА (АТАМА, СЎЗ)НИНГ АНИҚ ВА ЎЗ ЎРНИДА ИШЛАТИЛИШИ БЕЛГИЛАБ БЕРАДИ",
"a": "Тоҳир Сатторович Маликов",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/17._%D0%9C%D0%BE%D0%BB.%D1%82%D0%B5%D1%85.%D0%A2.%D0%A1._%D0%9C%D0%90%D0%BB%D0%B8%D0%BA%D0%BE%D0%B2.pdf"
},
{
"f": "2025-yil 1-son",
"n": 6,
"full": false,
"t": "RESPUBLIKAMIZDA ISLOM MOLIYASINI RIVOJLANTIRISHNING USTUVOR YO‘NALISHLARI",
"a": "Ibragimov Abdunazar Narzullayevich, Bositova Samiya Bahodir qizi",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Ibaragimov_A.N._Bositova_S.%D0%92.pdf"
},
{
"f": "2025-yil 1-son",
"n": 7,
"full": false,
"t": "O’ZBEKISTON RESPUBLIKASIDA XALQARO YOZGI MAKTAB VA TA’LIM TURIZMINI RIVOJLANTIRISHNINING ISTIQBOLLI YO’NALISHLARI",
"a": "Adilova Go’zal Abdazovna Qoraboyev Nuriddin Pardaboy o’g’li Odilova Malika Abdushukur qizi",
"c": "Bank, kredit, davlat qarzi.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/7_Adilova_G__Qoraboyev_N_Ozbekistonda_Talim_turizmni_rivojlantirish.pdf"
},
{
"f": "2025-yil 1-son",
"n": 8,
"full": false,
"t": "O‘ZBEKISTON BANK TIZIMIDA RAQAMLI VALYUTALAR VA YASHIL INVESTITSIYALAR INTEGRATSIYASINI TAKOMILLASHTIRISH",
"a": "Nodirov Azizxon Asrorovich",
"c": "Bank, kredit, davlat qarzi.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/24._%D0%9D%D0%BE%D0%B4%D0%B8%D1%80%D0%BE%D0%B2_%D0%9C%D0%B0%D2%9B%D0%BE%D0%BB%D0%B0_1-son_PDF.pdf"
},
{
"f": "2025-yil 1-son",
"n": 9,
"full": false,
"t": "ДАВЛАТ-ХУСУСИЙ ШЕРИКЛИК ЛОЙИҲАЛАРИ ИНВЕСТИЦИОН ФАОЛИЯТИНИ ТАКОМИЛЛАШТИРИШ",
"a": "Хайдаров Низамиддин Хамраевич",
"c": "Iqtisodiyotni Raqamlashtirish, agro va nano texnololgiyalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/19_%D0%9D_%D0%A5%D0%B0%D0%B8%D0%B4%D0%B0%D1%80%D0%BE%D0%B2_%D0%94%D0%A5%D0%A8_%D0%BC%D0%B0%D2%9B%D0%BE%D0%BB%D0%B0_%D0%96%D1%83%D1%80%D0%BD%D0%B0%D0%BB_1_%D1%81%D0%BE%D0%BD%D0%B8%D0%B3%D0%B0_2025_%D0%B8%D0%B8%D0%BB.pdf"
},
{
"f": "2025-yil 1-son",
"n": 10,
"full": false,
"t": "КУЗАТИЛМАЙДИГАН ИҚТИСОДИЁТДА ХУФИЁНА ДАРОМАДЛАРНИ КАМАЙТИРИШ: ЎЗБЕКИСТОНДАГИ ИСЛОҲОТЛАР ВА САМАРАЛИ ЧОРАЛАР",
"a": "Ғиёсов Азизбек Аъзамович",
"c": "Iqtisodiyotni Raqamlashtirish, agro va nano texnololgiyalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/23._%D0%90.%D0%90.%D2%92%D0%B8%D0%B5%D1%81%D0%BE%D0%B2_%D0%BC%D0%B0%D0%BA%D0%BE%D0%BB%D0%B0_%D1%82%D0%B0%D0%B8%D0%B5%D1%80%D0%B8.pdf"
},
{
"f": "2025-yil 1-son",
"n": 11,
"full": false,
"t": "TURIZM OBYEKTLARIDAGI MA’LUMOTLARNI QAYTA ISHLASHNI OPTIMALLASHTIRISHDA TEXNOLOGIK YONDASHUVLAR.",
"a": "Toshtemirov Xojiakbar Qahramon o‘g‘li",
"c": "Iqtisodiyotni Raqamlashtirish, agro va nano texnololgiyalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/TURIZM_OBYEKTLARIDAGI_MALUMOTLARNI_QAYTA_ISHLASHNI_OPTIMALLASHT_p69EJvI.pdf"
},
{
"f": "2025-yil 1-son",
"n": 12,
"full": false,
"t": "AFG‘ONISTONDA GIYOHVAND MODDALARI SAVDOSINING RIVOJLANISH DINAMIKASI",
"a": "Xudayberdiyev Ikrom Ilxomjon o‘g‘li",
"c": "Xorijiy mamlakatlar iqtisodiyoti.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/14_Xudayberdiyev_I_maqola_Rukn_11_Ozbekiston_2030.pdf"
},
{
"f": "2025-yil 1-son",
"n": 13,
"full": false,
"t": "О‘ZBЕKIЅTОN VA HINDIЅTОN O‘RTASIDA TURIZM YO‘LIDA HAMKORLIK ALOQALARI VA ISTIQBOLLARI",
"a": "Sayfullayev Behruz Dilshod o‘g‘li,",
"c": "Xorijiy mamlakatlar iqtisodiyoti.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/21._Sayfullayev_B.D._Rukn_11._Ozbekiston_-_2030_3.pdf"
},
{
"f": "2025-yil 1-son",
"n": 14,
"full": false,
"t": "MUQADDAS JOYLARNING ARXITEKTURA YODGORLIKLARI VA UNING IJTIMOIY MADANIYATGA KO‘RSATGAN TAʼSIRI",
"a": "Kalanov Komil Kulaxmatovich",
"c": "Xorijiy mamlakatlar iqtisodiyoti.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/22_Kalonov_K_maqola_09_04_Rukn_11_Ozbekiston_2030.pdf"
},
{
"f": "2025-yil 1-son",
"n": 15,
"full": false,
"t": "IQTISODIY MODELLARDA MATRITSALAR VA CHIZIQLI TENGLAMALAR SISTEMASINING QOʻLLANILISHI",
"a": "Eshimbetov Muzaffar Reyimbayevich Eshimbetov Joʻrabek Reyimbayevich",
"c": "Kichik, biznes va xususiy tadbirkorlik.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/16._Eshimbetov_Muzaffar_Matematika_kafedrasi.pdf"
},
{
"f": "2025-yil 1-son",
"n": 16,
"full": false,
"t": "O‘ZBEKISTON RESPUBLIKASIDA IQTISODIY FAOL AHOLINI SAMARALI ISH BILAN BANDLIGINI TA’MINLASH ISTIQBOLLARI",
"a": "Adilova Guzal Abdazovna Madaminjanov Bekzodbek Ayubxan o’g’li",
"c": "Kichik, biznes va xususiy tadbirkorlik.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/12._Adilova_G_maqola_TIFT_jurnal_1_son_3._09.04.25.pdf"
},
{
"f": "2025-yil 1-son",
"n": 17,
"full": false,
"t": "YANGI O‘ZBEKISTONNING MINTAQAVIY TASHQI VA IQTISODIY SIYOSATI MARKAZIY OSIYODA BARQAROR RIVOJLANISHNING MUHIM GAROVI",
"a": "Ergasheva Xulkar Quldoshevna",
"c": "Kichik, biznes va xususiy tadbirkorlik.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/9._Ergasheva_X.Q._maqola_-_Rukn_11._Ozbekiston_-_2030.pdf"
},
{
"f": "2025-yil 1-son",
"n": 18,
"full": false,
"t": "QORAQALPOG‘ISTON RESPUBLIKASIDA AHOLI DAROMADLARI DINAMIKASI",
"a": "Rahimboyev Muxtorbek Ikrom o’g’li.",
"c": "Kichik, biznes va xususiy tadbirkorlik.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/5._Rahimboyev_M._maqola__TIFT_jurnal_1-son_2.pdf"
},
{
"f": "2025-yil 1-son",
"n": 19,
"full": false,
"t": "ISLOMIY ILMLAR SHAKLLANISHIDA MUSULMON SHARQIDAGI QADIMGI MADANIY AN’ANALARNING O‘RNI",
"a": "Jurayev Sherali Soibnazar o‘g‘li",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/11._Jurayev_Sh.__maqola_-_Rukn_11._Ozbekiston_-_2030.pdf"
},
{
"f": "2025-yil 1-son",
"n": 20,
"full": false,
"t": "ABU RAYHON BERUNIYNING “HINDISTON” ASARI VA UNING TARIXSHUNOSLIGI",
"a": "Jumayev Buron Ulug‘murotovich",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/10._Jumayev_B._maqola_-_Rukn_11._Ozbekiston_-_2030.pdf"
},
{
"f": "2025-yil 1-son",
"n": 21,
"full": false,
"t": "O’ZBEKISTON RESPUBLIKASINING FRANKOFON DAVLATLAR BILAN ALOQALARI TARIXI VA DAVLAT SIYOSATI",
"a": "Boboyev Doniyor Xaydaraliyevich",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/8._Boboyev_D._maqola_-_Rukn_11._Ozbekiston_2030.pdf"
},
{
"f": "2025-yil 1-son",
"n": 22,
"full": false,
"t": "О‘ZBEK XALQI ANTROPOLOGIK TIPI DASTLAB TARKIB TOPGAN MAKON VA ZAMON",
"a": "Sayfullayev Samarbek Dilshod o’g’li",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/6._Sayfullayev_S_D_maqola_Rukn_11_Ozbekiston_2030_copy.pdf"
},
{
"f": "2025-yil 1-son",
"n": 23,
"full": false,
"t": "YOSH VA GENDER XUSUSIYATLARI KONTEKSTIDA IJTIMOIY TARMOQLARGA QARAMLIK MUAMMOSIGA DOIR TADQIQOTLAR TAVSIFI",
"a": "Ahrorov Suhrobxon Yunusovich",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/1._Maqola_Ahrorov_S._TIFT_jurnal.Asosiy.pdf"
},
{
"f": "2025-yil 1-son",
"n": 24,
"full": false,
"t": "ХУЛҚ-АТВОР АРХИТЕКТОНИКАСИ ВА МОДЕЛЛАРИНИНГ ПСИХОЛОГИК ХАРАКТЕРИСТИКАСИ",
"a": "Садриддинов Сухроб Рустамжонович Садриддинов Сайроб Рустамжонович Садриддинова Дилнура Рустамжонз",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/15._S.R.Sadriddinov_1_%D0%A5%D1%83%D0%BB%D0%BA_%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D0%BB%D0%B0%D1%80%D0%B8_2.pdf"
},
{
"f": "2025-yil 1-son",
"n": 25,
"full": false,
"t": "Ragnar Frisch ,Yan Tinbergen ilmiy ijodiy faoliyati",
"a": "Nizamiddin Xaydarov Abdullayev Axrorjon",
"c": "Nobel mukofoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/20._Nobel_mukofoti_1969_Jurnal_uchun_tayyor.pdf"
},
{
"f": "2025-yil 1-son",
"n": 0,
"full": true,
"t": "1-son | 2025 - Moliya va intellektual texnologiyalar ilmiy tahliliy jurnal",
"a": "",
"c": "",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/full_1-son_.pdf"
},
{
"f": "2025-yil 2-son",
"n": 1,
"full": false,
"t": "Татқиқотчи ва муштарийлар илмий фаолиятга ривож!",
"a": "Бош муҳаррир, TIFT университети Ректори А. Нодиров",
"c": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/BOSH_MUHARRIRDAN_-_MUSHTARIYLARGA.pdf"
},
{
"f": "2025-yil 2-son",
"n": 2,
"full": false,
"t": "O‘ZBEKISTON RESPUBLIKASI BYUDJET TASHKILOTLARIDA BYUDJET MABLAG‘LARIDAN FOYDALANISHNING NATIJADORLIGI BO‘YICHA HISOB TIZIMINI SHAKLLANTIRISH",
"a": "Jo’rayev Qobiljon Olimjonovich",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʻURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Jorayev_Qobiljon_Olimjonovich__.pdf"
},
{
"f": "2025-yil 2-son",
"n": 3,
"full": false,
"t": "O‘ZBEKISTONDA ISLOM MOLIYASI INSTRUMENTLARINI TADBIQ QILISH IMKONIYATLARI",
"a": "Abdullayev Suxrobiddin Ismoilovich",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʻURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/6._Abdullayev__Suxrobiddin._Ismoilovich_4.pdf"
},
{
"f": "2025-yil 2-son",
"n": 4,
"full": false,
"t": "DAVLAT XARIDLARI TIZIMIDA MOLIYAVIY NAZORATNI AMALGA OSHIRISHNING DOLZARB MASALALARI",
"a": "O‘roqov Uchqun Yunusovich",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʻURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A3.%D0%8E%D1%80%D0%BE%D2%9B%D0%BE%D0%B2.pdf"
},
{
"f": "2025-yil 2-son",
"n": 5,
"full": false,
"t": "MAMLAKATLARARO BOJLAR URUSHINING SOLIQ SIYOSATIGA TA’SIRI",
"a": "Giyasov Sarvar A’zamovich",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʻURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/11._%D0%A1.%D0%93%D0%B8%D1%8F%D1%81%D0%BE%D0%B2_%D0%BC%D0%B0%D0%BA%D0%BE%D0%BB%D0%B0.pdf"
},
{
"f": "2025-yil 2-son",
"n": 6,
"full": false,
"t": "AKSIYADORLIK TIJORAT BANKLARIDA LIKVIDLIKNI TA'MINLASH UCHUN QO'LLANILADIGAN USULLARNI TAKOMILLASHTIRISH",
"a": "To‘rayev Abdurahim Nortojiyevich , Abdusalomova Xurshidabonu Abrorbek qizi",
"c": "BANK, TURIZM, DAVLAT QARZI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/2._Torayev_A.pdf"
},
{
"f": "2025-yil 2-son",
"n": 7,
"full": false,
"t": "TIJORAT BANKLARI FAOLIYATINI TRANSFORMATLASHDA BANK XIZMATLARINI TAKOMILLASHTIRISH YO‘LLARI",
"a": "Berdiqulova Manzura Rahmonqulovna",
"c": "BANK, TURIZM, DAVLAT QARZI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/5._Berdiqulova_Manzura.pdf"
},
{
"f": "2025-yil 2-son",
"n": 8,
"full": false,
"t": "AKSIYADORLIK TIJORAT BANKLARINING KREDIT SIYOSATINI AMALGA OSHIRISH BILAN BOG‘LIQ MUAMMO VA ISTIQBOLLAR",
"a": "Eshonqulov Azamat Abdiraximovich",
"c": "BANK, TURIZM, DAVLAT QARZI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/10.__Eshonqulov_Azamat_Abdiraximovich.pdf"
},
{
"f": "2025-yil 2-son",
"n": 9,
"full": false,
"t": "ТИЖОРАТ БAНКЛАРНИНГ РЕCУРС БАЗАСИНИ МУСТAҲКАМ- ЛАШНИНГ ХОРИЖ ТАЖРИБАСИ",
"a": "Султанмуратова Дилрабо Шайлавбековна",
"c": "BANK, TURIZM, DAVLAT QARZI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/15._Sultonmurodova_D._maqola__TIFT_jurnal_1-son_2.pdf"
},
{
"f": "2025-yil 2-son",
"n": 10,
"full": false,
"t": "АKSIYADORLIK JAMIYATLARIDA AUDITORLIK TEKSHIRUVI JARAYONIDA YUZAGA KELADIGAN MUOMMOLAR",
"a": "Xalimova Mayram Xamidovna",
"c": "BUXGALTERIYA HISOBI VA IQTISODIY TAHLIL",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/3._Xalimova_Mayram_Maqola.pdf"
},
{
"f": "2025-yil 2-son",
"n": 11,
"full": false,
"t": "АКЦИЯДОРЛИК ЖАМИЯТЛАРИДА ҲИСОБ СИЁСАТИНИ ХАЛҚАРО СТАНДАРТЛАР АСОСИДА ТУЗИШ",
"a": "Жўраев Дилмурод Холмўминович",
"c": "BUXGALTERIYA HISOBI VA IQTISODIY TAHLIL",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/1._Jorayev_Dilmurod_Xolmominovich_07_07_2025.pdf"
},
{
"f": "2025-yil 2-son",
"n": 12,
"full": false,
"t": "FARMATSEVTIKA KORXONALARIDA DORI VOSITALARINI ISHLAB CHIQARISHDAGI CHIQINDILAR VA YO‘QOTISHLARNI BUXGALTERIYA HISOBIDA AKS ETTIRISH MASALALARI",
"a": "Turdikulova Gulshad Nurmamatovna",
"c": "BUXGALTERIYA HISOBI VA IQTISODIY TAHLIL",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/8._Turdikulova_Gulshad.pdf"
},
{
"f": "2025-yil 2-son",
"n": 13,
"full": false,
"t": "AKSIYADORLIK TIJORAT BANKLARINING MOLIYAVIY HISOBOTLARINI XALQARO STANDARTLAR ASOSIDA TUZISHNI TAKOMILLASHTIRISH YO’LLARI",
"a": "Eshonqulov Azamat Abdiraximovich",
"c": "QIMMATLI QOGʻOZLAR BOZORI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/7.__Eshonqulov_Azamat_Abdiraximovich.pdf"
},
{
"f": "2025-yil 2-son",
"n": 14,
"full": false,
"t": "AKSIYADORLIK JAMIYATLARIDA XODIMLARNING SAMARADORLIGINI BELGILOVCHI KO’RSATKICHLAR TAHLILI",
"a": "Suvonov Bekniyoz Baxtiyor o’g’li",
"c": "QIMMATLI QOGʻOZLAR BOZORI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/4._Suvonov_Bekniyoz.pdf"
},
{
"f": "2025-yil 2-son",
"n": 15,
"full": false,
"t": "СИФАТЛИ ТАЪЛИМ – ИЖТИМОИЙ, ИҚТИСОДИЙ ВА СИЁСИЙ БАРҚАРОРЛИК ТАЯНЧИ",
"a": "Nodirov Azizxon Asrorovich",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/12_%D0%A1%D0%B8%D1%84%D0%B0%D1%82%D0%BB%D0%B8_%D1%82%D0%B0%D1%8A%D0%BB%D0%B8%D0%BC__%D0%B8%D0%B6%D1%82%D0%B8%D0%BC%D0%BE%D0%B8%D0%B9_%D0%B8%D2%9B%D1%82%D0%B8%D1%81%D0%BE%D0%B4%D0%B8%D0%B9_%D0%B2%D0%B0_%D1%81%D0%B8%D1%91%D1%81%D0%B8%D0%B9_%D0%B1%D0%B0%D1%80%D2%9B%D0%B0%D1%80%D0%BE%D1%80%D0%BB%D0%B8%D0%BA_%D1%82%D0%B0%D1%8F%D0%BD%D1%87%D0%B8.pdf"
},
{
"f": "2025-yil 2-son",
"n": 16,
"full": false,
"t": "TA‘LIMDA RAQAMLI TRANSFORMATSIYANI JORIY ETISHNING ASOSIY BOSQICHLARI VA ISTIQBOLI",
"a": "Normatov Ibroximali Xolmamatovich",
"c": "«Oʼzbekiston – 2030» strategiyasidagi 5 ta yoʼnalish va 100 ta maqsaddan birini gavdalantirigan maqolalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/14._Professor_Normatov_Ibroximali_Xolmamatovich.pdf"
},
{
"f": "2025-yil 2-son",
"n": 17,
"full": false,
"t": "Paul A. Samuelson илмий-ижодий фаолияти.",
"a": "Хайдаров Низамиддин. Нормуродов Алибек",
"c": "Nobel mukofoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Paul_A._Samuelson_%D0%B8%D0%BB%D0%BC%D0%B8%D0%B8-%D0%B8%D0%B6%D0%BE%D0%B4%D0%B8%D0%B8_%D1%84%D0%B0%D0%BE%D0%BB%D0%B8%D1%8F%D1%82%D0%B8..pdf"
},
{
"f": "2025-yil 2-son",
"n": 0,
"full": true,
"t": "2-son | 2025 - Moliya va intellektual texnologiyalar ilmiy tahliliy jurnal to'liq shakli",
"a": "",
"c": "",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/ilovepdf_merged.pdf"
},
{
"f": "2025-yil 3-son",
"n": 1,
"full": false,
"t": "Татқиқотчи ва муштарийлар илмий фаолиятга ривож!",
"a": "Бош муҳаррир, TIFT университети Ректори А. Нодиров",
"c": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/af556b7d-7c40-470b-a9ef-dc9d4ec71461.pdf"
},
{
"f": "2025-yil 3-son",
"n": 2,
"full": false,
"t": "РОЛЬ НАЛОГОВОГО ПОТЕНЦИАЛА В РАЗВИТИИ ЭКОНОМИКИ",
"a": "Baxtiyorov Umid Qaxramon o’g’li.",
"c": "Moliya, soliq, byudjet, sug'urta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%91%D0%B0%D1%85%D1%82%D0%B8%D1%91%D1%80%D0%BE%D0%B2_%D0%A3%D0%BC%D0%B8%D0%B4_%D0%A0%D0%BE%D0%BB%D1%8C_%D0%BD%D0%B0%D0%BB%D0%BE%D0%B3%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE_%D0%BF%D0%BE%D1%82%D0%B5%D0%BD%D1%86%D0%B8%D0%B0%D0%BB%D0%B0_%D0%B2_%D1%80%D0%B0%D0%B7%D0%B2%D0%B8%D1%82%D0%B8%D0%B8_%D1%8D%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8%D0%BA%D0%B8.pdf"
},
{
"f": "2025-yil 3-son",
"n": 3,
"full": false,
"t": "МОЛИЯВИЙ ФАНЛАР ТАРАҚҚИЁТИНИ ҲАМ, АВВАЛО, ҲАР БИР ТУШУНЧА (АТАМА, СЎЗ)НИНГ АНИҚ ВА ЎЗ ЎРНИДА ИШЛАТИЛИШИ БЕЛГИЛАБ БЕРАДИ",
"a": "Тоҳир Сатторович Маликов",
"c": "Moliya, soliq, byudjet, sug'urta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A2.%D0%9C%D0%90%D0%9B%D0%98%D0%9A%D0%9E%D0%92_%D0%9C%D0%BE%D0%BB.%D1%82%D0%B5%D1%85._%D0%9D.%D2%B2._-_2.pdf"
},
{
"f": "2025-yil 3-son",
"n": 4,
"full": false,
"t": "Умумий овқатланиш соҳасини ривожлантиришда солиқ сиёсати ва маъмурчилигини такомиллаштириш",
"a": "Xolbo'ta Ismatov",
"c": "Moliya, soliq, byudjet, sug'urta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A5.%D0%91.%D0%98%D1%81%D0%BC%D0%B0%D1%82%D0%BE%D0%B2_-08042025.pdf"
},
{
"f": "2025-yil 3-son",
"n": 5,
"full": false,
"t": "ТИЖОРАТ БAНКЛАРНИНГ РЕCУРС БАЗАСИНИ МУСТAҲКАМЛАШНИНГ ХОРИЖ ТАЖРИБАСИ",
"a": "Султанмуратова Дилрабо Шайлавбековна",
"c": "Bank, kredit, davlat qarzi.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A1%D1%83%D0%BB%D1%82%D0%B0%D0%BD%D0%BC%D1%83%D1%80%D0%BE%D0%B4%D0%BE%D0%B2%D0%B0_%D0%94%D0%B8%D0%BB%D1%80%D0%B0%D0%B1%D0%BE_%D0%A2%D0%B8%D0%B6%D0%BE%D1%80%D0%B0%D1%82_%D0%B1a%D0%BD%D0%BA%D0%BB%D0%B0%D1%80%D0%BD%D0%B8%D0%BD%D0%B3_%D1%80%D0%B5c%D1%83%D1%80%D1%81_%D0%B1%D0%B0%D0%B7%D0%B0%D1%81%D0%B8%D0%BD%D0%B8_%D0%BC%D1%83%D1%81%D1%82_9LRasky.pdf"
},
{
"f": "2025-yil 3-son",
"n": 6,
"full": false,
"t": "TIJORAT BANKLARIDA KREDIT RISKLARINI SUG‘URTALASH VA DIVERSIFIKATSIYA QILISH MEXANIZMLARINI TAKOMILLASHTIRISH",
"a": "Eshboyev Shahobiddin Anorqul o‘g‘li",
"c": "Bank, kredit, davlat qarzi.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%AD%D1%88%D0%B1%D0%BE%D0%B5%D0%B2_%D0%A8%D0%B0%D2%B3%D0%BE%D0%B1%D0%B8%D0%B4%D0%B4%D0%B8%D0%BD_Tijorat_banklarida_kredit_risklarini_sugurtalash.pdf"
},
{
"f": "2025-yil 3-son",
"n": 7,
"full": false,
"t": "PORTFEL SHAKLLANTIRISHDA KAPITAL BOZORIDAGI MAVJUD MUAMMOLAR TAHLILI",
"a": "Sindarov Fazliddin Qaxramonivich",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A1%D0%B8%D0%BD%D0%B4%D0%B0%D1%80%D0%BE%D0%B2_%D0%A4%D0%B0%D0%B7%D0%BB%D0%B8%D0%B4%D0%B4%D0%B8%D0%BD_O%CA%BBzbekiston_respublikasida_meva_sabzavot_mah_OWNwCCA.pdf"
},
{
"f": "2025-yil 3-son",
"n": 8,
"full": false,
"t": "O`ZBEKISTON IQTISODIY SIYOSATINI SHAKLLANTIRISHDA OUKEN QONUNING AMALIY AHAMIYATI",
"a": "Sadriddinova Sevinchxon Sadriddin qiz",
"c": "Moliyaviy menejment va marketing.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A1%D0%B0%D0%B4%D1%80%D0%B8%D0%B4%D0%B4%D0%B8%D0%BD%D0%BE%D0%B2%D0%B0_%D0%A1%D0%B5%D0%B2%D0%B8%D0%BD%D1%87%D1%85%D0%BE%D0%BD_Ozbekiston_iqtisodiy_siyosatini_shakllantirishda.pdf"
},
{
"f": "2025-yil 3-son",
"n": 9,
"full": false,
"t": "QORAQALPOG‘ISTON RESPUBLIKASIDA RAQAMLI TEXNOLOGIYALARNI JORIY ETISH ORQALI AHOLI BANDLIGINI OSHIRISH",
"a": "Rahimboyev Muxtorbek Ikrom o’g’li.",
"c": "Iqtisodiyotni Raqamlashtirish, agro va nano texnologiyalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A0%D0%B0%D1%85%D0%B8%D0%BC%D0%B1%D0%BE%D0%B5%D0%B2_%D0%9C%D1%83%D1%85%D1%82%D0%BE%D1%80%D0%B1%D0%B5%D0%BA_Qoraqalpogiston_respublikasida_raqamli_texn_4GycPwx.pdf"
},
{
"f": "2025-yil 3-son",
"n": 10,
"full": false,
"t": "КОРХОНАЛАР ФАОЛИЯТИНИ РАҚАМЛАШТИРИШ ЖАРАЁНЛАРИ ВА УЛАРДА БИЗНЕС-МОДЕЛЛАРНИНГ ТУТГАН ЎРНИ",
"a": "Бегалов Баҳодир Абдусаломович, Дадабаева Раъно Акрамовна",
"c": "Iqtisodiyotni Raqamlashtirish, agro va nano texnologiyalar.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%91%D0%B5%D0%B3%D0%B0%D0%BB%D0%BE%D0%B2_%D0%91.%D0%90._%D0%94%D0%B0%D0%B4%D0%B0%D0%B1%D0%BE%D0%B5%D0%B2%D0%B0_%D0%A0..pdf"
},
{
"f": "2025-yil 3-son",
"n": 11,
"full": false,
"t": "BUXGALTERIYA HISOBINING MILLIY STANDARTLARI ASOSIDA HISOB YURITISH: NAZARIY VA AMALIY YONDASHUVLAR",
"a": "A’zamov Shohjahon Muhammadrasulxon Baxtiyor o‘g‘li",
"c": "Buxgalteriya hisobi va iqtisodiy tahlil.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%90%D1%8A%D0%B7%D0%B0%D0%BC%D0%BE%D0%B2_%D0%A8%D0%BE%D1%85%D0%B6%D0%B0%D1%85%D0%BE%D0%BD_Buxgalteriya_hisobining_milliy_standartlari_asosida.pdf"
},
{
"f": "2025-yil 3-son",
"n": 12,
"full": false,
"t": "FARMATSEVTIKA KORXONALARIDA BUXGALTERIYA HISOBI TIZIMINI XALQARO STANDARTLAR ASOSIDA TAKOMILLASHTIRISH YO‘LLARI",
"a": "Turdikulova Gulshad Nurmamatovna",
"c": "Buxgalteriya hisobi va iqtisodiy tahlil.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A2%D1%83%D1%80%D0%B4%D0%B8%D0%BA%D1%83%D0%BB%D0%BE%D0%B2%D0%B0_%D0%93%D1%83%D0%BB%D1%88%D0%B0%D0%B4_Tijorat_banklarida_kredit_risklarini_sugurtalash.pdf"
},
{
"f": "2025-yil 3-son",
"n": 13,
"full": false,
"t": "TURKIYA IQTISODIYOTI: MUAMMO VA YECHIMLAR",
"a": "Ergashev Urolbek Berkinovich",
"c": "Xorijiy mamlakatlar iqtisodiyoti.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Ergashev_O.B._8-rukn.pdf"
},
{
"f": "2025-yil 3-son",
"n": 14,
"full": false,
"t": "BUSINESS ETHICS AND CULTURE",
"a": "Urazov Mansur Musurmanovich",
"c": "Xorijiy mamlakatlar iqtisodiyoti.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A3%D1%80%D0%B0%D0%B7%D0%BE%D0%B2_%D0%9C%D0%B0%D0%BD%D1%81%D1%83%D1%80._-_Business_ethics_and_culture.pdf"
},
{
"f": "2025-yil 3-son",
"n": 15,
"full": false,
"t": "OLIY TA’LIM TIZIMIDA TA’LIM SIFATNI RIVOJLANTIRISHNING IJTIMOIY OMILLARI",
"a": "Hakimova Gulmira To‘xtatoshevna",
"c": "Ta‘lim tizimi",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Hakimova_Gulmira_Toxtatoshevna_vC0xX9X.pdf"
},
{
"f": "2025-yil 3-son",
"n": 16,
"full": false,
"t": "OʻZBEKISTON RESPUBLIKASIDA MEVA-SABZAVOT MAHSULOTLARI ISHLAB CHIQARISH JARAYONLARINI IQTISODIY TAHLILI",
"a": "Anorboyeva Baxtijamol Daniyar qizi",
"c": "Tarmoqlar iqtisidoyoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%90%D0%BD%D0%B0%D1%80%D0%B1%D0%B0%D0%B5%D0%B2%D0%B0_%D0%91%D0%B0%D1%85%D1%82%D0%B8%D0%B6%D0%B0%D0%BC%D0%BE%D0%BB_O%CA%BBzbekiston_respublikasida_meva_sabzavot_m_7gKpafo.pdf"
},
{
"f": "2025-yil 3-son",
"n": 17,
"full": false,
"t": "SPORT VA YOSHLAR SALOMATLIGI MILLIY XAVFSIZLIK GAROVI",
"a": "KAGARMANOVA ANISA AXMETOVNA",
"c": "Tarmoqlar iqtisidoyoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9A%D0%B0%D0%B3%D0%B0%D1%80%D0%BC%D0%BE%D0%BD%D0%BE%D0%B2%D0%B0_%D0%90%D0%BD%D0%B8%D1%81%D0%B0_Sport_va_yoshlar_salomatligi_milliy_xavfsizli_4kBFl3B.pdf"
},
{
"f": "2025-yil 3-son",
"n": 18,
"full": false,
"t": "Simon Kuznets ilmiy-ijodiy faoliyati",
"a": "Хайдаров Низамиддин. Нормуродов Алибек",
"c": "Nobel mukofoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Nobel_mukofoti_1971_Simon_Kuznets.pdf"
},
{
"f": "2025-yil 3-son",
"n": 0,
"full": true,
"t": "3-son | 2025 - Moliya va intellektual texnologiyalar ilmiy tahliliy jurnal to'liq shakli",
"a": "",
"c": "",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/FULL_12.pdf"
},
{
"f": "2025-yil 4-son",
"n": 1,
"full": false,
"t": "Татқиқотчи ва муштарийлар илмий фаолиятга ривож!",
"a": "Бош муҳаррир, TIFT университети Ректори А. Нодиров",
"c": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/1f48ffe8-7734-47ad-ba30-5331cb466624.pdf"
},
{
"f": "2025-yil 4-son",
"n": 2,
"full": false,
"t": "SOLIQ YUKINI HISOBLASH USLUBLARI",
"a": "Azizov Olim Maxmudovich",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʼURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/SOLIQ_YUKINI_HISOBLASH_USLUBLARI22%D0%B7.pdf"
},
{
"f": "2025-yil 4-son",
"n": 3,
"full": false,
"t": "AKSIYADORLIK JAMIYATLARI TOMONIDAN CHIQARILGAN AKSIYALARNING IKKILAMCHI BOZORDA SAVDOSI SAMARADORLIGINI OSHIRISH.",
"a": "Berdiqulova Manzura Raxmonqulovna",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʼURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/AKSIYADORLIK_JAMIYATLARI_TOMONIDAN_CHIQARILGAN.pdf"
},
{
"f": "2025-yil 4-son",
"n": 4,
"full": false,
"t": "O’ZBEKISTONDA IQTISODIY O’SISHNING ATROF MUHIT ZARARLANISHIGA TA’SIRINI EKONOMETRIK PROGNOZLASH: KUZNETS EGRI CHIZIG’INI YONDASHUVI",
"a": "Sarvar Mamasoliyev",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʼURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/OZBEKISTONDA_IQTISODIY_OSISHNING_ATROF_MUHIT.pdf"
},
{
"f": "2025-yil 4-son",
"n": 5,
"full": false,
"t": "ВАЖНОСТЬ ФИНАНСОВОЙ ПОДДЕРЖКИ ВНЕШНЕЭКОНОМИЧЕСКОЙ ДЕЯТЕЛЬНОСТИ ПРЕДПРИЯТИЙ",
"a": "Пулатова Мохира Бахтиёровна",
"c": "MOLIYA, SOLIQ, BYUDJET, SUGʼURTA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A4%D0%98%D0%9D%D0%90%D0%9D%D0%A1%D0%9E%D0%92%D0%9E%D0%99_%D0%9F%D0%9E%D0%94%D0%94%D0%95%D0%A0%D0%96%D0%9A%D0%98.pdf"
},
{
"f": "2025-yil 4-son",
"n": 6,
"full": false,
"t": "TIJORAT BANKLARIDA KREDIT RISKLARINI BOSHQARISHNING XORIJIY TAJRIBALARNI O‘ZBEKISTON BANK AMALIYOTIGA TATBIQ ETISH IMKONIYATLARI.",
"a": "Norova Nozima Nabiyevna",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/TIJORAT_BANKLARIDA_KREDIT_RISKLARINI_Bs855R8.pdf"
},
{
"f": "2025-yil 4-son",
"n": 7,
"full": false,
"t": "ДИНАМИКА И СТРУКТУРА ВНЕШНЕГО ДОЛГА УЗБЕКИСТАН.",
"a": "Одинаев Фаёзхон Зиядуллаевич",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%94%D0%98%D0%9D%D0%90%D0%9C%D0%98%D0%9A%D0%90_%D0%98_%D0%A1%D0%A2%D0%A0%D0%A3%D0%9A%D0%A2%D0%A3%D0%A0%D0%90_%D0%92%D0%9D%D0%95%D0%A8%D0%9D%D0%95%D0%93%D0%9E_%D0%94%D0%9E%D0%9B%D0%93%D0%90_%D0%A3%D0%97%D0%91%D0%95%D0%9A%D0%98%D0%A1%D0%A2%D0%90%D0%9D.pdf"
},
{
"f": "2025-yil 4-son",
"n": 8,
"full": false,
"t": "BANKLARNING CHAKANA XIZMATLARI TIZIMIDA CHAKANA KREDITLARNING OʻRNI VA RIVOJLANISH OMILLARI TAHLILI",
"a": "Nodirov Azizxon Asrorovich",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9D%D0%BE%D0%B4%D0%B8%D1%80%D0%BE%D0%B2_%D0%90_BANKLARNING_CHAKANA_XIZMATLARI_TIZIMIDA_CHAKANA.pdf"
},
{
"f": "2025-yil 4-son",
"n": 9,
"full": false,
"t": "OʻZBEKISTON BANK TIZIMI MOLIYAVIY BARQARORLIGINI TAʼMINLASHDA KAPITAL VA LIKVIDLILIK KOʻRSATKICHLARI TAHLILI",
"a": "Xolmamatov Farhodjon Kubayevich",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/BANK_TIZIMI_MOLIYAVIY_BARQARORLIGINI_TA%CA%BCMINLASHDA_KAPITAL_2.pdf"
},
{
"f": "2025-yil 4-son",
"n": 10,
"full": false,
"t": "TIJORAT BANKLARIDA YASHIL DEPOZITLAR TIZIMINI RIVOJLANTIRISH ISTIQBOLLARI",
"a": "Norova Nozima Nabiyevna",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/TIJORAT_BANKLARIDA_YASHIL_DEPOZITLAR_TIZIMINI_2R06dF1.pdf"
},
{
"f": "2025-yil 4-son",
"n": 11,
"full": false,
"t": "BLOKCHEYN TEXNOLOGIYASIDAN FOYDALANGAN HOLDA ENERGIYA SAVDOSI VA MOLIYALASHTIRISH",
"a": "Otaxonov Alisherbek Abdumutal o‘g‘li",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/BLOKCHEYN_TEXNOLOGIYASIDAN_FOYDALANGAN_JupAzAN.pdf"
},
{
"f": "2025-yil 4-son",
"n": 12,
"full": false,
"t": "МАXСУС ИҚТИСОДИЙ ЗОНАЛАР ИНВЕСТИЦИЯ МУҲИТИ ЖОЗИБАДОРЛИГИНИ ОШИРИШ МУАММОЛАРИ",
"a": "Умирзоқов Жасъур Артиқбой ўғли",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9C%D0%90X%D0%A1%D0%A3%D0%A1_%D0%98%D2%9A%D0%A2%D0%98%D0%A1%D0%9E%D0%94%D0%98%D0%99_%D0%97%D0%9E%D0%9D%D0%90%D0%9B%D0%90%D0%A0_%D0%98%D0%9D%D0%92%D0%95%D0%A1%D0%A2%D0%98%D0%A6%D0%98%D0%AF.pdf"
},
{
"f": "2025-yil 4-son",
"n": 13,
"full": false,
"t": "КОРХОНАНИ САМАРАЛИ БОШКАРИШДА ХОДИМЛАР ФАОЛЛИГИНИ ОШИРИШ",
"a": "Садриддинова Севинчхон Садриддин қизи",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9A%D0%9E%D0%A0%D0%A5%D0%9E%D0%9D%D0%90%D0%9D%D0%98_%D0%A1%D0%90%D0%9C%D0%90%D0%A0%D0%90%D0%9B%D0%98_%D0%91%D0%9E%D0%A8%D0%9A%D0%90%D0%A0%D0%98%D0%A8%D0%94%D0%90_%D0%A5%D0%9E%D0%94%D0%98%D0%9C%D0%9B%D0%90%D0%A0_%D0%A4%D0%90%D0%9E%D0%9B%D0%9B%D0%98%D0%93%D0%98%D0%9D%D0%98_%D0%9E%D0%A8%D0%98%D0%A0%D0%98%D0%A8.pdf"
},
{
"f": "2025-yil 4-son",
"n": 14,
"full": false,
"t": "INVESTITSION JOZIBADORLIKNI OSHIRISH –KORXONALARNING RAQOBATBARDOSHLIGINI OSHIRISHNING MUHIM SHARTIDIR",
"a": "Karimova Dilafruz Sadriddin qizi",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/2._INVESTITSION_JOZIBADORLIKNI_OSHIRISH_15.pdf"
},
{
"f": "2025-yil 4-son",
"n": 15,
"full": false,
"t": "O‘YINLI TA’LIM ORQALI TA‘LIM SAMARADORLIGINI OSHIRISH",
"a": "Tahirov Behzod Nasriddinovich",
"c": "Ta'lim tizimi",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/OYINLI_TALIM_ORQALI_TALIM_SAMARADORLIGINI_OSHIRISH.pdf"
},
{
"f": "2025-yil 4-son",
"n": 16,
"full": false,
"t": "OLIY TA’LIM TIZIMIDA TA’LIM SIFATINI BOSHQARISH VA RIVOJLANTIRISHDA IJTIMOIY HAMDA TASHKILIY OMILLARNING RO’LI.",
"a": "Yokubova Dilafruz Mirjabborovna",
"c": "Ta'lim tizimi",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/OLIY_TALIM_TIZIMIDA_TALIM_SIFATINI_BOSHQARISH.pdf"
},
{
"f": "2025-yil 4-son",
"n": 17,
"full": false,
"t": "ANALYSIS OF SPEECH-LIKE SIGNALS FOR THE UZBEK LANGUAGE",
"a": "Musadjanova Dilobar Abduvakhidovna",
"c": "Ta'lim tizimi",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/ANALYSIS_OF_SPEECH-LIKE_SIGNALS_FOR_THE_UZBEK_LANGUAGE.pdf"
},
{
"f": "2025-yil 4-son",
"n": 18,
"full": false,
"t": "O‘ZBEKISTONDA SMART SUV MENEJMENTIDAN FOYDALANISH ISTIQBOLLARI",
"a": "Sarvar Mamasoliyev",
"c": "Moliyaviy menejment va marketing.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/OZBEKISTONDA_SMART_SUV_MENEJMENTIDAN_FOYDALANISH.pdf"
},
{
"f": "2025-yil 4-son",
"n": 19,
"full": false,
"t": "СИСТЕМНЫЙ ПОДХОД В ПОДДЕРЖКИ УПРАВЛЕНИЯ И КОНТРОЛЬ ЭФФЕКТИВНОСТИ ПРЕДПРИЯТИЙ",
"a": "Умурзоков Элёр Ўктамович",
"c": "Moliyaviy menejment va marketing.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A1%D0%98%D0%A1%D0%A2%D0%95%D0%9C%D0%9D%D0%AB%D0%99_%D0%9F%D0%9E%D0%94%D0%A5%D0%9E%D0%94_%D0%92_%D0%9F%D0%9E%D0%94%D0%94%D0%95%D0%A0%D0%96%D0%9A%D0%98_%D0%A3%D0%9F%D0%A0%D0%90%D0%92%D0%9B%D0%95%D0%9D%D0%98%D0%AF.pdf"
},
{
"f": "2025-yil 4-son",
"n": 20,
"full": false,
"t": "RAQAMLASHTIRISHNING AYLANMA IQTISODIYOTDAGI O‘RNI",
"a": "Nasriddinov Burxoniddin Zuxriddin o’g’li",
"c": "IQTISODIYOTNI RAQAMLASHTIRISH, AGRO VA NANO TEXNOLOGIYALAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/RAQAMLASHTIRISHNING_AYLANMA_IQTISODIYOTDAGI_ORNI.pdf"
},
{
"f": "2025-yil 4-son",
"n": 21,
"full": false,
"t": "РАҚАМЛИ ИҚТИСОДИЁТНИНГ ШАКЛЛАНИБ БОРИШ ЖАРАЁНЛАРИНИ СТАТИСТИК ҲИСОБГА ОЛИШНИНГ УСЛУБИЙ ЁНДАШУВЛАРИ",
"a": "Баходир Абдусаломович Бегалов Шахбоз Уктамович Жонодилов Абдусамад Баходирович Абдусаломов",
"c": "IQTISODIYOTNI RAQAMLASHTIRISH, AGRO VA NANO TEXNOLOGIYALAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A0%D0%90%D2%9A%D0%90%D0%9C%D0%9B%D0%98_%D0%98%D2%9A%D0%A2%D0%98%D0%A1%D0%9E%D0%94%D0%98%D0%81%D0%A2%D0%9D%D0%98%D0%9D%D0%93_%D0%A8%D0%90%D0%9A%D0%9B%D0%9B%D0%90%D0%9D%D0%98%D0%91_%D0%91%D0%9E%D0%A0%D0%98%D0%A8.pdf"
},
{
"f": "2025-yil 4-son",
"n": 22,
"full": false,
"t": "KONSOLIDATSIYALASHGAN PUL OQIMLARI HISOBOTINING TUZILISHI VA TAHLILINI TAKOMILLASHTIRISH",
"a": "Eshonqulov Azamat Abdiraximovich",
"c": "BUXGALTERIYA HISOBINING MILLIY STANDARTLARI ASOSIDA HISOB YURITISH: NAZARIY VA AMALIY YONDASHUVLAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/PUL_OQIMLARI_HISOBOTINING.pdf"
},
{
"f": "2025-yil 4-son",
"n": 23,
"full": false,
"t": "ADDRESSING THE TRAINING NEEDS OF TOURISM STAFF FOR SUSTAINABLE PRACTICES IN THE GREEN ECONOMY ERA",
"a": "Dadamuxamedova Mushtariy Maxmudjon qizi",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/ADDRESSING_THE_TRAINING_NEEDS_OF_TOURISM_STAFF.pdf"
},
{
"f": "2025-yil 4-son",
"n": 24,
"full": false,
"t": "TURIZM INFRATUZILMASINI RAQAMLASHTIRISH VA OBYEKTLARNI RIVOJLANTIRISHNING TASHKILIY-IQTISODIY ASOSLARI.",
"a": "Toshtemirov Xojiakbar Qahramon o‘g‘li",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/TURIZM_INFRATUZILMASINI_RAQAMLASHTIRISH_VA.pdf"
},
{
"f": "2025-yil 4-son",
"n": 25,
"full": false,
"t": "OʻZBEKISTONDA YENGIL SANOATNING RAQAMLI TRANSFORMATSIYASI",
"a": "Quldasheva Nargiza Komoliddin qizi",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/YENGIL_SANOATNING_RAQAMLI_TRANSFORMATSIYASI_%D0%8E%D0%B7%D0%B1..pdf"
},
{
"f": "2025-yil 4-son",
"n": 26,
"full": false,
"t": "O‘ZBEKISTON AKSIYADORLIK JAMIYATLARI QIMMATLI QOG‘OZLARNING IKKILAMCHI BOZORIDAGI AMALDAGI HOLATINI TAHLILI",
"a": "Berdiqulova Manzura Rahmonqulovna",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/OZBEKISTON_AKSIYADORLIK_JAMIYATLARI_QIMMATLI_QOGOZLARNING_IKKILAMCHI.pdf"
},
{
"f": "2025-yil 4-son",
"n": 27,
"full": false,
"t": "ЗНАЧЕНИЕ ЭТИКИ В ИНЖЕНЕРНОЙ ДЕЯТЕЛЬНОСТИ",
"a": "Сайфуллаев Самарбек Дилшод o'g'li",
"c": "O‘ZBEKISTON - 2030 STRATEGIYASI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%97%D0%9D%D0%90%D0%A7%D0%95%D0%9D%D0%98%D0%95_%D0%AD%D0%A2%D0%98%D0%9A%D0%98_%D0%92_%D0%98%D0%9D%D0%96%D0%95%D0%9D%D0%95%D0%A0%D0%9D%D0%9E%D0%99_%D0%94%D0%95%D0%AF%D0%A2%D0%95%D0%9B%D0%AC%D0%9D%D0%9E%D0%A1%D0%A2%D0%98.pdf"
},
{
"f": "2025-yil 4-son",
"n": 28,
"full": false,
"t": "МИГРАЦИОННЫЕ ПРОЦЕССЫ В ЦЕНТРАЛЬНОЙ АЗИИ: АНАЛИЗ И НАПРАВЛЕНИЯ РЕГУЛИРОВАНИЯ",
"a": "Salimov Sherzod Yunusovich",
"c": "O‘ZBEKISTON - 2030 STRATEGIYASI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9C%D0%98%D0%93%D0%A0%D0%90%D0%A6%D0%98%D0%9E%D0%9D%D0%9D%D0%AB%D0%95_%D0%9F%D0%A0%D0%9E%D0%A6%D0%95%D0%A1%D0%A1%D0%AB_%D0%92_%D0%A6%D0%95%D0%9D%D0%A2%D0%A0%D0%90%D0%9B%D0%AC%D0%9D%D0%9E%D0%99_%D0%90%D0%97%D0%98%D0%98.pdf"
},
{
"f": "2025-yil 4-son",
"n": 29,
"full": false,
"t": "BILINGUAL ONGNING LINGVOKOGNITIV KONSEPTUAL SINTEZ MEXANIZMLARI",
"a": "Komilova Gulmira Olimovna",
"c": "O‘ZBEKISTON - 2030 STRATEGIYASI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/BILINGUAL_ONGNING_LINGVOKOGNITIV_KONSEPTUAL_SINTEZ.pdf"
},
{
"f": "2025-yil 4-son",
"n": 30,
"full": false,
"t": "Jon R. Hiks ilmiy-ijodiy faoliyati",
"a": "Хайдаров Низамиддин. Нормуродов Алибек",
"c": "Nobel mukofoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Nobel_mukofoti_1972_John_R_wyIMkbh._Hicks_Kenneth_J._Arrow.pdf"
},
{
"f": "2025-yil 4-son",
"n": 0,
"full": true,
"t": "4-son | 2025 - Moliya va intellektual texnologiyalar ilmiy tahliliy jurnal to'liq shakli",
"a": "",
"c": "",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/FULL_PDF__merged.pdf"
},
{
"f": "2026-yil 1-son",
"n": 1,
"full": false,
"t": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"a": "Бош муҳаррир, TIFT университети Ректори А. Нодиров",
"c": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/4f844bd3-c052-4b74-9e8e-c76428003fa2.pdf"
},
{
"f": "2026-yil 1-son",
"n": 2,
"full": false,
"t": "DAROMAD SOLIG‘I STAVKALARINI QO‘LLASHNING O‘ZIGA XOS XUSUSIYATLARI",
"a": "Giyasov Sarvar A’zamovich",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/DAROMAD_SOLIGI_STAVKALARINI_QOLLASHNING.pdf"
},
{
"f": "2026-yil 1-son",
"n": 3,
"full": false,
"t": "JISMONIY SHAXSLAR DAROMADLARINI SOLIQQA TORTISH TIZIMINI YANADA TAKOMILLASHTIRISHGA OID",
"a": "Boltayev Jo‘rabek Yusufovich , Sidiqov Rauf Rustamovich.",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/JISMONIY_SHAXSLAR_DAROMADLARINI_SOLIQQA_TORTISH.pdf"
},
{
"f": "2026-yil 1-son",
"n": 4,
"full": false,
"t": "XO‘JALIK YURITUVCHI SUBYEKTLARDA PUL MABLAGʻLARI HISOBINI EKONOMETRIK MODELLASHTIRISH VA PROGNOZLASHNI TAKOMILLASHTIRISH",
"a": "Raxmonov Sherzod Sherkulovich",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/XOJALIK_YURITUVCHI_SUBYEKTLARDA_PUL_MABLAG%CA%BBLARI.pdf"
},
{
"f": "2026-yil 1-son",
"n": 5,
"full": false,
"t": "SUG‘URTA KOMPANIYALARNI MOLIYAVIY XAVFSIZLIGINI TA`MINLASHNING TASHKILIY-IQTISODIY MEXANIZMLARI",
"a": "Nosirov Jasur Tursunpulotovich",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/SUGURTA_KOMPANIYALARNI_MOLIYAVIY_XAVFSIZLIGINI_TAMINLASHNING_TASHKILIY.pdf"
},
{
"f": "2026-yil 1-son",
"n": 6,
"full": false,
"t": "CHET EL VALYUTASIDAGI OPERATSIYALAR VA VALYUTA KURSLARINING O'ZGARISHI HISOBI",
"a": "To‘rayev Abdurahim Nortojiyevich , Abdusalomova Xurshidabonu Abrorbek qizi",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/CHET_EL_VALYUTASIDAGI_OPERATSIYALAR_VA_VALYUTA.pdf"
},
{
"f": "2026-yil 1-son",
"n": 7,
"full": false,
"t": "O‘ZBEKISTONDA ISLOM BANK TIZIMINI JORIY ETISHNING INSTITUTSIONAL MODELI VA UNING IQTISODIY RIVOJLANISHGA TA’SIRI",
"a": "Voitov Aziz Botirovich",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Islom_banklari_maqola_2.pdf"
},
{
"f": "2026-yil 1-son",
"n": 8,
"full": false,
"t": "O'ZBEKISTON BANK TIZIMIDA “OPEN BANKING” TEXNOLOGIYASINI JORIY ETISH ISTIQBOLLARI",
"a": "Sidiqov Rauf Rustamovich , Allamurotov Azimbek Jahongir o‘g‘li.",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Ozbekiston_bank_tizimi.__Maqola..pdf"
},
{
"f": "2026-yil 1-son",
"n": 9,
"full": false,
"t": "QO‘SHMA KORXONALARDA JORIY AKTIVLAR HISOBINI XALQARO STANDARTLAR ASOSIDA YURITISH TARTIBI",
"a": "Yusupov Asror Maxmanazar o‘g‘li.",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/QOSHMA_KORXONALARDA_JORIY_AKTIVLAR_HISOBINI_XALQARO.pdf"
},
{
"f": "2026-yil 1-son",
"n": 10,
"full": false,
"t": "SANOATDA INNOVATSIYALARNI RIVOJLANTIRISHNI MOLIYAVIY RAG‘BATLANTIRISH: STRATEGIK YONDASHUVLAR VA AMALIY VOSITALAR",
"a": "Olimjonov Odil Olimovich , Baxriddinov Nodirbek Zamirdinovich",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/SANOATDA_INNOVATSIYALARNI_RIVOJLANTIRISHNI_MOLIYAVIY.pdf"
},
{
"f": "2026-yil 1-son",
"n": 11,
"full": false,
"t": "КОРПОРАТИВ БОШҚАРУВ ТИЗИМИНИ ЖОРИЙ ЭТИШНИНГ ХОРИЖ ТАЖРИБАСИ",
"a": "Тўраев Абдураҳим Нортожиевич , Тўраева Моҳира Гулмирзаевна",
"c": "Moliyaviy menejment va marketing.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9A%D0%9E%D0%A0%D0%9F%D0%9E%D0%A0%D0%90%D0%A2%D0%98%D0%92_%D0%91%D0%9E%D0%A8%D2%9A%D0%90%D0%A0%D0%A3%D0%92_%D0%A2%D0%98%D0%97%D0%98%D0%9C%D0%98%D0%9D%D0%98_%D0%96%D0%9E%D0%A0%D0%98%D0%99_%D0%AD%D0%A2%D0%98%D0%A8%D0%9D%D0%98%D0%9D%D0%93.pdf"
},
{
"f": "2026-yil 1-son",
"n": 12,
"full": false,
"t": "O‘ZBEKISTON IQTISODIYOTINING 2025 YILDA MAKROMOLIYAVIY HOLATI TAHLILI",
"a": "Azizov Olim Maxmudovich",
"c": "Moliyaviy menejment va marketing.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A3%D0%B7%D0%B1%D0%B5%D0%BA%D0%B8%D1%81%D1%82%D0%BE%D0%BD_%D0%B8%D2%9B%D1%82%D0%B8%D1%81%D0%BE%D0%B4%D0%B8%D1%91%D1%82%D0%B8%D0%BD%D0%B8%D0%BD%D0%B3_2025_%D0%B9%D0%B8%D0%BB%D0%B4%D0%B0_%D0%BC%D0%B0%D0%BA%D1%80%D0%BE%D0%BC%D0%BE%D0%BB%D0%B8%D1%8F%D0%B2%D0%B8%D0%B9_%D2%B3%D0%BE%D0%BB%D0%B0%D1%82%D0%B8_%D1%82%D0%B0%D1%85%D0%BB%D0%B8%D0%BB%D0%B8_3.pdf"
},
{
"f": "2026-yil 1-son",
"n": 13,
"full": false,
"t": "MATRITSALARNING INFORMATSION TEXNOLOGIYALARNING BA’ZI MASALALARIDA QO‘LLANILISHI",
"a": "Eshimbetov Muzaffar Reyimbayevich, Farhodillayev Dostonbek Toxirjon o’g’li",
"c": "IQTISODIYOTNI RAQAMLASHTIRISH, AGRO VA NANO TEXNOLOGIYALAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/MATRITSALARNING_INFORMATSION_TEXNOLOGIYALARNING.pdf"
},
{
"f": "2026-yil 1-son",
"n": 14,
"full": false,
"t": "TURIZM INFRATUZILMASIDA MA’LUMOTLARNI QAYTA ISHLASH JARAYONLARINI RAQAMLASHTIRISH VA OPTIMALLASHTIRISH",
"a": "Toshtemirov Xojiakbar Qahramon o'g'li, Ma'rufov Sardorbek Bahromjon o'g'li",
"c": "IQTISODIYOTNI RAQAMLASHTIRISH, AGRO VA NANO TEXNOLOGIYALAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/TURIZM_INFRATUZILMASIDA_MALUMOTLARNI.pdf"
},
{
"f": "2026-yil 1-son",
"n": 15,
"full": false,
"t": "KONSOLIDATSIYALASHGAN MOLIYAVIY HISOBOTDA ICHKI GURUH OPERATSIYALARINI ELIMINATSIYA QILISHNING NAZARIY VA AMALIY MUAMMOLARI",
"a": "Eshonqulov Azamat Abdiraximovich",
"c": "BUXGALTERIYA HISOBINING MILLIY STANDARTLARI ASOSIDA HISOB YURITISH: NAZARIY VA AMALIY YONDASHUVLAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/KONSOLIDATSIYALASHGAN_MOLIYAVIY_HISOBOTDA_ICHKI.pdf"
},
{
"f": "2026-yil 1-son",
"n": 16,
"full": false,
"t": "HISOB SIYOSATINI TUZISHNING TASHKILIY JIHATLARI",
"a": "To‘rayev Abdurahim Nortojiyevich, Masudova Nozimaxon Ma’rufjon qizi",
"c": "BUXGALTERIYA HISOBINING MILLIY STANDARTLARI ASOSIDA HISOB YURITISH: NAZARIY VA AMALIY YONDASHUVLAR",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/HISOB_SIYOSATINI_TUZISHNING_TASHKILIY_JIHATLARI.pdf"
},
{
"f": "2026-yil 1-son",
"n": 17,
"full": false,
"t": "O‘ZBEKISTON AKSIYADORLIK JAMIYATLARI QIMMATLI QOG‘OZLARNING IKKILAMCHI BOZORIDAGI AMALDAGI HOLATINI TAHLILI",
"a": "Berdiqulova Manzura Raxmonqulovna",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/OZBEKISTON_AKSIYADORLIK_JAMIYATLARI_QIMMATLI_QOGOZLARNING_IKKIL_Vp7XRsf.pdf"
},
{
"f": "2026-yil 1-son",
"n": 18,
"full": false,
"t": "Sug‘urta kompaniyalarining moliyaviy barqarorligini oshirishda noproporsional qayta sug‘urtani amaliyotga joriy etish",
"a": "Moyliyev Murod Baxtiyorovich",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Sugurta_kompaniyalarining_moliyaviy_barqarorligini_oshirishda.pdf"
},
{
"f": "2026-yil 1-son",
"n": 19,
"full": false,
"t": "Vasiliy Vasilyevich Leontev",
"a": "Хайдаров Низамиддин. Нормуродов Алибек",
"c": "Nobel mukofoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Nobel_mukofoti_1973_Vasiliy_Leontef.pdf"
},
{
"f": "2026-yil 1-son",
"n": 0,
"full": true,
"t": "1-son | 2026 - Moliya va intellektual texnologiyalar ilmiy tahliliy jurnal to'liq shakli",
"a": "",
"c": "",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/FULLL_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 1,
"full": false,
"t": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"a": "Бош муҳаррир, TIFT университети Ректори А. Нодиров",
"c": "BOSH MUHARRIRDAN - MUSHTARIYLARGA",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A2%D0%90%D0%91%D0%A0%D0%98%D0%9A.pdf"
},
{
"f": "2026-yil 2-son",
"n": 2,
"full": false,
"t": "ISLOM MOLIYASI SOHASIDA MALAYZIYA TAJRIBASI VA UNING O‘ZBEKISTON UCHUN IJOBIY JIHATLARI",
"a": "Azizov Olim Maxmudovich",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/15._Azizov_O.M._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 3,
"full": false,
"t": "НАУЧНО-ТЕОРЕТИЧЕСКИЕ ОСНОВЫ И МЕЖДУНАРОДНАЯ ПРАКТИКА ОЦЕНКИ НАЛОГОВЫХ РАСХОДОВ",
"a": "Giyasov Sarvar A’zamovich",
"c": "Moliya, soliq, byudjet, sugʼurta.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/S.Giyasov_maqola_ann_2.pdf"
},
{
"f": "2026-yil 2-son",
"n": 4,
"full": false,
"t": "TIJORAT BANKLARI CHAKANA XIZMATLAR BOZORINI KENGAYTIRISHNING USTUVOR YOʻNALISHLARI",
"a": "Nodirov Azizxon Asrorovich",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9D%D0%BE%D0%B4%D0%B8%D1%80%D0%BE%D0%B2_%D0%90-TIJORAT_BANKLARI_CHAKANA_XIZMATLAR.pdf"
},
{
"f": "2026-yil 2-son",
"n": 5,
"full": false,
"t": "INFLYATSION BOSIMLARNI KAMAYTIRISHDA MARKAZIY BANK KOMMUNIKATSIYA SIYOSATINING AHAMIYATI",
"a": "Abduraximova Saida Axmadjanovna,Saidov Sardorbek Iskandarbekovich",
"c": "BANK, KREDIT, DAVLAT QARZI.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/5_17SH0oL._Abduraximova_S.A._Saidov_S.I._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 6,
"full": false,
"t": "NAMANGAN VILOYATI QURILISH MATERIALLARI SANOATIDA MODERNIZATSIYA JARAYONLARIGA TA’SIR ETUVCHI OMILLAR VA ULARNING IQTISODIY AHAMIYATI",
"a": "Adilova Guzal Abdazovna,Odilova Malika Abdushukur qizi",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/1._Adilova_G.A._Odilova_M.A._-.pdf"
},
{
"f": "2026-yil 2-son",
"n": 7,
"full": false,
"t": "KAPITAL TARKIBI VA KOMPANIYA QIYMATI: MODIGLIANI-MILLER NAZARIYASI RIVOJLANAYOTGAN BOZORLARDA",
"a": "Umarova Go‘zal G‘ayratovna,Rustamova Sevinch Ravshan qizi",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/6._Umarova_G._G._Rustamova_S.R._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 8,
"full": false,
"t": "INNOVATSION IQTISODIYOT SHAROITIDA KORXONALARDA INNOVATSION MARKETING KONSEPSIYASINI SHAKLLANTIRISHNING NAZARIY-USLUBIY ASOSLARI",
"a": "Mirzajonova Maftunaxon Jaxongir qizi",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/8._Mirzajonova_M.J._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 9,
"full": false,
"t": "O'ZBEKISTON MILLIY INVESTITSIYA JAMG'ARMASI (UzNIF) LOYIHASI: TASHKIL ETILISHIDAN BIRINCHI XALQARO IPO GACHA BO'LGAN TRANSFORMATSIYA JARAYONI VA UNING MARKAZIY OSIYO KAPITAL BOZORIGA TA'SIRI",
"a": "Azizov Odiljon Olimovich",
"c": "Investitsiya va innovatsiya.",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/14._Azizov_O.O._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 10,
"full": false,
"t": "HISOB SIYOSATLARI, HISOBLAB CHIQILGAN BAHOLARDAGI OʼZGARISHLAR VA XATOLAR (BHXS 8)",
"a": "Jo‘raev Dilmurod Xolmo‘minovich, Bositova Samiya Bahodir qizi",
"c": "Buxgalteriya hisobi va iqtisodiyot tahlil",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/18._Joraev_D.X._Bositova_S.%D0%92._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 11,
"full": false,
"t": "FOYDALANISH HUQUQI KO‘RINISHIDAGI AKTIVLAR VA IJARA MAJBURIYATLARINI QAYTA BAHOLASHNING NAZARIY MASALALARI",
"a": "Djumayeva Guzal Axtamovna",
"c": "Buxgalteriya hisobi va iqtisodiyot tahlil",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/21._Djumayeva_G.A._-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 12,
"full": false,
"t": "NEFT NARXI, VALYUTA KURSI VA MOLIYAVIY BARQARORLIK: NEFT EKSPORT QILUVCHI MAMLAKATLAR MISOLIDA VAR VA GREYNJER TAHLILI",
"a": "Narziyev Abror Baxtiyorovich",
"c": "Xorijiy mamlakatlar iqtisodiyoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/9._Narziyev_A.B._-_Neft_narxi_valyuta_kursi_va_moliyaviy_barqarorlik.pdf"
},
{
"f": "2026-yil 2-son",
"n": 13,
"full": false,
"t": "O‘ZBEKISTON–TOJIKISTON IQTISODIY HAMKORLIGINING ZAMONAVIY HOLATI VA RIVOJLANISH ISTIQBOLLARI",
"a": "Sheraliyev Nurali Sherali oʻgʻli",
"c": "Xorijiy mamlakatlar iqtisodiyoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/19._Sheraliyev_N.S._-.pdf"
},
{
"f": "2026-yil 2-son",
"n": 14,
"full": false,
"t": "CHANGING TRENDS IN POPULATION EMPLOYMENT AND INCOME IN THE REPUBLIC OF KARAKALPAKSTAN",
"a": "Mukhtorbek Rahimboyev, Alibek Normurodov",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/2._Rahimboyev_M.M._Normurodov_A.A_-_.pdf"
},
{
"f": "2026-yil 2-son",
"n": 15,
"full": false,
"t": "OʻZBEKISTON KIMYO SANOATINING TRANSFORMATSION RIVOJLANISH TENDENSIYALARI VA SANOAT SIYOSATI SAMARADORLIGINI BAHOLASH",
"a": "Odilova Malika Abdushukur qizi",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/11._Odilova_M.%D0%90._-.pdf"
},
{
"f": "2026-yil 2-son",
"n": 16,
"full": false,
"t": "ЭКОНОМИЧЕСКАЯ ЭФФЕКТИВНОСТЬ СОЛНЕЧНОЙ И ВЕТРОВОЙ ЭНЕРГЕТИИКИ",
"a": "Махкамова Надира Саидмуратовна",
"c": "TARMOQLAR IQTISODIYOTI",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9C%D0%B0%D1%85%D0%BA%D0%B0%D0%BC%D0%BE%D0%B2%D0%B0_%D0%9D.%D0%A1._%D0%AD%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC.%D1%8D%D1%84%D1%84%D0%B5%D0%BA%D1%82._%D1%81%D0%BE%D0%BB%D0%BD._%D0%B8_%D0%B2%D0%B5%D1%82%D1%80.%D1%81%D1%82..pdf"
},
{
"f": "2026-yil 2-son",
"n": 17,
"full": false,
"t": "Gunnar Myrdal, Fridrix fon Hayek",
"a": "Хайдаров Низамиддин. Нормуродов Алибек",
"c": "Nobel mukofoti",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Nobel_mukofoti_1974_Gunnar_Myrda_Fridrix_fon_Hayek_2.pdf"
},
{
"f": "2026-yil 2-son",
"n": 0,
"full": true,
"t": "2-son | 2026 - Moliya va intellektual texnologiyalar ilmiy tahliliy jurnal to'liq shakli",
"a": "",
"c": "",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/FULLLL.pdf"
},
{
"f": "2026-yil 3-son",
"n": 1,
"full": false,
"t": "DAVLAT XARIDLARIDA OʻRTACHA BOZOR VA BOSHLANGʻICH NARXNI ANIQLASH METODOLOGIYASINI JORIY ETISH MASALALARI",
"a": "O‘roqov Uchqun Yunusovich",
"c": "Молия, солиқ, бюджет, суғурта",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%94%D0%B0%D0%B2%D0%BB%D0%B0%D1%82_%D1%85%D0%B0%D1%80%D0%B8%D0%B4%D0%BB%D0%B0%D1%80%D0%B8%D0%B4%D0%B0_%D0%A3_%D0%8E%D1%80%D0%BE%D2%9B%D0%BE%D0%B2.pdf"
},
{
"f": "2026-yil 3-son",
"n": 2,
"full": false,
"t": "BUDJET JARAYONIDA JAMOATCHILIK ISHTIROKINI KENGAYTIRISH VA INKLYUZIVLIKNI OSHIRISH MEXANIZMLARI",
"a": "Umarov Umid Panjiyevich",
"c": "Молия, солиқ, бюджет, суғурта",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Umarov_Umid_Panjiyevich.pdf"
},
{
"f": "2026-yil 3-son",
"n": 3,
"full": false,
"t": "RESPUBLIKAMIZDA ISLOM MOLIYASINI RIVOJLANTIRISHNING USTUVOR YO‘NALISHLARI",
"a": "Ibragimov Abdunazar Narzullayevich, Bositova Samiya Bahodir qizi",
"c": "Молия, солиқ, бюджет, суғурта",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Ibaragimov_A_fNquRmI.N._Bositova_S.%D0%92.pdf"
},
{
"f": "2026-yil 3-son",
"n": 4,
"full": false,
"t": "ПУТИ ПОВЫШЕНИЯ ЭФФЕКТИВНОСТИ БЮДЖЕТНЫХ СРЕДСТВ В СФЕРЕ ГОСУДАРСТВЕННЫХ ЗАКУПОК",
"a": "Базаров Назиржон Сабирович ,Бахтияров Умид Кахраманович",
"c": "Молия, солиқ, бюджет, суғурта",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%91%D0%B0%D0%B7%D0%B0%D1%80%D0%BE%D0%B2_%D0%9D.%D0%A1._%D0%91%D0%B0%D1%85%D1%82%D0%B8%D1%8F%D1%80%D0%BE%D0%B2_%D0%A3.%D0%9A..pdf"
},
{
"f": "2026-yil 3-son",
"n": 5,
"full": false,
"t": "НАЛОГОВЫЕ ОТНОШЕНИЯ В ЭПОХУ ТИМУРИДОВ",
"a": "Тошматов Шухрат Амонович, Гиясов Сарвар Аъзамович",
"c": "Молия, солиқ, бюджет, суғурта",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%9D%D0%B0%D0%BB%D0%BE%D0%B3%D0%BE%D0%B2%D1%8B%D0%B5_%D0%BE%D1%82%D0%BD%D0%BE%D1%88%D0%B5%D0%BD%D0%B8%D1%8F_%D0%B2_%D1%8D%D0%BF%D0%BE%D1%85%D1%83_%D0%A2%D0%B8%D0%BC%D1%83%D1%80%D0%B8%D0%B4%D0%BE%D0%B2_.pdf"
},
{
"f": "2026-yil 3-son",
"n": 6,
"full": false,
"t": "MONETAR SIYOSAT TRANSMISSIYA MEXANIZMI VA KAPITAL HARAKATI SAMARADORLIGI",
"a": "Abduraximova Saida Axmadjanovna,Mamadjanov Farrux Gayratovich",
"c": "Банк, кредит, давлат қарзи",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Abduraximova_S.A._Mamadjanov_F.G._-_Monei.pdf"
},
{
"f": "2026-yil 3-son",
"n": 7,
"full": false,
"t": "KRIPTO AKTIVLARNI GLOBAL MOLIYAVIY BOSHQARUVDA FUNKSIONAL TARTIBGA SOLISH VA SOLIQ SHAFFOFLIGI: XALQARO MODELLAR VA O‘ZBEKISTON UCHUN INTEGRATSIYALASHGAN MEXANIZM",
"a": "Zafar Berdinazarov,Baxodir Davlatov",
"c": "Банк, кредит, давлат қарзи",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Zafar_Berdinazarov_Biznes_va_tadbirkorlik_%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B2%D0%B0%D0%BB%D1%8E%D1%82%D0%B0%D0%BB%D0%B0%D1%80.pdf"
},
{
"f": "2026-yil 3-son",
"n": 8,
"full": false,
"t": "KORPORATIV BOSHQARUV TIZIMIDA ICHKI AUDIT XIZMATINI TASHKIL ETISHNING O‘ZIGA XOS JIHATLARI",
"a": "To‘rayev Abdurahim Nortojiyevich,To‘rayeva Mohira Gulmirzayevna",
"c": "Бухгалтерия ҳисоби ва иқтисодий таҳлил",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Torayev_A_N__Torayeva_G_Korpoi.pdf"
},
{
"f": "2026-yil 3-son",
"n": 9,
"full": false,
"t": "MOLIYAVIY HISOBOT ISHONCHLILIGINI BAHOALSH KO’RSATKICHLARINI TAKOMILLASHTIRISH",
"a": "Suvonov Bekniyoz Baxtiyor o‘g‘li",
"c": "Бухгалтерия ҳисоби ва иқтисодий таҳлил",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Suvonov_B.B._-_Moliyaviy_hisobashtirish.pdf"
},
{
"f": "2026-yil 3-son",
"n": 10,
"full": false,
"t": "RAQAMLI IQTISODIYOT SHAROITIDA BUXGALTERIYA HISOBINI TRANSFORMATSIYA QILISH",
"a": "Sidiqov Rauf Rustamovich,Mirahmedov Abdulhafiz Alisher o‘g‘li",
"c": "Бухгалтерия ҳисоби ва иқтисодий таҳлил",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Sidiqov_R.R._Mirahmedov_A.pdf"
},
{
"f": "2026-yil 3-son",
"n": 11,
"full": false,
"t": "ISLOM MOLIYA TASHKILOTLARIDA BUXGALTERIYA HISOBIDA TASHKIL QILISH TARTIBI",
"a": "Ibragimov Abdunazar Narzullayevich",
"c": "Бухгалтерия ҳисоби ва иқтисодий таҳлил",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Ibragimov_A.Ni.pdf"
},
{
"f": "2026-yil 3-son",
"n": 12,
"full": false,
"t": "ГЛОБАЛЬНЫЕ РЫНКИ ПОД ДАВЛЕНИЕМ: РОЛЬ ЯПОНИИ КАК ВОЗМОЖНОГО ОЧАГА ФИНАНСОВОЙ НЕСТАБИЛЬНОСТИ",
"a": "Расул Шавкатович Салаев",
"c": "Хорижий мамлакатлар иқтисодиёти",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A1%D0%B0%D0%BB%D0%B0%D0%B5%D0%B2_%D0%A8.%D0%A0._-_%D0%93%D0%BB%D0%BE%D0%B1%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5_%D1%80%D1%8B%D0%BD%D0%BA%D0%B8_%D0%BF%D0%BE%D0%B4_%D0%B4%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%D0%BC_%D1%80%D0%BE%D0%BB%D1%8C_%D0%AF%D0%BF%D0%BE%D0%BD.pdf"
},
{
"f": "2026-yil 3-son",
"n": 13,
"full": false,
"t": "THE EXPERIENCE OF DEVELOPED COUNTRIES IN DIGITAL TRANSFORMATION OF UZBEKISTAN’S ECONOMY AND OPPORTUNITIES FOR ITS APPLICATION",
"a": "Tursinbayev Azizbek Nabijon o‘g‘li",
"c": "Хорижий мамлакатлар иқтисодиёти",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Tursinbayev_A.N._-_The_experience_of_dn.pdf"
},
{
"f": "2026-yil 3-son",
"n": 14,
"full": false,
"t": "KIMYO SANOATI KORXONALARINING IQTISODIY SALOHIYATINI BAHOLASHDA AHP USULI VA INTEGRAL INDEKSLARDAN FOYDALANISH",
"a": "Adilova Guzal Abdazovna,Odilova Malika Abdushukur qizi",
"c": "Тармоқлар иқтисодиёти",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Adilova_G.A._Odilova_M.A._-_Kimyo_sanoati_korxonalarili.pdf"
},
{
"f": "2026-yil 3-son",
"n": 15,
"full": false,
"t": "O‘ZBEKISTON RESPUBLIKASIDA KICHIK BIZNES VA XUSUSIY TADBIRKORLIKNI RIVOJLANTIRISH ISTIQBOLLARI",
"a": "Nurullayeva Shaxnoza Toxtasinovna,Saydullayeva Saodat Abdumajitovna",
"c": "Тармоқлар иқтисодиёти",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Nurullayeva_S.%D0%A2._Saydullayeva_S.%D0%90._-_Ozbekish_istiqbollari.pdf"
},
{
"f": "2026-yil 3-son",
"n": 16,
"full": false,
"t": "MEHNAT MIGRATSIYASINING DINAMIKASI VA TARKIBIY TUZILMASI",
"a": "Rahimboyev Muxtorbek Ikrom o‘g‘li",
"c": "Тармоқлар иқтисодиёти",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Rahimboyev_M.I._-_Mehnat_migratsiyasiningibiy_tuzilmasi.pdf"
},
{
"f": "2026-yil 3-son",
"n": 17,
"full": false,
"t": "СТРУКТУРНАЯ ТРАНСФОРМАЦИЯ ПРОМЫШЛЕННОСТИ УЗБЕКИСТАНА: СОВРЕМЕННЫЕ ТЕНДЕНЦИИ И РЕГИОНАЛЬНЫЕ ДИСПРОПОРЦИИ",
"a": "Холикова Рухсора Санджаровна",
"c": "Тармоқлар иқтисодиёти",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/%D0%A5%D0%BE%D0%BB%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0_%D0%A0.%D0%A1._-_%D0%A1%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D0%BD%D0%B0%D1%8F_%D1%82%D1%88%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE%D1%81%D1%82%D0%B8_%D0%A3%D0%B7%D0%B1%D0%B5%D0%BA%D0%B8%D1%81%D1%82%D0%B0%D0%BD%D0%B0.pdf"
},
{
"f": "2026-yil 3-son",
"n": 18,
"full": false,
"t": "OʻZBEK TILIDAGI YOZMA NUTQNI TABIIY TILNI QAYTA ISHLASH ASOSIDA AVTOMATIK TAHLIL QILISH USULLARINING QIYOSIY TAHLILI",
"a": "Zokirov Sanjar Zohidjon o‘g‘li,Xolmuminov Yusufjon Xolbuta o‘g‘li",
"c": "Сунъий интеллект ва ахборот технологиялари",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Ozbek_NLP_qiyosiy_tahlil_2.pdf"
},
{
"f": "2026-yil 3-son",
"n": 19,
"full": false,
"t": "РАЗВИТИЕ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА В ЭКОНОМИКЕ: ТЕНДЕНЦИИ, ЭФФЕКТЫ И ОГРАНИЧЕНИЯ",
"a": "Набиева Севара Султановна, Нормурадов Нурбек Сунатиллоевич,Зокиров Санжар Зохиджон угли",
"c": "Сунъий интеллект ва ахборот технологиялари",
"u": "https://back.tift-fintech.uz/media/bosh_sahifa/maqolalar/uz/Nabieva_v_ekonomike_1.pdf"
}
]
'@ | ConvertFrom-Json

$ok = 0; $skip = 0; $fail = @()
$i = 0
foreach ($it in $items) {
    $i++
    $dir = Join-Path $Journal $it.f
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    if ($it.full) {
        $name = "00. Toʻliq son ($($it.f)).pdf"
    } else {
        $who = if ($it.a) { Clean-Name $it.a 70 } else { 'Muallif koʻrsatilmagan' }
        $name = ('{0:D2}. {1} - {2}.pdf' -f $it.n, $who, (Clean-Name $it.t 110))
    }
    $dest = Join-Path $dir $name
    Write-Host ("[{0}/{1}] {2}\{3}" -f $i, $items.Count, $it.f, $name)
    if ((Test-Path -LiteralPath $dest) -and ((Get-Item -LiteralPath $dest).Length -gt 1000)) { $skip++; continue }
    $done = $false
    for ($try = 1; $try -le 3 -and -not $done; $try++) {
        try {
            Invoke-WebRequest -Uri $it.u -OutFile $dest -UseBasicParsing -TimeoutSec 120 -UserAgent 'Mozilla/5.0'
            $done = $true; $ok++
        } catch { Start-Sleep -Seconds (2 * $try) }
    }
    if (-not $done) { $fail += "$($it.f) | $name | $($it.u)" }
}

# Har bir son uchun mundarija (Excel'da ochiladi)
foreach ($g in ($items | Where-Object { -not $_.full } | Group-Object f)) {
    $g.Group | Sort-Object n | ForEach-Object {
        [pscustomobject]@{ 'Nº' = $_.n; 'Maqola nomi' = $_.t; 'Mualliflar' = $_.a; 'Yoʻnalish' = $_.c }
    } | Export-Csv -LiteralPath (Join-Path (Join-Path $Journal $g.Name) 'Mundarija.csv') -NoTypeInformation -Encoding UTF8
}

Write-Host ''
Write-Host "Tayyor: $ok ta yangi fayl yuklandi, $skip tasi oldin bor edi." -ForegroundColor Green
Write-Host "Papka: $Journal"
if ($fail.Count) {
    Write-Host "Yuklab boʻlmadi ($($fail.Count) ta) — skriptni qayta ishga tushiring:" -ForegroundColor Yellow
    $fail | ForEach-Object { Write-Host "  $_" }
}
Start-Process explorer.exe $Journal
