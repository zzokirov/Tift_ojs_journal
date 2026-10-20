from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from journal.models import User, Journal, JournalIssue, ArticleCategory, Article, StaffMember, ReviewRecord


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
