from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from journal.models import User, Journal, JournalIssue, ArticleCategory, Article, StaffMember, ReviewRecord, Conference


class JournalIsolationTests(TestCase):
    def setUp(self):
        self.j1 = Journal.objects.create(
            title="Arxitektura va Ta'lim",
            slug="arxitektura",
            issn="2181-1230",
            publication_status="published",
            is_active=True
        )
        self.j2 = Journal.objects.create(
            title="Moliya va Bank",
            slug="moliya",
            issn="2181-4567",
            publication_status="published",
            is_active=True
        )
        self.user = User.objects.create_user(
            username="author1", email="author1@example.com", password="password123", role="author"
        )

    def test_different_journals_can_use_identical_issue_numbers(self):
        issue1 = JournalIssue.objects.create(
            journal=self.j1, volume=1, number=1, year=2026, is_published=True
        )
        issue2 = JournalIssue.objects.create(
            journal=self.j2, volume=1, number=1, year=2026, is_published=True
        )
        self.assertEqual(issue1.number, issue2.number)
        self.assertEqual(issue1.year, issue2.year)
        self.assertNotEqual(issue1.journal, issue2.journal)

    def test_duplicate_issue_rejected_in_same_journal(self):
        JournalIssue.objects.create(
            journal=self.j1, volume=1, number=1, year=2026, is_published=True
        )
        dup = JournalIssue(
            journal=self.j1, volume=1, number=1, year=2026, is_published=True
        )
        with self.assertRaises(ValidationError):
            dup.clean()

    def test_editorial_board_isolation(self):
        staff1 = StaffMember.objects.create(
            journal=self.j1, full_name="Prof. Arxitektor", position="editor_in_chief", is_active=True
        )
        staff2 = StaffMember.objects.create(
            journal=self.j2, full_name="Prof. Moliyachi", position="editor_in_chief", is_active=True
        )
        j1_staff = StaffMember.objects.filter(journal=self.j1)
        j2_staff = StaffMember.objects.filter(journal=self.j2)
        self.assertIn(staff1, j1_staff)
        self.assertNotIn(staff2, j1_staff)
        self.assertIn(staff2, j2_staff)
        self.assertNotIn(staff1, j2_staff)


class ArticleManagementAndWorkflowTests(TestCase):
    def setUp(self):
        self.j1 = Journal.objects.create(
            title="Arxitektura va Ta'lim", slug="arxitektura", publication_status="published", is_active=True
        )
        self.j2 = Journal.objects.create(
            title="Moliya va Bank", slug="moliya", publication_status="published", is_active=True
        )
        self.issue1 = JournalIssue.objects.create(
            journal=self.j1, volume=1, number=1, year=2026, is_published=True
        )
        self.issue2 = JournalIssue.objects.create(
            journal=self.j2, volume=1, number=1, year=2026, is_published=True
        )
        self.author1 = User.objects.create_user(
            username="author1", email="author1@example.com", password="password123", role="author"
        )
        self.author2 = User.objects.create_user(
            username="author2", email="author2@example.com", password="password123", role="author"
        )

    def test_cannot_assign_article_to_issue_of_different_journal(self):
        art = Article(
            journal=self.j1,
            author=self.author1,
            issue=self.issue2,  # Belongs to j2, but article is j1!
            title="Bino konstruksiyalari",
            abstract="Tavsif",
            keywords="bino",
            status="accepted"
        )
        with self.assertRaises(ValidationError):
            art.clean()

    def test_cannot_assign_unaccepted_article_to_issue(self):
        art = Article(
            journal=self.j1,
            author=self.author1,
            issue=self.issue1,
            title="Xomaki maqola",
            abstract="Tavsif",
            keywords="xom",
            status="submitted"  # Not accepted!
        )
        with self.assertRaises(ValidationError):
            art.clean()

    def test_rejected_article_cannot_be_assigned_to_issue(self):
        art = Article(
            journal=self.j1,
            author=self.author1,
            issue=self.issue1,
            title="Rad etilgan maqola",
            abstract="Tavsif",
            keywords="rad",
            status="rejected"
        )
        with self.assertRaises(ValidationError):
            art.clean()


class ReviewRecordWithoutAccountsTests(TestCase):
    def setUp(self):
        self.j1 = Journal.objects.create(
            title="Arxitektura va Ta'lim", slug="arxitektura", publication_status="published", is_active=True
        )
        self.author = User.objects.create_user(
            username="author1", email="author1@example.com", password="password123", role="author"
        )
        self.article = Article.objects.create(
            journal=self.j1,
            author=self.author,
            title="Test Ilmiy Maqola",
            abstract="Annotatsiya",
            keywords="kalit",
            status="under_review"
        )

    def test_review_record_creation_without_reviewer_account(self):
        # Admin manually logs the external review
        review = ReviewRecord.objects.create(
            article=self.article,
            reviewer_name="Tashqi Ekspert Dots. Qodirov",
            reviewer_affiliation="SamDAQI",
            status="received",
            decision="accept",
            confidential_comments="Ushbu tadqiqot chop etishga to'liq loyiq."
        )
        self.assertEqual(review.reviewer_name, "Tashqi Ekspert Dots. Qodirov")
        self.assertEqual(review.decision, "accept")
        self.assertEqual(review.article, self.article)
        # Ensure reviewer does not require a User instance FK
        self.assertFalse(hasattr(review, 'user'))


class PublicInterfaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.j1 = Journal.objects.create(
            title="Arxitektura va Ta'lim",
            slug="arxitektura",
            issn="2181-1230",
            short_description="Arxitektura va shaharsozlik",
            research_areas="Arxitektura, Qurilish, Dizayn",
            publication_status="published",
            is_active=True
        )
        self.draft_journal = Journal.objects.create(
            title="Qoralama Jurnal",
            slug="qoralama",
            publication_status="draft",
            is_active=False
        )

    def test_homepage_status_200_and_catalog_filtering(self):
        response = self.client.get(reverse('portal_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Active and published journal should appear
        self.assertIn("Arxitektura", content)
        # Draft journal should NOT appear
        self.assertNotIn("Qoralama Jurnal", content)

    def test_search_by_title_and_issn(self):
        # Search by title
        r_title = self.client.get(reverse('portal_home') + '?q=Arxitektura')
        self.assertEqual(r_title.status_code, 200)
        self.assertIn("Arxitektura", r_title.content.decode('utf-8'))

        # Search by ISSN
        r_issn = self.client.get(reverse('portal_home') + '?q=2181-1230')
        self.assertEqual(r_issn.status_code, 200)
        self.assertIn("Arxitektura", r_issn.content.decode('utf-8'))

        # Search non-existent
        r_empty = self.client.get(reverse('portal_home') + '?q=NonExistentTermXYZ')
        self.assertEqual(r_empty.status_code, 200)
        self.assertIn("Hozircha nashrga joylashtirilgan jurnallar mavjud emas", r_empty.content.decode('utf-8'))

    def test_journal_detail_page_valid_and_invalid_slug(self):
        # Valid slug
        response = self.client.get(reverse('index', kwargs={'journal_slug': 'arxitektura'}))
        self.assertEqual(response.status_code, 200)

        # Resilient alias / slug
        response_alias = self.client.get(reverse('index', kwargs={'journal_slug': 'arxitektura-va-talim'}))
        self.assertEqual(response_alias.status_code, 200)

        # Dynamic creation of new journal
        j_finance = Journal.objects.create(
            title="Moliya va intellektual texnologiyalar",
            slug="moliya-va-intellektual-texnologiyalar",
            publication_status="published",
            is_active=True
        )
        response_finance = self.client.get(reverse('index', kwargs={'journal_slug': 'moliya-va-intellektual-texnologiyalar'}))
        self.assertEqual(response_finance.status_code, 200)

        # Space-separated query resilience
        response_space = self.client.get('/moliya%20va%20intellektual%20texnologiyalar/')
        self.assertEqual(response_space.status_code, 200)

        # Invalid slug -> 404
        response_404 = self.client.get(reverse('index', kwargs={'journal_slug': 'nonexistent-journal-slug-999'}))
        self.assertEqual(response_404.status_code, 404)


class ReviewPermissionTests(TestCase):
    def setUp(self):
        self.journal = Journal.objects.create(
            title="Arxitektura", slug="arxitektura", publication_status="published", is_active=True
        )
        self.author = User.objects.create_user(
            username="author1", email="author1@example.com", password="password123", role="author"
        )
        self.reviewer = User.objects.create_user(
            username="rev1", email="rev1@example.com", password="password123", role="reviewer"
        )
        self.other_reviewer = User.objects.create_user(
            username="rev2", email="rev2@example.com", password="password123", role="reviewer"
        )
        self.editor = User.objects.create_user(
            username="ed1", email="ed1@example.com", password="password123", role="editor"
        )
        self.article = Article.objects.create(
            journal=self.journal, title="Test maqola", author=self.author,
            status="under_review", assigned_reviewer=self.reviewer
        )

    def _publish(self, user):
        self.client.force_login(user)
        self.client.post(reverse('review_article_action', args=[self.article.pk]), {'action': 'reject'})
        self.article.refresh_from_db()
        return self.article.status

    def test_unassigned_reviewer_cannot_change_article(self):
        self.assertEqual(self._publish(self.other_reviewer), 'under_review')

    def test_assigned_reviewer_can_change_article(self):
        self.assertEqual(self._publish(self.reviewer), 'rejected')

    def test_editor_can_change_any_article(self):
        self.assertEqual(self._publish(self.editor), 'rejected')

    def test_reviewer_cannot_assign_reviewers(self):
        self.client.force_login(self.other_reviewer)
        self.client.post(reverse('assign_reviewer_action', args=[self.article.pk]), {'reviewer_id': self.other_reviewer.pk})
        self.article.refresh_from_db()
        self.assertEqual(self.article.assigned_reviewer, self.reviewer)

    def test_editor_can_assign_reviewers(self):
        self.client.force_login(self.editor)
        self.client.post(reverse('assign_reviewer_action', args=[self.article.pk]), {'reviewer_id': self.other_reviewer.pk})
        self.article.refresh_from_db()
        self.assertEqual(self.article.assigned_reviewer, self.other_reviewer)


class SeoTests(TestCase):
    def setUp(self):
        self.journal = Journal.objects.create(
            title="Arxitektura", slug="arxitektura", issn="2181-1230",
            publication_status="published", is_active=True
        )
        author = User.objects.create_user(
            username="author1", email="author1@example.com", password="password123", role="author"
        )
        self.published = Article.objects.create(
            journal=self.journal, title="Chop etilgan maqola", author=author,
            authors="Ali Valiyev | TIFT", abstract="Annotatsiya matni", status="published",
            content="<p>Matn</p>"
        )
        self.draft = Article.objects.create(
            journal=self.journal, title="Qoralama maqola", author=author, status="submitted"
        )

    def test_robots_txt(self):
        r = self.client.get('/robots.txt')
        self.assertEqual(r.status_code, 200)
        self.assertIn('Disallow: /admin/', r.content.decode())
        self.assertIn('Sitemap:', r.content.decode())

    def test_sitemap_lists_only_published(self):
        r = self.client.get('/sitemap.xml')
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertIn(f'/arxitektura/article/{self.published.pk}/', body)
        self.assertNotIn(f'/arxitektura/article/{self.draft.pk}/', body)

    def test_favicon_redirects(self):
        self.assertEqual(self.client.get('/favicon.ico').status_code, 301)

    def test_article_has_scholar_meta(self):
        r = self.client.get(reverse('article_detail', args=['arxitektura', self.published.pk]))
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertIn('name="citation_title" content="Chop etilgan maqola"', body)
        self.assertIn('name="citation_author" content="Ali Valiyev"', body)
        self.assertIn('name="citation_issn" content="2181-1230"', body)

    def test_plain_authors_split_into_separate_tags(self):
        self.published.authors = "Ali Valiyev, Vali Aliyev"
        self.published.save()
        body = self.client.get(reverse('article_detail', args=['arxitektura', self.published.pk])).content.decode()
        self.assertIn('name="citation_author" content="Ali Valiyev"', body)
        self.assertIn('name="citation_author" content="Vali Aliyev"', body)

    def test_https_links_behind_proxy(self):
        body = self.client.get('/robots.txt', HTTP_X_FORWARDED_PROTO='https').content.decode()
        self.assertIn('Sitemap: https://', body)


class JournalThemeTests(TestCase):
    def _journal(self, slug):
        return Journal.objects.create(title=slug, slug=slug, publication_status="published", is_active=True)

    def test_each_journal_gets_own_theme(self):
        for slug, template in [('arxitektura-va-talim', 'themes/arch/index.html'),
                               ('moliya-va-intellektual-texnologiyalar', 'themes/finance/index.html'),
                               ('bugalteriya-hisobi', 'index.html')]:
            self._journal(slug)
            r = self.client.get(reverse('index', args=[slug]))
            self.assertEqual(r.status_code, 200)
            self.assertTemplateUsed(r, template)

    def test_inner_pages_use_theme_header(self):
        self._journal('moliya-va-intellektual-texnologiyalar')
        r = self.client.get(reverse('archive', args=['moliya-va-intellektual-texnologiyalar']))
        self.assertTemplateUsed(r, 'themes/finance/header.html')


class AuthorMatchingTests(TestCase):
    """"Muallif boshqa maqolalari" faqat shu muallifning maqolalarini ko'rsatishi kerak"""
    def _match(self, a, b):
        from journal.views import _author_people, _same_person
        return any(_same_person(x, y) for x in _author_people(a) for y in _author_people(b))

    def test_same_author_different_institution(self):
        self.assertTrue(self._match("Abbos Maxmudov | TIFT", "Abbos Maxmudov | Toshkent davlat universiteti"))

    def test_shared_institution_is_not_a_match(self):
        self.assertFalse(self._match("Abbos Maxmudov | TIFT", "Dilshod Karimov | TIFT"))
        self.assertFalse(self._match("Abbos Maxmudov, TIFT, Toshkent shahri", "Sardor Aliyev, TIFT, Toshkent shahri"))

    def test_initials(self):
        self.assertTrue(self._match("A. Karimov, D. Yusupova", "Akmal Karimov"))
        self.assertTrue(self._match("Karimov A.", "A. Karimov"))
        self.assertFalse(self._match("A. Karimov", "D. Karimov"))

    def test_same_first_name_only_is_not_a_match(self):
        self.assertFalse(self._match("Abbos Maxmudov", "Abbos Rahimov"))


class CertificateTests(TestCase):
    def setUp(self):
        from django.utils import timezone
        self.journal = Journal.objects.create(title="Arxitektura va ta'lim", slug='arxitektura-va-talim', publication_status='published', is_active=True, issn='3162-1554')
        self.article = Article.objects.create(journal=self.journal, title="SUN’IY INTELLEKT ASOSIDA YANGILIKLARNI SARALASH", authors='Abbos Maxmudov | TIFT; Dilnoza Karimova | TIFT', status='published', published_at=timezone.now())

    def test_author_names_exclude_institutions(self):
        from journal.certificate import author_display_names
        self.assertEqual(author_display_names('Abbos Maxmudov | TIFT; Dilnoza Karimova | TIFT'), ['Abbos Maxmudov', 'Dilnoza Karimova'])
        self.assertEqual(author_display_names('A. Karimov, TIFT, Toshkent shahri'), ['A. Karimov'])

    def test_certificate_pdf_for_each_author(self):
        for idx in (0, 1):
            r = self.client.get(reverse('article_certificate', args=[self.journal.slug, self.article.pk]) + f'?author={idx}')
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r['Content-Type'], 'application/pdf')
            self.assertTrue(r.content.startswith(b'%PDF'))

    def test_no_certificate_for_unpublished(self):
        self.article.status = 'submitted'
        self.article.save()
        r = self.client.get(reverse('article_certificate', args=[self.journal.slug, self.article.pk]))
        self.assertEqual(r.status_code, 404)

    def test_article_page_has_no_reader_and_offers_certificate(self):
        body = self.client.get(reverse('article_detail', args=[self.journal.slug, self.article.pk])).content.decode()
        self.assertNotIn('readerSection', body)
        self.assertIn(reverse('article_certificate', args=[self.journal.slug, self.article.pk]), body)


class PdfMetaExtractionTests(TestCase):
    def test_russian_with_second_language_block(self):
        from journal.pdf_meta import extract_from_text
        text = ("ЗАГОЛОВОК\nАннотация: В статье рассматриваются пути повышения эффективности использования бюджетных сред-\n"
                "ств в сфере государственных закупок и предлагаются меры по их совершенствованию.\n"
                "Ключевые слова: бюджет, государственные закупки, тендер.\n\nAnnotatsiya: Maqolada ...\nВведение\n")
        a, k = extract_from_text(text)
        self.assertTrue(a.startswith("В статье рассматриваются"))
        self.assertIn("бюджетных средств", a)
        self.assertEqual(k, "бюджет, государственные закупки, тендер")

    def test_uzbek_heading_on_own_line(self):
        from journal.pdf_meta import extract_from_text
        text = ("ANNOTATSIYA\nMaqolada yangiliklarni avtomatik yig‘ish, filtrlash, klasterlash va Telegram kanalida nashr etish modeli taklif etiladi.\n"
                "Kalit so‘zlar: sun’iy intellekt, yangiliklar\nKIRISH\nMatn")
        a, k = extract_from_text(text)
        self.assertTrue(a.startswith("Maqolada yangiliklarni"))
        self.assertEqual(k, "sun’iy intellekt, yangiliklar")

    def test_nothing_found(self):
        from journal.pdf_meta import extract_from_text
        self.assertEqual(extract_from_text("Oddiy matn, sarlavhalarsiz."), ("", ""))


class TranslateContentCommandTests(TestCase):
    def test_fills_only_missing_or_untranslated_fields(self):
        from unittest import mock
        from django.core.management import call_command
        j = Journal.objects.create(title="Moliya", slug='moliya-x', publication_status='published', is_active=True)
        Journal.objects.filter(pk=j.pk).update(title_uz="Moliya", title_ru="Финансы (ручной)", title_en="",
                                               publication_frequency_uz="Yiliga 4 marta",
                                               publication_frequency_ru="Yiliga 4 marta", publication_frequency_en="Yiliga 4 marta")
        fake = lambda text, lang: f"[{lang}] {text}"
        with mock.patch('journal.management.commands.translate_content.translate_text', side_effect=fake):
            call_command('translate_content', stdout=open('/dev/null', 'w'))
        j.refresh_from_db()
        self.assertEqual(j.title_ru, "Финансы (ручной)")          # qo'lda kiritilgani saqlanadi
        self.assertEqual(j.title_en, "[en] Moliya")
        self.assertEqual(j.publication_frequency_ru, "[ru] Yiliga 4 marta")
        self.assertEqual(j.publication_frequency_en, "[en] Yiliga 4 marta")


class LanguageSwitchTests(TestCase):
    def test_portal_home_fully_switches_language(self):
        Journal.objects.create(title="Arxitektura", slug='arxitektura-va-talim', publication_status='published', is_active=True)
        for lang, expected, absent in (('ru', 'Научные журналы', 'ilmiy jurnallari'), ('en', 'Scientific Journals', 'ilmiy jurnallari')):
            self.client.cookies['django_language'] = lang
            body = self.client.get('/').content.decode()
            self.assertIn(expected, body)
            self.assertNotIn(absent, body)
            self.assertNotIn('ta jurnal · ochiq kirish', body)


class DomainTests(TestCase):
    def test_new_and_old_domains_are_served(self):
        from django.conf import settings
        self.assertEqual(settings.SITE_DOMAIN, 'journal.tift.uz')
        self.assertIn('https://journal.tift.uz', settings.CSRF_TRUSTED_ORIGINS)
        for host in ('journal.tift.uz', 'architect-edu.tift.uz'):
            r = self.client.get('/robots.txt', HTTP_HOST=host)
            self.assertEqual(r.status_code, 200, host)

    def test_old_domain_redirect_is_opt_in(self):
        from django.test import override_settings
        r = self.client.get('/robots.txt', HTTP_HOST='architect-edu.tift.uz')
        self.assertEqual(r.status_code, 200)
        with override_settings(REDIRECT_OLD_DOMAINS=True):
            r = self.client.get('/moliya/?a=1', HTTP_HOST='architect-edu.tift.uz')
            self.assertEqual(r.status_code, 301)
            self.assertEqual(r['Location'], 'https://journal.tift.uz/moliya/?a=1')
            r = self.client.get('/robots.txt', HTTP_HOST='journal.tift.uz')
            self.assertEqual(r.status_code, 200)


class PdfServingTests(TestCase):
    def setUp(self):
        import tempfile, shutil
        from django.core.files.base import ContentFile
        from django.test import override_settings
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.ov = override_settings(MEDIA_ROOT=self.tmp)
        self.ov.enable(); self.addCleanup(self.ov.disable)
        self.j = Journal.objects.create(title='Moliya', slug='moliya-va-intellektual-texnologiyalar', publication_status='published', is_active=True)
        self.issue = JournalIssue.objects.create(journal=self.j, volume=1, number=1, year=2025, is_published=True, status='published')
        self.issue.full_pdf.save('full.pdf', ContentFile(b'%PDF-1.4 full issue ' + b'x' * 2000))
        Article.objects.filter(pk=0).delete()
        self.full = Article.objects.create(journal=self.j, issue=self.issue, title="1-son | 2025 - to'liq shakli", status='published', start_page=1, end_page=1)
        self.art = Article.objects.create(journal=self.j, issue=self.issue, title='Maqola', authors='Ali Valiyev', status='published', start_page=2, end_page=3)
        self.art.pdf_file.save('a.pdf', ContentFile(b'%PDF-1.4 article ' + b'y' * 2000))

    def test_full_issue_entry_serves_issue_pdf(self):
        r = self.client.get(reverse('article_pdf', args=[self.j.slug, self.full.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(b''.join(r.streaming_content).startswith(b'%PDF-1.4 full issue'))

    def test_x_accel_redirect_when_enabled(self):
        from django.test import override_settings
        with override_settings(X_ACCEL_MEDIA=True):
            r = self.client.get(reverse('download_pdf', args=[self.j.slug, self.art.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r['X-Accel-Redirect'].startswith('/media/'))
        self.assertIn('attachment', r['Content-Disposition'])

    def test_page_view_does_not_call_translator(self):
        from unittest import mock
        with mock.patch('journal.signals.translate_text') as tr:
            r = self.client.get(reverse('article_detail', args=[self.j.slug, self.art.pk]))
        self.assertEqual(r.status_code, 200)
        tr.assert_not_called()
        self.art.refresh_from_db()
        self.assertEqual(self.art.views_count, 1)


class WordArticleTests(TestCase):
    def test_word_file_is_served_as_real_pdf(self):
        import io, tempfile, shutil, docx
        from django.core.files.base import ContentFile
        from django.test import override_settings
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        with override_settings(MEDIA_ROOT=tmp):
            j = Journal.objects.create(title='Arxitektura', slug='arxitektura-va-talim', publication_status='published', is_active=True)
            d = docx.Document(); d.add_heading('Sinov maqolasi', 1); d.add_paragraph('Annotatsiya: oʻzbekcha va русский матн.')
            buf = io.BytesIO(); d.save(buf)
            a = Article.objects.create(journal=j, title='Sinov', authors='Ali Valiyev', status='published', start_page=1, end_page=1)
            a.pdf_file.save('sinov.docx', ContentFile(buf.getvalue()))
            for name in ('article_pdf', 'download_pdf'):
                r = self.client.get(reverse(name, args=[j.slug, a.pk]))
                self.assertEqual(r.status_code, 200)
                self.assertEqual(r['Content-Type'], 'application/pdf')
                self.assertTrue(b''.join(r.streaming_content).startswith(b'%PDF'), name)


class IssuePdfTests(TestCase):
    """To'liq son: mundarija va tahririyat Unicode bilan, bet raqamlari to'g'ri."""

    def make_issue(self, out_path=None):
        import tempfile, shutil, fitz
        from unittest import mock
        from django.core.files.base import ContentFile
        from django.test import override_settings
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        ov = override_settings(MEDIA_ROOT=tmp); ov.enable(); self.addCleanup(ov.disable)
        p = mock.patch('journal.signals.translate_text', side_effect=lambda t, *a, **k: t); p.start(); self.addCleanup(p.stop)
        j = Journal.objects.create(title='Moliya va intellektual texnologiyalar', slug='moliya-va-intellektual-texnologiyalar',
                                   issn='3162-1562', publication_status='published', is_active=True)
        issue = JournalIssue.objects.create(journal=j, volume=1, number=1, year=2026, is_published=True, status='published')
        StaffMember.objects.create(journal=j, full_name='Nodirov Azizxon Asrorovich', position='editor_in_chief', workplace='TIFT universiteti Rektori')
        StaffMember.objects.create(journal=j, full_name='Zokirov Sanjar Zohidjon o‘g‘li', position='secretary', workplace='TIFT universiteti')
        for i in range(12):
            StaffMember.objects.create(journal=j, full_name=f'Po‘latov Muhiddin {i}', position='member', academic_degree='i.f.d.',
                                       academic_title='prof.', workplace='Samarqand iqtisodiyot va servis instituti rektori', order=i)
        titles = ['МОНЕТАРНАЯ ПОЛИТИКА И ТРАНСМИССИОННЫЙ МЕХАНИЗМ', 'O‘ZBEK TILIDAGI YOZMA NUTQNI TABIIY TILNI QAYTA ISHLASH ASOSIDA TAHLIL',
                  'Kripto aktivlarni global moliyaviy boshqaruvda funksional tartibga solish va soliq shaffofligi: xalqaro modellar']
        cats = [ArticleCategory.objects.create(journal=j, code='MF.02.00', name='Bank, kredit', order=2),
                ArticleCategory.objects.create(journal=j, code='MF.01.00', name='Moliya, soliq, byudjet', order=1)]
        for n in range(15):
            doc = fitz.open()
            for k in range(3):
                pg = doc.new_page()
                pg.insert_text((72, 100 if n % 2 else 45), f'Article {n} body', fontsize=12)
                pg.insert_text((pg.rect.width / 2, pg.rect.height - 30), str(k + 1), fontsize=10)
            a = Article.objects.create(journal=j, issue=issue, title=titles[n % 3], authors='Абдурахимова Саида, Mamadjanov Farrux G‘ayratovich',
                                       status='published', order_in_issue=n, category=cats[n % 2])
            a.pdf_file.save(f'a{n}.pdf', ContentFile(doc.tobytes()))
        r = self.client.get(reverse('download_issue_pdf', args=[j.slug, issue.pk]))
        self.assertEqual(r.status_code, 200)
        if out_path:
            open(out_path, 'wb').write(r.content)
        return fitz.open(stream=r.content, filetype='pdf'), issue

    def test_toc_unicode_and_page_numbers(self):
        doc, issue = self.make_issue()
        text = '\n'.join(p.get_text() for p in doc)
        self.assertIn('МОНЕТАРНАЯ', text)
        self.assertIn('O‘ZBEK', text)
        self.assertIn('Zokirov Sanjar Zohidjon o‘g‘li', text)
        arts = list(Article.objects.filter(issue=issue).order_by('order_in_issue'))
        first = arts[0]
        page = doc[first.start_page - 1]
        self.assertIn('Article 0 body', page.get_text())
        words = [w[4] for w in page.get_text('words') if w[1] > page.rect.height * 0.88]
        self.assertIn(str(first.start_page), words)
        mid = page.rect.width / 2
        old = [w for w in page.get_text('words') if w[4] == '1' and abs(w[0] - mid) < 5]
        self.assertEqual(old, [])  # maqola faylidagi eski raqam olib tashlangan
        self.assertEqual(arts[-1].end_page, arts[-1].start_page + 2)
        self.assertEqual(len(doc.get_toc()), len(arts) + 3)  # mundarija + 2 yo'nalish

    def test_articles_grouped_by_category_with_sequential_pages(self):
        doc, issue = self.make_issue()
        from journal.views import ordered_issue_articles
        arts = ordered_issue_articles(issue)
        codes = [a.category.code for a in arts]
        self.assertEqual(codes, sorted(codes))  # MF.01 (order=1) avval, keyin MF.02
        for prev, cur in zip(arts, arts[1:]):
            self.assertEqual(cur.start_page, prev.end_page + 1)
        toc = doc.get_toc()
        self.assertEqual([t[1] for t in toc if t[0] == 1][1:], ['Moliya, soliq, byudjet', 'Bank, kredit'])
        for a in arts:
            first = doc[a.start_page - 1].get_text()
            self.assertNotIn(a.category.name, first)
            self.assertIn(f'Article {a.order_in_issue} body', first)
        toc_text = doc[1].get_text()
        self.assertNotIn('Bank, kredit', toc_text)
        r = self.client.get(reverse('issue_detail', args=[issue.journal.slug, issue.pk]))
        self.assertEqual(r.status_code, 200)


class ConferenceTests(TestCase):
    def test_parse_legacy_dates(self):
        import datetime
        from journal.management.commands.import_fintech_conferences import parse_date
        self.assertEqual(parse_date('28.03.2026', 2026), (datetime.date(2026, 3, 28), ''))
        self.assertEqual(parse_date('25-09-2026', 2026), (datetime.date(2026, 9, 25), ''))
        self.assertEqual(parse_date('30.05.2025–31.05.2025', 2025),
                         (datetime.date(2025, 5, 30), '30.05.2025–31.05.2025'))

    def test_page_nav_and_admin(self):
        import datetime
        from unittest import mock
        with mock.patch('journal.signals.translate_text', side_effect=lambda t, *a, **k: t):
            j = Journal.objects.create(title='Moliya', slug='moliya-va-intellektual-texnologiyalar', publication_status='published', is_active=True)
            arch = Journal.objects.create(title='Arxitektura', slug='arxitektura-va-talim', publication_status='published', is_active=True)
            Conference.objects.create(journal=j, title='Yashil iqtisodiyot konferensiyasi', date=datetime.date(2026, 9, 25),
                                      participants='130', organization='TIFT', location='Toshkent', url='https://example.com/c')
            Conference.objects.create(journal=j, title='Eski konferensiya', date=datetime.date(2025, 5, 30), date_text='30.05.2025–31.05.2025')
        r = self.client.get(reverse('conferences', args=[j.slug]))
        self.assertContains(r, 'Yashil iqtisodiyot konferensiyasi')
        self.assertContains(r, '130 ishtirokchi')
        self.assertContains(r, '30.05.2025–31.05.2025')
        html = r.content.decode()
        self.assertLess(html.index('>2026<'), html.index('>2025<'))
        self.assertContains(self.client.get(reverse('index', args=[j.slug])), reverse('conferences', args=[j.slug]))
        self.assertNotContains(self.client.get(reverse('index', args=[arch.slug])), reverse('conferences', args=[arch.slug]))
        admin = User.objects.create_superuser('adm', 'adm@example.com', 'pw')
        self.client.force_login(admin)
        self.assertEqual(self.client.get('/admin/journal/conference/').status_code, 200)
        self.assertEqual(self.client.get('/admin/journal/conference/add/').status_code, 200)
        # sidebar menyusida: umumiy rejimda va jurnal tanlanganda
        self.assertContains(self.client.get('/admin/journal/document/'), 'href="/admin/journal/conference/"')
        r = self.client.get(f'/admin/journal/document/?journal__id__exact={j.pk}')
        self.assertContains(r, f'href="/admin/journal/conference/?journal__id__exact={j.pk}"')

    def test_import_links_existing_instead_of_duplicating(self):
        import datetime
        from io import StringIO
        from unittest import mock
        from django.core.management import call_command
        with mock.patch('journal.signals.translate_text', side_effect=lambda t, *a, **k: t), \
                mock.patch('journal.management.commands.import_fintech_conferences.download', side_effect=OSError('offline')):
            j = Journal.objects.create(title='Moliya', slug='moliya-va-intellektual-texnologiyalar', publication_status='published', is_active=True)
            Conference.objects.create(journal=j, title='XXI asr. Ilm-fan, innovatsiyalar, ta’lim: xorijiy tillarni o‘qitishning dolzarb masalalari',
                                      date=datetime.date(2025, 2, 21), location='Toshkent')
            call_command('import_fintech_conferences', stdout=StringIO())
            call_command('import_fintech_conferences', stdout=StringIO())
        self.assertEqual(Conference.objects.filter(journal=j).count(), 12)
        c = Conference.objects.get(date=datetime.date(2025, 2, 21))
        self.assertEqual(c.legacy_id, 10)
        self.assertEqual(c.location, 'Toshkent')  # admin kiritgani saqlandi
        self.assertEqual(c.participants, '80')
