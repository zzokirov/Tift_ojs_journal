from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('archive/', views.archive, name='archive'),
    path('about/', views.about, name='about'),
    path('conferences/', views.conferences, name='conferences'),
    path('news/', views.news_list, name='news'),
    path('documents/', views.documents, name='documents'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/<int:pk>/download/', views.download_pdf, name='download_pdf'),
    path('article/<int:pk>/pdf/', views.generate_article_pdf, name='article_pdf'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('submit/', views.submit_article, name='submit_article'),
    path('my-articles/', views.my_articles, name='my_articles'),
    path('profile/', views.profile, name='profile'),
    path('profile/password/', views.change_password, name='change_password'),
    path('issue/<int:issue_pk>/', views.issue_detail, name='issue_detail'),
]
