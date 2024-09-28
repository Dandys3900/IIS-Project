"""
URL configuration for source project.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page + Login
    path('', views.home, name='home'),
    path('logout/', views.client_logout, name='logout')
]
