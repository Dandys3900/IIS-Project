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

# Home view
def home(request):
    # Get search query if any
    search_query = request.GET.get("query")

    if search_query:
        animals = Animal.objects.filter(name__icontains=search_query, is_active=True)
    else:
        animals = Animal.objects.filter(is_active=True).order_by("animal_id")

    # User is trying to upload animal schedule
    if request.method == "POST":
        # TODO: Add form for animal schedule and its handling
        pass
    return render(request, "home.html", {
        "animals" : animals
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

    form = UserInfoForm(user=request.user)
    if request.method == "POST":
        form = UserInfoForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            # Save changes in user profile
            form.save()
            # Re-authenticate user and update session hash to prevent logout
            update_session_auth_hash(request, request.user)
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
        return redirect("createanimal")

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
        return redirect("editanimal", anima_id=animal.animal_id)

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
    # Delete photo
    photo.delete()
    return redirect("editanimal", animal_id=animal_id)

def animals_list(request):
    # Security: only carer or veterinarian can view this
    role_required(request, ["carer", "vet"])

    animals = Animal.objects.all().order_by("animal_id")
    # Render page
    return render(request, "animal_list.html", {
        "animals" : animals
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

    if request.method == "GET":
        # Render page
        return render(request, "animal_detail.html", {
            "animal"         : animal,
            "health_records" : health_records,
            "animal_tasks"   : animal_tasks,
            "form"           : form
        })

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

    form = CreateAnimalTaskForm()

    if request.method == "GET":
        # Render page
        return render(request, "animal_tasks.html", {
            "animal" : animal,
            "tasks"  : animal_tasks,
            "form"   : form
        })

    form = CreateAnimalTaskForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("animalvettasks", animal_id=animal.animal_id)

    vet_task = form.save(commit=False)
    vet_task.animal_id = animal
    vet_task.veterinarian = form.cleaned_data["target_vet"]
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
        return redirect("home")

    form = BookAnimalForm(animal=animal, user=request.user)

    # Get current date
    today = date.today()
    # Get all booking for selected animal (don't take past bookings)
    bookings = Reservation.objects.filter(animal_id=animal, start_time__date__gte=today).order_by("start_time")

    timetable = {}
    for reservation in bookings:
        book_date = str(reservation.start_time.date())
        # Get day name from the reservation
        day_name = reservation.start_time.strftime('%A')
        # Use tuple (date, day_name) as dict key
        key = (book_date, day_name)

        # New date, init whole day for it
        if key not in timetable:
            timetable[key] = [None for _ in range(8, 18)]

        # Add reservation
        reser_time = reservation.start_time.hour - 8
        # Shelter has opening hours from 8am - 5pm every day
        if reser_time in [range(0, 10)]:
            timetable[key][reservation.start_time.hour] = reservation

    if request.method == "GET":
        # Render page
        return render(request, "animal_book.html", {
            "form"     : form,
            "animal"   : animal,
            "timetable": timetable,
            "hours"    : list(range(8, 18))
        })

    if request.user and not request.user.verified: # Unverified volunteer
        messages.warning(request, "To take an animal for a walk, you need to be verified. Contact a carer to be verified.")
        return redirect("home")

    form = BookAnimalForm(data=request.POST, animal=animal, user=request.user)
    if not form.is_valid():
        messages.error(request, "Could not book a walk.")
        return redirect("bookanimal", animal_id)

    # Ensure time is in correct timezone
    start_time = form.cleaned_data["start_time"].astimezone(timezone.utc)
    end_time   = form.cleaned_data["end_time"].astimezone(timezone.utc)

    if form.cleaned_data["date"] == datetime.today().date() and start_time < datetime.now().time().replace(tzinfo=timezone.utc):
        messages.error(request, "Error while booking animal: Cannot book animal in the past time.")
        return redirect("bookanimal", animal_id)
    if start_time > end_time:
        messages.error(request, "Error while booking animal: Cannot book animal for a negative time.")
        return redirect("bookanimal", animal_id)
    if start_time.hour < 8 or start_time.hour > 17:
        messages.error(request, "Error while booking animal: Shelter is open from 8am - 5pm.")
        return redirect("bookanimal", animal_id)

    form.save()
    messages.success(request, "Walk booked.")
    return redirect("home")

def walk_list(request):
    role_required(request, ["carer", "volunteer"])
    walks = Walking.objects.all()
    if request.user.userrole == "volunteer":
        walks = walks.filter(volunteer_id=request.user.user_id)
    return render(request, "walk_list.html", {
        "walks" : walks
    })

def walk_change_confirmation(request, walk_id, desired_confirmation):
    role_required(request, ["carer"])
    if not desired_confirmation in ["pending", "approved", "declined"]:
        messages.error(request, f"Booking confirmation could not be changed to '{desired_confirmation}'. Bad choice.")
        return redirect("walklist")

    try: # Get walk to be edited
        walk = Walking.objects.get(walk_id=walk_id)
    except Exception as e:
        messages.error(request, f"Error while changing booking confirmation: {e}.")
        return redirect("walklist")

    # Forbid changing of already ongoing booking
    if walk.walk_id.start_time < datetime.now().replace(tzinfo=timezone.utc):
        messages.error(request, "Cannot modify an already finished/ongoing walk.")
        return redirect("walklist")

    # Forbid confirming two bookings at the same time
    if desired_confirmation == "approved" and walk.walk_id.has_conflict():
        messages.error(request, "Cannot approve walk. Another booking is in conflict.")
        return redirect("walklist")


    walk.confirmation = desired_confirmation
    walk.save()
    messages.success(request, f"Booking confirmation changed to '{desired_confirmation}'.")
    return redirect("walklist")

def walk_delete(request, walk_id):
    role_required(request, ["volunteer"])

    try: # Get walk to be edited
        walk = Walking.objects.get(walk_id=walk_id)
        messages.success(request, "Walk booking deleted.")
    except Exception as e:
        messages.error(request, f"Error while deleting walk booking: {e}.")

    if walk.walk_id.start_time < datetime.now().replace(tzinfo=timezone.utc):
        messages.error(request, "Cannot cancel an already finished/ongoing walk.")
        return redirect("walklist")

    walk.delete()
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
