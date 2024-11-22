import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from .forms import *
from .models import *
from time import gmtime, strftime
from datetime import datetime, timezone, date

# Define max. size for uploaded image to 2MB
MAX_IMG_SIZE = 2*1024*1024
MIN_HOUR = 8
MAX_HOUR = 18

# Home view
def home(request):
    form = AnimalSearchForm(request.GET)
    animals = Animal.objects.filter(is_active=True).order_by("animal_id")

    if form.is_valid():
        search_query = form.cleaned_data["search_bar"]
        search_specie = form.cleaned_data["specie_choice"]

        if search_query:
            animals = animals.filter(name__icontains=search_query, is_active=True)
        if search_specie:
            animals = animals.filter(species__in=search_specie)

    return render(request, "home.html", {
        "animals" : animals,
        "form" : form
    })

# Perform client login
def client_login(request):
    # If POST request, user tries to log in, otherwise would be GET
    if request.method == "POST":
        # Store given credentials
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate user
        user = authenticate(
            request=request,
            username=username,
            password=password
        )
        # Check if successful
        if user is not None:
            login(request, user)
            # User has default password set, issue warning
            if password == "password1234":
                messages.warning(request, "You have default password set, change it in profile details!")
            messages.success(request, mark_safe(f"Welcome back <strong>{username}</strong>!"))
            # Redirect back to homepage
            return redirect("home")
        messages.error(request, mark_safe(f"Error with Your login <strong>{username}</strong>, please try again..."))
    return render(request, "login.html", {})

# Perform current user logout
def client_logout(request):
    logout(request)
    messages.info(request, "Logout successful, see You soon")
    # Redirect back to homepage
    return redirect("home")

# Register new outside user
def client_register(request):
    form = SignUpForm()
    # User is trying to register
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if handle_registration(request, form, True):
            # Redirect back to homepage
            return redirect("home")
    # Re-render form with eventual errors
    return render(request, "register.html", {
        "form" : form
    })

# Create new user by currently logged user
def client_create_new(request):
    # Security: only admin can view this
    role_required(request, ["admin"])

    form = CreateUserForm()
    # User is trying to register
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if handle_registration(request, form, False):
            # Redirect back to homepage
            return redirect("home")
    # Re-render form with eventual errors
    return render(request, "register.html", {
        "form" : form
    })

def client_edit_select(request):
    # Security: only admin can view this
    role_required(request, ["admin"])

    if request.method == "GET":
        form = EditUserSelectForm()
        # Render form
        return render(request, "edit_user.html", {
            "form" : form
        })

    form = EditUserSelectForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("edituser")

    return redirect("edituser", user_id=form.cleaned_data["user_to_edit"])

def client_edit(request, user_id):
    # Security: only admin can view this
    role_required(request, ["admin"])

    try: # Check user_id validity
        user = CustomUser.objects.get(username=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, f"Error occured while editing a user. Nonexistent user {user_id} selected")
        return redirect("edituser")
    except Exception as e:
        messages.error(request, f"Unexpected exception occured, while editing user: {e}")
        return redirect("edituser")

    if request.method == "GET":
        form = EditUserForm(user=user)
        # Render form
        return render(request, "edit_user.html", {
            "form" : form,
            "username" : user.username
        })

    form = EditUserForm(request.POST, instance=user, user=user)
    if form.is_valid():
        form.save()
        messages.success(request, f"User {user_id} edited")
        return redirect("edituser")

    return render(request, "edit_user.html", {
        "form" : form,
        "username" : user.username
    })

# Deleting user by admin
def client_delete(request):
    # Security: only admin can view this
    role_required(request, ["admin"])

    if request.method == "GET":
        form = DeleteUserForm()
        # Render form
        return render(request, "delete_user.html", {
            "form" : form
        })

    form = DeleteUserForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("deleteuser")

    try:
        user_to_delete_id = form.cleaned_data["user_to_delete"]
        # Try to find and delete requested user in database
        user_to_delete = CustomUser.objects.get(username=user_to_delete_id)
        user_to_delete.delete()
        messages.success(request, f"User {user_to_delete_id} deleted successfully.")

    except CustomUser.DoesNotExist:
        messages.error(request, f"Error occured while deleting user {user_to_delete_id}. User does not exist.")
    except Exception as e:
        messages.error(request, f"Unexpected exception occured, while deleting user: {e}")
    finally:
        return redirect("deleteuser")

# Show details for currently logged in user
def client_details(request):
    # Security: only logged user can view this
    role_required(request)

    userinfo_form = UserInfoForm(instance=request.user)

    if request.method == "POST":
        userinfo_form = UserInfoForm(request.POST, instance=request.user)

        if userinfo_form.is_valid():
            userinfo_form.save()
        else:
            error_messages = [error for errors in userinfo_form.errors.values() for error in errors]
            messages.error(request, " ".join(error_messages))
    # Redirect to page user is currently on
    return redirect(request.META.get("HTTP_REFERER"))

def client_changepwd(request):
    # Security: only logged user can view this
    role_required(request)

    changepwd_form = UserPasswordChangeForm(user=request.user)

    if request.method == "POST":
        changepwd_form = UserPasswordChangeForm(user=request.user, data=request.POST)

        if changepwd_form.is_valid():
            changepwd_form.save()
            # Re-authenticate user and update session hash to prevent logout
            update_session_auth_hash(request, changepwd_form.user)
        else:
            error_messages = [error for errors in changepwd_form.errors.values() for error in errors]
            messages.error(request, " ".join(error_messages))
    # Redirect to page user is currently on
    return redirect(request.META.get("HTTP_REFERER"))

def animal_create(request):
    # Security: only carer can view this
    role_required(request, ["carer"])

    form = CreateAnimalForm()
    formset = AnimalPhotoFormSet()

    if request.method == "GET":
        # Render page
        return render(request, "animal.html", {
            "form"    : form,
            "formset" : formset
        })

    # Animal creation form submitted
    form = CreateAnimalForm(request.POST)
    formset = AnimalPhotoFormSet(request.POST, request.FILES)

    if not form.is_valid() or not formset.is_valid():
        messages.error(request, "Invalid form.")
        # Re-render page
        return render(request, "animal.html", {
            "form"    : form,
            "formset" : formset
        })

    # Check for valid date combination
    if form.cleaned_data["birth_date"]:
        if form.cleaned_data["birth_date"] > form.cleaned_data["arrival_date"]:
            messages.error(request, "Invalid date combination entered.")
            # Reset given dates
            form.data = form.data.copy()
            form.data["birth_date"] = ""
            form.data["arrival_date"] = ""
            # Re-render page
            return render(request, "animal.html", {
                "form"    : form,
                "formset" : formset
            })

    animal = form.save()
    photos = formset.save(commit=False) or []
    # Store photos for animal (if any)
    for photo in photos:
        if photo.image.size > MAX_IMG_SIZE:
            messages.warning(request, "Uploaded image size must be < 2MB")
            break
        # Set photo reference to animal object
        photo.animal_id = animal
        photo.save()
    # Re-show form with uploaded image
    if request.POST.get('action') == 'upload':
        return redirect("editanimal", animal_id=animal.animal_id)
    # Notify user
    messages.success(request, f"Animal {animal.name} added.")
    # Redirect back to homepage
    return redirect("home")

def animal_edit(request, animal_id):
    # Security: only carer can view this
    role_required(request, ["carer"])

    try: # Get animal to be edited
        animal = Animal.objects.get(animal_id=animal_id)
    except Exception as e:
        messages.error(request, f"Error while editing animal: {e}")
        return redirect("home")

    form = EditAnimalForm(animal=animal)
    formset = AnimalPhotoFormSet()

    if request.method == "GET":
        # Render page
        return render(request, "animal.html", {
            "form"    : form,
            "formset" : formset,
            "animal"  : animal
        })

    # Animal edit form submitted
    form = EditAnimalForm(request.POST, instance=animal, animal=animal)
    formset = AnimalPhotoFormSet(request.POST, request.FILES)

    if not form.is_valid() or not formset.is_valid():
        messages.error(request, "Invalid form.")
        # Re-render page
        return render(request, "animal.html", {
            "form"    : form,
            "formset" : formset,
            "animal"  : animal
        })

    # Check for valid date combination
    if form.cleaned_data["birth_date"]:
        if form.cleaned_data["birth_date"] > form.cleaned_data["arrival_date"]:
            messages.error(request, "Invalid date combination entered.")
            # Reset given dates
            form.data = form.data.copy()
            form.data["birth_date"] = ""
            form.data["arrival_date"] = ""
            # Re-render page
            return render(request, "animal.html", {
                "form"    : form,
                "formset" : formset,
                "animal"  : animal
            })

    photos = formset.save(commit=False) or []
    # Store photos for animal (if any)
    for photo in photos:
        if photo.image.size > MAX_IMG_SIZE:
            messages.warning(request, "Uploaded image size must be < 4MB")
            break
        # Set photo reference to animal object
        photo.animal_id = animal
        photo.save()
    form.save()
    # Re-show form with uploaded image
    if request.POST.get('action') == 'upload':
        return redirect("editanimal", animal_id=animal_id)
    # Notify user
    messages.success(request, f"Animal {animal.name} edited.")
    # Redirect back to homepage
    return redirect("home")

def animal_delete(request, animal_id):
    # Security: only carer can view this
    role_required(request, ["carer"])

    try: # Get animal to be deleted
        animal = Animal.objects.get(animal_id=animal_id)
    except Exception as e:
        messages.error(request, f"Error while deleting animal: {e}")
        return redirect("home")

    # Change isActive to False to mark it deleted
    animal.is_active = False
    animal.save()
    # Get all animal photos
    photos = animal.photos.all()
    # Delete these photos as no longer needed
    for photo in photos:
        photo.delete()
    # Notify user
    messages.success(request, f"Animal {animal.name} deleted successfully.")
    # Redirect back to homepage
    return redirect("home")

def image_delete(request, animal_id, image_id):
    # Security: only carer can view this
    role_required(request, ["carer"])

    try:
        photo = AnimalPhoto.objects.get(image_id=image_id)
    except Exception as e:
        messages.error(request, f"Error while deleting image: {e}")
        return redirect("editanimal", animal_id=animal_id)

    # Store animal_id to return back
    animal_id = photo.animal_id.animal_id
    # Remove photo from filesystem first
    os.remove(photo.image.path)
    # Delete photo
    photo.delete()
    return redirect("editanimal", animal_id=animal_id)

def animals_list(request):
    # Security: only carer or veterinarian can view this
    role_required(request, ["carer", "vet"])

    animals = Animal.objects.all().order_by("animal_id")
    # Create list of all animals having todo tasks for logged-in vet to highlight them in table
    todo_animals = []
    for animal in animals:
        tasks_count = request.user.assigned_tasks.filter(is_done=False, animal_id=animal.animal_id).count()
        if request.user.userRole() == "vet" and tasks_count != 0:
            todo_animals.append(animal.animal_id)
    # Render page
    return render(request, "animal_list.html", {
        "animals"     : animals,
        "todo_animals": todo_animals
    })

def animal_medrecord(request, animal_id):
    # Security: only veterinarian can view this
    role_required(request, ["vet"])

    try: # Get animal and its health records
        animal = Animal.objects.get(animal_id=animal_id)
        health_records = animal.med_records.all()
        animal_tasks = animal.animal_tasks.filter(veterinarian=request.user)
    except Exception as e:
        messages.error(request, f"Error while getting animal: {e}")
        return redirect("home")

    form = CreateMedicalRecordForm()
    # Create dictionary of forms for each record to edit
    edit_forms = {record.record_id: EditMedicalRecordForm(instance=record) for record in health_records}

    if request.method == "GET":
        # Render page
        return render(request, "animal_detail.html", {
            "animal"         : animal,
            "health_records" : health_records,
            "animal_tasks"   : animal_tasks,
            "form"           : form,
            "edit_forms"     : edit_forms
        })

    record_id = request.POST.get("record_id")
    if record_id:
        form = edit_forms[int(record_id)]
        form = EditMedicalRecordForm(request.POST, instance=form.instance)
        if form.is_valid():
            form.save()
            return redirect("animalmedrecs", animal_id=animal.animal_id)

    form = CreateMedicalRecordForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("animalmedrecs", animal_id=animal.animal_id)

    health_record = form.save(commit=False)
    health_record.animal_id = animal
    health_record.veterinarian = request.user
    health_record.save()
    # Notify user
    messages.success(request, "Medical record added succesfully")
    return redirect("animalmedrecs", animal_id=animal.animal_id)

def animal_vetrecord(request, animal_id):
    # Security: only carer can view this
    role_required(request, ["carer"])

    try: # Get animal and its health records
        animal = Animal.objects.get(animal_id=animal_id)
        animal_tasks = animal.animal_tasks.all()
    except Exception as e:
        messages.error(request, f"Error while getting animal: {e}")
        return redirect("home")

    timetable = create_timetable(animal, MIN_HOUR, MAX_HOUR)

    animal_task_form = CreateAnimalTaskForm()
    book_animal_form = BookAnimalForm(animal=animal, user=request.user, type="checkup")

    if request.method == "GET":
        # Render page
        return render(request, "animal_tasks.html", {
            "animal" : animal,
            "tasks"  : animal_tasks,
            "animal_task_form" : animal_task_form,
            "book_animal_form" : book_animal_form,
            "timetable": timetable,
        })

    animal_task_form = CreateAnimalTaskForm(request.POST)
    book_animal_form = BookAnimalForm(request.POST, animal=animal, user=request.user, type="checkup")

    if not (animal_task_form.is_valid() and book_animal_form.is_valid()):
        messages.error(request, "Invalid form.")
        return redirect("animalvettasks", animal_id=animal.animal_id)

    if not verify_booking(book_animal_form, request):
        return render(request, "animal_tasks.html", {
            "animal" : animal,
            "tasks"  : animal_tasks,
            "animal_task_form" : animal_task_form,
            "book_animal_form" : book_animal_form,
            "timetable": timetable,
        })

    vet_task = animal_task_form.save(commit=False)
    reservation = book_animal_form.save(commit=False)

    if not reservation:
        messages.error(request, "Conflicting booking found, can't proceed")
        return redirect("animalvettasks", animal_id=animal.animal_id)

    reservation.veterinarian = animal_task_form.cleaned_data["target_vet"]
    vet_task.animal_id = animal
    vet_task.veterinarian = animal_task_form.cleaned_data["target_vet"]
    vet_task.reservation = reservation

    reservation.save()
    vet_task.save()
    # Notify user
    messages.success(request, "Task created succesfully")
    return redirect("animalvettasks", animal_id=animal.animal_id)

def animal_update_task(request, task_id):
    # Security: only veterinarian can view this
    role_required(request, ["vet"])

    try: # Get task
        task = AnimalTask.objects.get(task_id=task_id)
    except Exception as e:
        messages.error(request, f"Error while getting task: {e}")
        return redirect("animalmedrecs", animal_id=task.animal_id.animal_id)

    task.is_done = not task.is_done
    task.save()
    # Redirect back
    return redirect('animalmedrecs', animal_id=task.animal_id.animal_id)

def animal_delete_record(request, record_id):
    # Security: only veterinarian can view this
    role_required(request, ["vet"])

    try: # Get record to be deleted
        record = HealthRecord.objects.get(record_id=record_id)
    except Exception as e:
        messages.error(request, f"Error while deleting health record: {e}")
        return redirect("animalmedrecs", animal_id=record.animal_id.animal_id)

    record.delete()
    # Redirect back
    return redirect('animalmedrecs', animal_id=record.animal_id.animal_id)

def volunteers_list(request):
    # Security: only carer can view this
    role_required(request, ["carer"])

    volunteers = CustomUser.objects.filter(userrole="volunteer", verified=False)
    # Render page
    return render(request, "volunteers_list.html", {
        "volunteers" : volunteers
    })

def verify_volunteer(request, volunteer_id):
    # Security: only carer can view this
    role_required(request, ["carer"])

    try: # Get volunteer (user)
        volunteer = CustomUser.objects.get(user_id=volunteer_id)
    except Exception as e:
        messages.error(request, f"Error while getting volunteer: {e}")
    else:
        volunteer.verified = True
        volunteer.save()
        # Notify user
        messages.success(request, f"Volunteer {volunteer.username} verified succesfully")
    finally:
        # Redirect back
        return redirect("volunteerslist")

def animal_book(request, animal_id):
    try: # Get animal
        animal = Animal.objects.get(animal_id=animal_id)
    except Exception as e:
        messages.error(request, f"Error while booking animal: {e}")
        return redirect("bookanimal", animal_id)

    form = BookAnimalForm(animal=animal, user=request.user)
    timetable = create_timetable(animal, MIN_HOUR, MAX_HOUR)
    if request.method == "GET":
        # Render page
        return render(request, "animal_book.html", {
            "form"     : form,
            "animal"   : animal,
            "timetable": timetable,
        })

    if request.user and not request.user.verified: # Unverified volunteer
        messages.warning(request, "To take an animal for a walk, you need to be verified. Contact a carer to be verified.")
        return redirect("bookanimal", animal_id)

    form = BookAnimalForm(data=request.POST, animal=animal, user=request.user)
    if not form.is_valid():
        messages.error(request, "Could not book a walk.")
        return redirect("bookanimal", animal_id)

    if not verify_booking(form, request):
        return render(request, "animal_book.html", {
            "form"     : form,
            "animal"   : animal,
            "timetable": timetable,
        })

    if form.save():
        messages.success(request, "Walk booked. Please wait for confirmation.")
    else:
        messages.error(request, "Conflicting booking found, can't proceed")
    return redirect("bookanimal", animal_id)

def walk_list(request):
    role_required(request, ["carer", "volunteer"])
    walks = Reservation.objects.all().filter(type="walk", start_time__date__gte=date.today()).order_by("start_time__date")
    if request.user.userrole == "volunteer":
        walks = walks.filter(owner=request.user.user_id)
    return render(request, "walk_list.html", {
        "walks" : walks
    })

def walk_change_confirmation(request, walk_id, desired_confirmation):
    role_required(request, ["carer"])
    if not desired_confirmation in ["pending", "approved", "declined"]:
        messages.error(request, f"Booking confirmation could not be changed to '{desired_confirmation}'. Bad choice.")
        return redirect("walklist")

    try: # Get walk to be edited
        walk = Reservation.objects.get(reservation_id=walk_id)
    except Exception as e:
        messages.error(request, f"Error while changing booking confirmation: {e}.")
        return redirect("walklist")

    # Forbid changing of already ongoing booking
    if walk.start_time < datetime.now().replace(tzinfo=timezone.utc):
        messages.error(request, "Cannot modify an already finished/ongoing walk.")
        return redirect("walklist")

    # Forbid confirming two bookings at the same time
    if desired_confirmation in ["approved", "pending"] and walk.has_conflict():
        messages.error(request, "Cannot process walk. Another booking is in conflict.")
        return redirect("walklist")

    walk.confirmation = desired_confirmation
    walk.save()
    messages.success(request, f"Booking confirmation changed to '{desired_confirmation}'.")
    return redirect("walklist")

def walk_delete(request, walk_id):
    role_required(request, ["volunteer"])
    try: # Get walk to be edited
        walk = Reservation.objects.get(reservation_id=walk_id)
    except Exception as e:
        messages.error(request, f"Error while deleting walk booking: {e}.")
        return redirect("walklist")

    if walk.owner.user_id != request.user.user_id:
        messages.error(request, "Cannot cancel a walk that does not belong to you.")
        return redirect("walklist")

    if walk.start_time < datetime.now().replace(tzinfo=timezone.utc):
        messages.error(request, "Cannot cancel an already finished/ongoing walk.")
        return redirect("walklist")

    walk.delete()
    messages.success(request, "Walk booking deleted.")
    return redirect("walklist")

######################################################
################## HELPER FUNCTIONS ##################

# Helper to ensure only allowed users can access certain views
def role_required(request, allowedRoles=None):
    # No user logged in -> block access
    if not request.user or not request.user.is_authenticated:
        raise PermissionDenied
    # User has different role
    if allowedRoles and request.user.userRole() not in allowedRoles:
        raise PermissionDenied

# Helper function handling registration of new user in multiple contexts
def handle_registration(request, form, doLogin):
    # Check given data validity
    if form.is_valid():
        # Load given credentials
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        extra_fields = {
            "first_name"   : form.cleaned_data.get("first_name"),
            "last_name"    : form.cleaned_data.get("last_name"),
            "email"        : form.cleaned_data.get("email"),
            "phone_number" : form.cleaned_data.get("phone_number"),
            # Default role when none given is "volunteer"
            "userrole"     : form.cleaned_data.get("userrole", "volunteer")
        }
        # Check if user already exists
        user = authenticate(
            request=request,
            username=username,
            password=password,
        )
        # Check user
        if user is None:
            # Create new user
            user = CustomUser.objects.create_user(
                username = username,
                password = password,
                **extra_fields
            )
            # After creation log new user in if requested
            if doLogin:
                login(request, user)
                messages.success(request, mark_safe(f"Welcome onboard <strong>{username}</strong> :-)"))
            else:
                messages.success(request, mark_safe(f"User <strong>{username}</strong> succesfully created :-)"))
            # Registration successful
            return True
        messages.error(request, mark_safe(f"User <strong>{username}</strong> already exists!"))
    return False

def create_timetable(animal, min_hour, max_hour):
    # hours - hour range
    # days - days with reservations
    #   day - formatted day name + date
    #       reservations - array of hours with state for each hour
    timetable = {
        "animal": animal,
        "hours": range(min_hour, max_hour),
        "days": {},
    }

    # Get all booking for selected animal (don't take past and declined bookings)
    reservations = Reservation.objects.filter(
        animal_id=animal,
        start_time__date__gte=date.today()
    ).exclude(confirmation="declined").order_by("start_time")

    for reservation in reservations:
        day_key = f"{str(reservation.start_time.date())} ({reservation.start_time.strftime('%A')})"
        # Make day empty if not exists
        if not day_key in timetable["days"].keys():
            timetable["days"][day_key] = ["none" for _ in range(min_hour, max_hour)]
        # Fill the day hours with reservation times
        for hour in range(min_hour, max_hour):
            if hour >= reservation.start_time.hour and hour < reservation.end_time.hour:
                timetable["days"][day_key][hour-min_hour] = reservation.confirmation if reservation.confirmation else "none"
    return timetable

def verify_booking(form, request):
    if form.cleaned_data["date"] == datetime.today().date() and form.cleaned_data["start_time"].replace(tzinfo=timezone.utc) < datetime.now().time().replace(tzinfo=timezone.utc):
        messages.error(request, "Error while booking animal: Cannot book animal in the past time.")
        # Reset given times and re-render
        form.data = form.data.copy()
        form.data["start_time"] = ""
        return False

    if form.cleaned_data["start_time"].replace(tzinfo=timezone.utc) >= form.cleaned_data["end_time"].replace(tzinfo=timezone.utc):
        messages.error(request, "Error while booking animal: Cannot book animal for a negative or zero time.")
        # Reset given times and re-render
        form.data = form.data.copy()
        form.data["start_time"] = ""
        form.data["end_time"] = ""
        return False

    if form.cleaned_data["start_time"].replace(tzinfo=timezone.utc).hour < MIN_HOUR or form.cleaned_data["start_time"].replace(tzinfo=timezone.utc).hour > MAX_HOUR:
        messages.error(request, f"Error while booking animal: Shelter is open from {MIN_HOUR}:00 - {MAX_HOUR}:00.")
        # Reset given times and re-render
        form.data = form.data.copy()
        form.data["start_time"] = ""
        form.data["end_time"] = ""
        return False

    return True
