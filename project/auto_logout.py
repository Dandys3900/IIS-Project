import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class SessionAutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Get current time
        current_time = datetime.datetime.now()
        # Load last user activity time
        if last_activity := request.session.get("last_activity"):
            # Convert value to time object
            last_activity = datetime.datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")
            # If delta of times is higher than given threholds, perform logout
            if (current_time - last_activity).seconds > 300: # 5 mins
                logout(request)
                # Notify user
                messages.warning(request, "For Your inactivity, we logged You out.")
                # Redirect to login page so user can login again
                return redirect("login")
        # Update user's last activity time
        request.session["last_activity"] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        return self.get_response(request)
