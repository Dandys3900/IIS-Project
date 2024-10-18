from .forms import UserInfoForm

def userdetails_form(request):
    form = None
    # Create form for logged-in user only
    if request.user.is_authenticated:
        form = UserInfoForm(user=request.user)
    # Return form
    return {
        "userdetails_form": form
    }
