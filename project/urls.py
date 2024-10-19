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
    path('register/', views.client_register, name='register'),
    # Creating new user by logged user
    path('createuser/', views.client_create_new, name='createuser'),
    # Editing user by admin
    path('edituser/', views.client_edit_select, name='edituser'),
    path('edituser/<str:user_id>/', views.client_edit, name='edituser'),
    # Deleting user by admin
    path('deleteuser/', views.client_delete, name='deleteuser'),
    # Logged user details page
    path('userdetails/', views.client_details, name='userdetails'),
    # Creating new animal
    path('createanimal/', views.animal_create, name='createanimal'),
    # Editing animal
    path('editanimal/<int:animal_id>/', views.animal_edit, name='editanimal'),
    # Deleting animal
    path('deleteanimal/<int:animal_id>/', views.animal_delete, name='deleteanimal')
]
