from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils.safestring import mark_safe
from .forms import *
from .models import *

# Home view
def home(request):
    # Get only active animals
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
            "form" : form
        })

    form = EditUserForm(request.POST, user=user)
    if not form.is_valid():
        messages.error(request, "Invalid form.")
        return redirect("edituser", user_id=user_id)

    form.save()
    messages.success(request, f"User {user_id} edited")
    return redirect("edituser")

# Deleting user by admin
def client_delete(request):
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
    form = UserInfoForm(user=request.user)
    if request.method == "POST":
        form = UserInfoForm(request.POST, user=request.user)
        if form.is_valid():
            # Save changes in user profile
            form.save()
            # Re-authenticate user and update session hash to prevent logout
            update_session_auth_hash(request, request.user)
    # Redirect to page user is currently on
    return redirect(request.META.get("HTTP_REFERER"))

def animal_create(request):
    form = CreateAnimalForm()
    formset = AnimalPhotoFormSet()
    # Animal creation form submitted
    if request.method == "POST":
        form = CreateAnimalForm(request.POST)
        formset = AnimalPhotoFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            animal = form.save()
            photos = formset.save(commit=False)
            # Store photos for animal (if any)
            if photos:
                for photo in photos:
                    # Set photo reference to animal object
                    photo.animal_id = animal
                    photo.save()
            # Notify user
            messages.success(request, f"Animal {animal.name} added.")
            # Re-show form with uploaded image
            if request.POST.get('action') == 'upload':
                return redirect("editanimal", animal_id=animal.animal_id)
            # Redirect back to homepage
            return redirect("home")
    # Render page
    return render(request, "animal.html", {
        "form"    : form,
        "formset" : formset
    })

def animal_edit(request, animal_id):
    # Get animal to be edited
    animal = Animal.objects.get(animal_id=animal_id)
    form = EditAnimalForm(animal=animal)
    formset = AnimalPhotoFormSet()
    # Animal edit form submitted
    if request.method == "POST":
        form = EditAnimalForm(request.POST, animal=animal)
        formset = AnimalPhotoFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            animal = form.save()
            for subform in formset:
                photo = subform.save(commit=False)
                if photo:
                    photo.animal_id = animal
                    photo.save()
                    # Notify user
                    messages.success(request, f"Animal {animal.name} edited.")
            # Re-show form with uploaded image
            if request.POST.get('action') == 'upload':
                return redirect("editanimal", animal_id=animal.animal_id)
            # Redirect back to homepage
            return redirect("home")
    # Render page
    return render(request, "animal.html", {
        "form"    : form,
        "formset" : formset,
        "animal"  : animal
    })

def animal_delete(request, animal_id):
    # Get animal to be deleted
    animal = Animal.objects.get(animal_id=animal_id)
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

def delete_image(request, image_id):
    try:
        photo = AnimalPhoto.objects.get(image_id=image_id)
    except Exception as e:
        messages.error(request, f"Error while deleting image: {e}")
    else:
        # Store animal_id to return back
        animal_id = photo.animal_id.animal_id
        # Delete photo
        photo.delete()
        return redirect("editanimal", animal_id=animal_id)

######################################################
################## HELPER FUNCTIONS ##################

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
