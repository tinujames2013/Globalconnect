# sitevisitor/urls.py
from django.urls import path
from . import views

app_name = 'sitevisitor'  # ← This registers the namespace

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('create-profile/', views.create_profile_view, name='create_profile'),
]
