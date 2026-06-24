from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import JournalIssue, Article, StaffMember
from .forms import ArticleSubmissionForm, CustomUserCreationForm


def index(request):
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
    return render(request, 'article_detail.html', {'article': article})


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
