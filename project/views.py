from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils.safestring import mark_safe
from .forms import SignUpForm, CreateUserForm, UploadImageForm
from .models import AnimalPhoto

# Home view
def home(request):
    form = UploadImageForm()
    pictures = AnimalPhoto.objects.all().order_by('animal_id')
    # User is trying to upload (animal) image
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract image and cardID to check if already has image
            image    = form.cleaned_data["image"]
            animalID = form.cleaned_data["card_id"]
            # Check if that image already exists
            curImage = AnimalPhoto.objects.filter(animal_id=animalID).first()
            if curImage:
                # Override it
                curImage.image = image
                curImage.save()
            else:
                # Save new image
                form.save()
            messages.success(request, mark_safe("Upload of Your image was succesful"))
    return render(request, 'home.html', {
        "form"   : form,
        "images" : pictures
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

# Show details for currently logged in user
def client_details(request):
    pass

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
            # Default role when none given is 'volunteer'
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
            user = get_user_model().objects.create_user(
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
