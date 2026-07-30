from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from journal.models import Article, JournalIssue
from datetime import timedelta
import json

register = template.Library()
User = get_user_model()

@register.simple_tag
def get_dashboard_stats():
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Counts
    total_articles = Article.objects.count()
    new_articles = Article.objects.filter(status='submitted').count()
    in_review = Article.objects.filter(status__in=['initial_review', 'under_review']).count()
    returned = Article.objects.filter(status='returned').count()
    accepted = Article.objects.filter(status__in=['accepted', 'ready_to_publish']).count()
    rejected = Article.objects.filter(status='rejected').count()
    published = Article.objects.filter(status='published').count()
    users = User.objects.filter(is_active=True).count()

    return {
        'total_articles': total_articles,
        'new_articles': new_articles,
        'in_review': in_review,
        'returned': returned,
        'accepted': accepted,
        'rejected': rejected,
        'published': published,
        'active_users': users,
    }

@register.simple_tag
def get_latest_articles(limit=6):
    return Article.objects.select_related('author', 'category').order_by('-created_at')[:limit]

@register.simple_tag
def get_recent_activity(limit=5):
    return LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:limit]

@register.simple_tag
def get_upcoming_issue():
    return JournalIssue.objects.filter(is_published=False).order_by('year', 'volume', 'number').first()

@register.simple_tag
def get_chart_data():
    # Status taqsimoti (Donut chart)
    status_counts = Article.objects.values('status').annotate(count=Count('id'))
    status_map = {
        'submitted': 'Yangi',
        'initial_review': 'Tekshiruv',
        'under_review': 'Taqriz',
        'returned': 'Qaytarilgan',
        'accepted': 'Qabul',
        'rejected': 'Rad etilgan',
        'ready_to_publish': 'Nashrga',
        'published': 'Nashr etilgan'
    }
    status_labels = []
    status_data = []
    for sc in status_counts:
        status_labels.append(status_map.get(sc['status'], sc['status']))
        status_data.append(sc['count'])

    # Oylik dinamika (Line chart) - last 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = Article.objects.filter(created_at__gte=six_months_ago)\
        .annotate(month=TruncMonth('created_at'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .order_by('month')
    
    monthly_labels = [m['month'].strftime('%b %Y') for m in monthly_data] if monthly_data else []
    monthly_counts = [m['count'] for m in monthly_data] if monthly_data else []

    # Yo'nalishlar bo'yicha (Bar chart)
    category_data = Article.objects.exclude(category__isnull=True)\
        .values('category__name')\
        .annotate(count=Count('id'))\
        .order_by('-count')[:5]
    
    cat_labels = [c['category__name'] for c in category_data] if category_data else []
    cat_counts = [c['count'] for c in category_data] if category_data else []

    return json.dumps({
        'status': {'labels': status_labels, 'data': status_data},
        'monthly': {'labels': monthly_labels, 'data': monthly_counts},
        'category': {'labels': cat_labels, 'data': cat_counts},
    })
