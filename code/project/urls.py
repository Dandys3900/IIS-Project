"""
URL configuration for source project.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    # User login + logout
    path('login/', views.client_login, name='login'),
    path('logout/', views.client_logout, name='logout'),
    # User registering
    path('register/', views.client_register, name='register')
]
