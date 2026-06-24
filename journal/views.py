from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JournalIssue, Article, StaffMember, SiteVisit
from .forms import ArticleSubmissionForm, CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm


def index(request):
    # Login qilgan user bosh sahifaga kelsa — hisobiga yo'naltir
    if request.user.is_authenticated:
        return redirect('my_articles')

    # Tashrif buyuruvchilarni sanash
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1'))
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        from datetime import date
        SiteVisit.objects.get_or_create(date=date.today(), ip_address=ip)
        total_visitors = SiteVisit.objects.values('ip_address').distinct().count()
        today_visitors = SiteVisit.objects.filter(date=date.today()).count()
    except Exception:
        total_visitors = 0
        today_visitors = 0

    query = request.GET.get('q')
    recent_articles = Article.objects.filter(status='published').order_by('-created_at')
    if query:
        recent_articles = recent_articles.filter(
            Q(title__icontains=query) |
            Q(abstract__icontains=query) |
            Q(keywords__icontains=query)
        )
    recent_articles = recent_articles[:10]
    issues = JournalIssue.objects.all().order_by('-year', '-number')
    return render(request, 'index.html', {
        'recent_articles': recent_articles,
        'issues': issues,
        'query': query,
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
    })


def archive(request):
    issues = JournalIssue.objects.all().order_by('-year', '-number')
    return render(request, 'archive.html', {'issues': issues})


def about(request):
    staff = StaffMember.objects.filter(is_active=True).order_by('order', 'full_name')
    areas = [
        "Arxitektura nazariyasi", "Binolar konstruksiyasi",
        "Shaharsozlik va landshaft", "Geodeziya va kartografiya",
        "Ta'lim metodikasi", "Raqamli texnologiyalar",
        "Sun'iy idrok", "Kadastr va er resurslari",
    ]
    return render(request, 'about.html', {'staff': staff, 'areas': areas})


def issue_detail(request, issue_pk):
    issue = get_object_or_404(JournalIssue, pk=issue_pk)
    articles = Article.objects.filter(issue=issue, status='published')
    return render(request, 'journal/issue_detail.html', {
        'issue': issue,
        'articles': articles,
    })


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if not request.session.get(f'viewed_article_{pk}'):
        article.views_count += 1
        article.save()
        request.session[f'viewed_article_{pk}'] = True

    # Shu muallifning boshqa nashr etilgan maqolalari
    author_articles = Article.objects.filter(
        author=article.author,
        status='published'
    ).exclude(pk=pk).order_by('-created_at')[:5]

    return render(request, 'article_detail.html', {
        'article': article,
        'author_articles': author_articles,
    })


def download_pdf(request, pk):
    """PDF yuklab olish — downloads_count ni oshiradi"""
    import urllib.request
    from django.http import HttpResponse, Http404

    article = get_object_or_404(Article, pk=pk, status='published')

    if not article.pdf_file:
        raise Http404

    # Yuklab olishlar sonini oshir
    Article.objects.filter(pk=pk).update(
        downloads_count=article.downloads_count + 1
    )

    # Cloudinary yoki lokal — ikkalasini ham qo'llab-quvvatlaydi
    try:
        # Lokal fayl
        import os
        file_path = article.pdf_file.path
        if os.path.exists(file_path):
            from django.http import FileResponse
            filename = f"{article.title[:50]}.pdf".replace(' ', '_')
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except (NotImplementedError, ValueError, AttributeError):
        pass

    # Cloudinary URL orqali
    import urllib.request
    from django.http import HttpResponse
    url = article.pdf_file.url
    filename = f"{article.title[:50]}.pdf".replace(' ', '_')
    with urllib.request.urlopen(url) as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my_articles')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def submit_article(request):
    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = 'submitted'
            article.save()
            return redirect('my_articles')
    else:
        form = ArticleSubmissionForm()
    return render(request, 'submit_article.html', {'form': form})


@login_required
def my_articles(request):
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    status_counts = {
        'submitted':    articles.filter(status='submitted').count(),
        'under_review': articles.filter(status='under_review').count(),
        'accepted':     articles.filter(status='accepted').count(),
        'published':    articles.filter(status='published').count(),
        'rejected':     articles.filter(status='rejected').count(),
    }
    return render(request, 'my_articles.html', {
        'articles': articles,
        'status_counts': status_counts,
    })


@login_required
def profile(request):
    """Profil ko'rish + ma'lumotlarni yangilash"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('profile')
        else:
            messages.error(request, 'Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    status_counts = {
        'submitted':    articles.filter(status='submitted').count(),
        'under_review': articles.filter(status='under_review').count(),
        'accepted':     articles.filter(status='accepted').count(),
        'published':    articles.filter(status='published').count(),
        'rejected':     articles.filter(status='rejected').count(),
    }
    return render(request, 'profile.html', {
        'form': form,
        'articles': articles,
        'status_counts': status_counts,
    })


@login_required
def change_password(request):
    """Parol o'zgartirish"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi!')
            return redirect('profile')
        else:
            messages.error(request, 'Xatolik yuz berdi.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
