from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Portal 
    path('', views.portal_home, name='portal_home'),
    
    # Auth & Global User Views
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/password/', views.change_password, name='change_password'),
    path('my-articles/', views.my_articles, name='my_articles'),
    
    # Reviewer Dashboard (Global)
    path('reviewer/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('reviewer/article/<int:pk>/action/', views.review_article_action, name='review_article_action'),
    path('reviewer/article/<int:pk>/assign/', views.assign_reviewer_action, name='assign_reviewer_action'),
    
    # Journal-specific Views
    path('<slug:journal_slug>/', views.index, name='index'),
    path('<slug:journal_slug>/archive/', views.archive, name='archive'),
    path('<slug:journal_slug>/about/', views.about, name='about'),
    path('<slug:journal_slug>/conferences/', views.conferences, name='conferences'),
    path('<slug:journal_slug>/news/', views.news_list, name='news'),
    path('<slug:journal_slug>/news/<int:pk>/', views.news_detail, name='news_detail'),
    path('<slug:journal_slug>/documents/', views.documents, name='documents'),
    path('<slug:journal_slug>/article/<int:pk>/', views.article_detail, name='article_detail'),
    path('<slug:journal_slug>/article/<int:pk>/download/', views.download_pdf, name='download_pdf'),
    path('<slug:journal_slug>/article/<int:pk>/pdf/', views.generate_article_pdf, name='article_pdf'),
    path('<slug:journal_slug>/submit/', views.submit_article, name='submit_article'),
    path('<slug:journal_slug>/issue/<int:issue_pk>/', views.issue_detail, name='issue_detail'),
    path('<slug:journal_slug>/issue/<int:issue_pk>/download/', views.download_issue_pdf, name='download_issue_pdf'),
]
