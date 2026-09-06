import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from journal.models import StaffMember

def populate():
    # Eski a'zolarni tozalash
    StaffMember.objects.all().delete()
    print("Eski staff memberlar o'chirildi.")

    staff_data = [
        # Rahbariyat (Leadership)
        {
            'full_name': 'Nodirov Azizxon Asrorovich',
            'position': 'editor_in_chief',
            'workplace': 'TIFT universiteti',
            'bio': 'TIFT universitetining Rektori.',
            'order': 1
        },
        {
            'full_name': 'Usmonov Nizomjon Aripovich',
            'position': 'deputy_editor',
            'workplace': 'TIFT universiteti',
            'bio': 'f.m.f. bo\'yicha PhD, docent. TIFT universitetining Ilmiy bo\'lim boshlig\'i.',
            'order': 2
        },
        {
            'full_name': 'Zokirov Sanjar Zohidjon o\'g\'li',
            'position': 'secretary',
            'workplace': 'TIFT universiteti',
            'bio': 'TIFT universitetining «Arxitektura va raqamli texnologiyalar» kafedrasi katta o\'qituvchisi.',
            'order': 3
        },

        # Tahririyat hay'ati (24 ta a'zo)
        {
            'full_name': 'Dushanov Rustam Xo\'jamovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'p.f.d., prof., TIFT universitetining «Pedagogika va psixologiya» kafedrasi mudiri (Pedagogika va psixologiya yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 4
        },
        {
            'full_name': 'Sheraliyev Javohirbek Jahongir o\'g\'li',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'i.f.b.f.d. (PhD), doc., TIFT universitetining «Iqtisodiyot va boshqaruv» kafedrasi mudiri (Iqtisodiyot va boshqaruv yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 5
        },
        {
            'full_name': 'Sayfullayev Behruz Dilshod o\'g\'li',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 't.f.b.f.d. (PhD), doc., TIFT universitetining «Ijtimoiy-gumanitar fanlar va tarix» kafedrasi mudiri (Ijtimoiy-gumanitar fanlar va tarix yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 6
        },
        {
            'full_name': 'Xayrullayev Rahmatilla Saydillayevich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 't.f.b.f.d. (PhD), doc., TIFT universitetining «Arxitektura va raqamli texnologiyalar» kafedrasi mudiri (Arxitektura va raqamli texnologiyalar yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 7
        },
        {
            'full_name': 'Xolmo\'minov Ilxom Abdixalilovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'f.f.b.f.d. (PhD), doc., TIFT universitetining «Xorijiy filologiya» kafedrasi mudiri (Xorijiy filologiya yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 8
        },
        {
            'full_name': 'Xolto\'rayev Xolsaid Fayzullayevich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'f.m.f.b.f.d. (PhD), doc., TIFT universitetining «Matematika» kafedrasi mudiri (Matematika yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 9
        },
        {
            'full_name': 'Ismoilov Farrux Israil o\'g\'li',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'f.f.b.f.d. (PhD), prof., TIFT universitetining «Jismoniy tarbiya va sport» kafedrasi mudiri (Jismoniy tarbiya va sport yo\'nalishidagi maqolalar bo\'yicha mas\'ul).',
            'order': 10
        },
        {
            'full_name': 'Asqarov Ahmadali Askarovich',
            'position': 'member',
            'workplace': 'O\'zbekiston milliy pedagogika universiteti',
            'bio': 'O\'zbekiston Fanlar akademiyasi akademigi, t.f.d., O\'zbekiston milliy pedagogika universiteti Tarix kafedrasi professori.',
            'order': 11
        },
        {
            'full_name': 'Shoumarov G\'ayrat Baxromovich',
            'position': 'member',
            'workplace': '"Profi University"',
            'bio': 'O\'zbekiston Fanlar akademiyasi akademigi, p.f.d., "Profi University" rektori.',
            'order': 12
        },
        {
            'full_name': 'Muxtorov Azamat',
            'position': 'member',
            'workplace': 'Toshkent davlat iqtisodiyot universiteti',
            'bio': 'f.f.d., prof., Toshkent davlat iqtisodiyot universitetining «Falsafa» kafedrasi mudiri.',
            'order': 13
        },
        {
            'full_name': 'Jo\'rayev Sayfiddin Axmatovich',
            'position': 'member',
            'workplace': 'Toshkent davlat sharqshunoslik universiteti',
            'bio': 's.f.d., Toshkent davlat sharqshunoslik universiteti Xalqaro munosabatlar kafedrasi professori.',
            'order': 14
        },
        {
            'full_name': 'Bulatov Saidaxbor Sobitovich',
            'position': 'member',
            'workplace': 'O\'zbekiston milliy pedagogika universiteti',
            'bio': 'p.f.d., O\'zbekiston milliy pedagogika universiteti «Tasviriy san\'at va muhandislik grafikasi» kafedrasi professori.',
            'order': 15
        },
        {
            'full_name': 'Jumabayev Abduvohid',
            'position': 'member',
            'workplace': 'Samarqand davlat universiteti',
            'bio': 'f.m.f.d., Samarqand davlat universiteti «Optika va spektroskopiya» kafedrasi professori.',
            'order': 16
        },
        {
            'full_name': 'Xolbekov Abdug\'ani Jumanazarovich',
            'position': 'member',
            'workplace': 'O\'zbekiston Milliy universiteti',
            'bio': 's.f.d., O\'zbekiston Milliy universitetining «Sotsiologiya» kafedrasi professori.',
            'order': 17
        },
        {
            'full_name': 'Kalonov Kamil Kulaxmatovich',
            'position': 'member',
            'workplace': 'Ijtimoiy-ma\'naviy tadqiqotlar instituti',
            'bio': 's.f.n., professor, Ijtimoiy-ma\'naviy tadqiqotlar instituti bosh ilmiy xodimi.',
            'order': 18
        },
        {
            'full_name': 'Mahmudov Behzod Xamidovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 't.f.n., docent, TIFT universitetining «Ijtimoiy-gumanitar fanlar va tarix» kafedrasi docenti.',
            'order': 19
        },
        {
            'full_name': 'Ergashev Uralbek Berkinovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'f.f.b.f.d. (PhD), TIFT universitetining «Ijtimoiy-gumanitar fanlar va tarix» kafedrasi docenti.',
            'order': 20
        },
        {
            'full_name': 'Xaydarov Fazliddin Ikromovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'p.f.n., TIFT universitetining «Pedagogika va psixologiya» kafedrasi professori.',
            'order': 21
        },
        {
            'full_name': 'Soyipova Madina Saidaxborovna',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 't.f.b.f.d. (PhD), TIFT universitetining «Arxitektura va raqamli texnologiyalar» kafedrasi docenti.',
            'order': 22
        },
        {
            'full_name': 'Hakimova Gulmira To\'xtatoshevna',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 'TIFT universitetining «Ta\'lim sifatini nazorat qilish» boshqarmasi boshlig\'i.',
            'order': 23
        },
        {
            'full_name': 'Jo\'rayev Ibrohim Bohodir o\'g\'li',
            'position': 'member',
            'workplace': 'O\'zDJTSU',
            'bio': 'p.f.b.f.d. (PhD), O\'zDJTSU, Inson resurslarini boshqarish bo\'limi bosh mutaxassisi, professor.',
            'order': 24
        },
        {
            'full_name': 'Igamberdiyev Obidjon Rubdulla o\'g\'li',
            'position': 'member',
            'workplace': 'O\'zDJTSU',
            'bio': 'p.f.d. (PhD), O\'zDJTSU, Futbol nazariyasi va uslubiyati kafedrasi docenti.',
            'order': 25
        },
        {
            'full_name': 'Rahimov Sherzod Abduvaxobjonovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 't.f.b.f.d. (PhD), TIFT universitetining «Ta\'limni raqamlashtirish va talabalarni amaliyotini tashkil etish» boshqarmasi menejeri.',
            'order': 26
        },
        {
            'full_name': 'Ahrorov Suhrabxon Yunusovich',
            'position': 'member',
            'workplace': 'TIFT universiteti',
            'bio': 's.f.n., TIFT universitetining «Pedagogika va psixologiya» kafedrasi docenti.',
            'order': 27
        },
    ]

    for item in staff_data:
        StaffMember.objects.create(**item)
    print(f"Jami {len(staff_data)} ta tahririyat a'zosi Latin alifbosida saqlandi!")

if __name__ == '__main__':
    populate()
