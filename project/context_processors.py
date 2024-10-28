from .forms import UserInfoForm

def userdetails_form(request):
    form = None
    user = request.user
    pendingTasksCount = 0

    # Create form for logged-in user only
    if user.is_authenticated:
        form = UserInfoForm(user=user)
        if user.userRole() == "vet":
            pendingTasksCount = user.assigned_tasks.filter(is_done=False).count()
    # Return form
    return {
        "userdetails_form" : form,
        "assigned_tasks"   : pendingTasksCount
    }
