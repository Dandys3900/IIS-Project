from .forms import UserInfoForm
from .models import CustomUser, Walking

def userdetails_form(request):
    form = None
    user = request.user
    pendingTasksCount  = 0
    pending_volunteers = 0
    pending_walks = 0

    # Create form for logged-in user only
    if user and user.is_authenticated:
        form = UserInfoForm(user=user)
        if user.userRole() == "vet":
            pendingTasksCount = user.assigned_tasks.filter(is_done=False).count()
        elif user.userRole() == "carer":
            pending_volunteers = CustomUser.objects.filter(userrole="volunteer", verified=False).count()
            pending_walks = Walking.objects.filter(confirmation="pending").count()
    # Return form
    return {
        "userdetails_form"   : form,
        "assigned_tasks"     : pendingTasksCount,
        "pending_volunteers" : pending_volunteers,
        "pending_walks"      : pending_walks,
    }
