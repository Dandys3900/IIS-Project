from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.safestring import mark_safe
from .forms import SignUpForm, CreateUserForm

# Home view
def home(request):
    # If POST request, user tries to log in, otherwise would be GET
    if request.method == "POST":
        # Store given credentials
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate user
        user = authenticate(
            request,
            username=username,
            password=password
        )
        # Check if successful
        if user is not None:
            login(request, user)
            messages.success(request, mark_safe(f"Welcome back <strong>{username}</strong>!"))
        else:
            messages.error(request, mark_safe(f"Error with Your login <strong>{username}</strong>, please try again..."))
        # Redirect back to homepage
        return redirect("home")
    return render(request, "home.html", {})

# Perform current user logout
def client_logout(request):
    logout(request)
    messages.info(request, "Logout successful, see You soon")
    # Redirect back to homepage
    return redirect("home")

# Register new user
def client_register(request):
    form = SignUpForm()
    # User is trying to register
    if request.method == "POST":
        form = SignUpForm(request.POST)
        # Check given data validity
        if form.is_valid():
            form.save()
            # Load given credentials
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            extra_fields = {
                "first_name"   : form.cleaned_data.get("first_name"),
                "last_name"    : form.cleaned_data.get("last_name"),
                "email"        : form.cleaned_data.get("email"),
                "phone_number" : form.cleaned_data.get("phone_number"),
                "userrole"     : "volunteer" # Default when
            }
            # Authenticate new user
            user = authenticate(
                request,
                username=username,
                password=password,
                **extra_fields
            )
            # Check if successful
            if user is not None:
                login(request, user)
                messages.success(request, mark_safe(f"Welcome onboard <strong>{username}</strong> :-)"))
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
        # Check given data validity
        if form.is_valid():
            form.save()
            # Load given credentials
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            extra_fields = {
                "first_name"   : form.cleaned_data.get("first_name"),
                "last_name"    : form.cleaned_data.get("last_name"),
                "email"        : form.cleaned_data.get("email"),
                "phone_number" : form.cleaned_data.get("phone_number"),
                "userrole"     : form.cleaned_data.get("userrole")
            }
            # Authenticate new user
            user = authenticate(
                request,
                username=username,
                password=password,
                **extra_fields
            )
            # Check if successful
            if user is not None:
                messages.success(request, mark_safe(f"User <strong>{username}</strong> succesfully created :-)"))
            # Redirect back to homepage
            return redirect("home")
    # Re-render form with eventual errors
    return render(request, "register.html", {
        "form" : form
    })

# Show details for currently logged in user
def client_details(request):
    pass
