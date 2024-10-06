from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import CustomUser

# Custom backend class for performing user authentication
class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Get custom user
            userModel = get_user_model()
            # Try to find requested user in database
            foundUser = userModel.objects.get(username=username)
            # Check if passwords matches
            if foundUser.password == password:
                return foundUser
        except CustomUser.DoesNotExist:
            # Create new user
            return CustomUser.objects.create_user(
                username = username,
                password = password,
                **kwargs
            )
        except Exception as e:
            print(f"auth: {e}")
            return None

    def get_user(self, user_id):
        # Get custom user
        userModel = get_user_model()
        try:
            return userModel.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
