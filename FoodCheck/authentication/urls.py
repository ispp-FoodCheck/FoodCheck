from django.urls import re_path, include, path 
from . import views
from django.contrib.auth import views as auth_views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.registro, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('terms/', views.terms_view, name='terms'),
    path('gdpr/', views.gdpr_view, name='gdpr'),
]