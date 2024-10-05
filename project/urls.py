"""
URL configuration for source project.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page + Login
    path('', views.home, name='home'),
    path('logout/', views.client_logout, name='logout'),
    # User registering
    path('register/', views.client_register, name='register'),
    # Creating new user by logged user
    path('createuser/', views.client_create_new, name='createuser'),
    # Logged user details page
    path('userdetails/', views.client_details, name='userdetails'),
]
