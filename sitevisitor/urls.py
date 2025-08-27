# sitevisitor/urls.py
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import JobSitemap, StaticViewSitemap

app_name = 'sitevisitor'

sitemaps = {
    "jobs": JobSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('create-profile/', views.create_profile_view, name='create_profile'),

    # Sitemap
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
