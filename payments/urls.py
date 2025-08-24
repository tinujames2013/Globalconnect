# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Payment dashboard
    path('upgrade/', views.upgrade, name='upgrade'),  # Upgrade plan page
    path('verify/', views.verify, name='verify'),  # Razorpay verification
    path('success/', views.success, name='success'),  # Payment success page
    path('failed/', views.failed, name='failed'),  # Payment failed page
    # Add these if you implement additional pages
    path('transactions/', views.dashboard, name='transactions'),
    path("plans/", views.plans, name="plans"),
    path('settings/', views.dashboard, name='settings'),
    path("transactions/", views.transactions, name="transactions"),
]
