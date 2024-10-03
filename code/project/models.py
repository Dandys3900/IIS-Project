from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Manager for custom user creation
class CustomUserManager(BaseUserManager):
    # Create user with given values
    def create_user(self, username=None, password=None, role=None, **extra_fields):
        # Abort when missing username
        if not username:
            raise ValueError("Missing username value")
        # Create mode
        user = self.model(
            username = username,
            role     = role,
            **extra_fields
        )
        user.set_password(password)
        # Save user into database
        user.save(using=self._db)
        return user

# Custom user class
class CustomUser(AbstractBaseUser):
    # Specify roles for user
    user_roles = (
        "admin",     # Administrator
        "carer",     # Pecovatel
        "vet",       # Veterinar
        "volunteer"  # Dobrovolnik
        # Neregistrovany uzivatel je else case
    )

    username = models.CharField(
        max_length     = 150,
        unique         = True,
        error_messages = {
            "unique": "User with that username already exists."
        },
    )
    userrole = models.CharField(max_length=20, choices=[(role, role) for role in user_roles])
    objects = CustomUserManager()

    # Methods for determining role of currently logged user
    def userRole(self):
        return self.userrole
