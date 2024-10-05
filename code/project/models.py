from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Manager for custom user creation
class CustomUserManager(BaseUserManager):
    # Create user with given values
    def create_user(self, username=None, password=None, **extra_fields):
        # Abort when missing username
        if not username:
            raise ValueError("Missing username value")
        # Create model
        user = self.model(
            username     = username,
            # Store passwords in plain version
            password     = password,
            first_name   = extra_fields.get("first_name"),
            last_name    = extra_fields.get("last_name"),
            email        = self.normalize_email(extra_fields.get("email")),
            phone_number = extra_fields.get("phone_number"),
            userrole     = extra_fields.get("userrole")
        )
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
    # Define fields for user
    user_id      = models.AutoField(primary_key=True, db_column="userID")
    first_name   = models.CharField(max_length=255,   db_column="firstName")
    last_name    = models.CharField(max_length=255,   db_column="lastName")
    username     = models.CharField(max_length=255,   db_column="username", unique=True)
    password     = models.CharField(max_length=128,   db_column="userPassword")
    email        = models.CharField(max_length=255,   db_column="email", unique=True)
    phone_number = models.CharField(max_length=9,     db_column="phoneNumber")
    userrole     = models.CharField(max_length=20,    db_column="userRole", choices=[(role, role) for role in user_roles])

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "password",
        "email",
        "phone_number",
        "userrole"
    ]

    class Meta:
        # Specify table for storing users
        db_table = "User"

    def save(self, *args, **kwargs):
        # Avoid passwords hashing when saving into DB
        super().save(*args, **kwargs)

    # Methods for determining role of currently logged user
    def userRole(self):
        return self.userrole
