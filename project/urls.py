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
    path('deleteanimal/<int:animal_id>/', views.animal_delete, name='deleteanimal'),
    # Deleting animal image
    path('deleteimage/<int:animal_id>/<int:image_id>/', views.image_delete, name='deleteimage'),
    # Getting list of animals
    path('animalslist/', views.animals_list, name='animalslist'),
    # Getting medical details of animal
    path('animalmedrecs/<int:animal_id>', views.animal_medrecord, name='animalmedrecs'),
    # Getting details of tasks for animal
    path('animalvettasks/<int:animal_id>', views.animal_vetrecord, name='animalvettasks'),
    # Setting task to done
    path('updatetaskstatus/<int:task_id>', views.animal_update_task, name='updatetaskstatus'),
    # Getting list of yet not verified volunteers
    path('volunteerslist/', views.volunteers_list, name='volunteerslist'),
    # Verifying selected volunteer
    path('volunteerverify/<int:volunteer_id>', views.verify_volunteer, name='volunteerverify'),
    # Book animal for walk
    path('bookanimal/<int:animal_id>/', views.animal_book, name='bookanimal'),
	# Manage walk bookings
	path('walklist/', views.walk_list, name='walklist'),
	# Change booking confirmation
	path('walklist/<int:walk_id>/<str:desired_confirmation>/', views.walk_change_confirmation, name='walk_change_confirmation'),
    # Delete booking confirmation
	path('walk_delete/<int:walk_id>', views.walk_delete, name='walk_delete'),
]
