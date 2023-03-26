from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
   path('recommendations/', views.recommendations, name='recommendations'),
]