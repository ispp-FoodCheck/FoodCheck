"""FoodCheck URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('home', views.index, name='index'),
    path('shopping_list/', views.shopping_list, name='shopping_list'),
    path('product/<int:id_producto>/details', views.product_details, name='product_details'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('unlock_recipes/', views.unlock_recipes, name='unlock_recipes'),
    path('recipes/', views.recipes_list, name='recipes_list'),
    path('recipe/<int:id_receta>/details', views.recipe_details, name='recipe_details'),
    path('recipes/new', views.new_recipes, name='new_recipes'),
    path('product/<int:id_producto>/add', views.add_product, name='add_product'),
    path('product/<int:id_producto>/remove', views.remove_product, name='remove_product'),    
    path('', include('authentication.urls')),
]