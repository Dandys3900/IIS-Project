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
    # Define fields for user
    last_login   = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    user_id      = models.AutoField(primary_key=True, db_column="userID")
    first_name   = models.CharField(max_length=255,   db_column="firstName")
    last_name    = models.CharField(max_length=255,   db_column="lastName")
    username     = models.CharField(max_length=255,   db_column="username", unique=True)
    password     = models.CharField(max_length=128,   db_column="userPassword")
    email        = models.CharField(max_length=255,   db_column="email", unique=True)
    phone_number = models.CharField(max_length=9,     db_column="phoneNumber")
    userrole     = models.CharField(max_length=20,    db_column="userRole")

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

    # Method for determining role of currently logged user
    def userRole(self):
        return self.userrole

    # Model's username getter
    def userName(self):
        return self.username

class Animal(models.Model):
    # Define fields for animal
    animal_id    = models.AutoField(primary_key=True,      db_column="animalID")
    species      = models.CharField(max_length=255,        db_column="species")
    name         = models.CharField(max_length=255,        db_column="name")
    gender       = models.SmallIntegerField(               db_column="gender")
    birth_date   = models.DateField(null=True, blank=True, db_column="birthDate")
    arrival_date = models.DateField(                       db_column="arrivalDate")
    is_active    = models.BooleanField(default=True,       db_column="isActive")
    breed        = models.CharField(max_length=255,        db_column="breed")
    description  = models.TextField(                       db_column="description")

    class Meta:
        # Specify table for storing animals
        db_table = "Animal"

# Model for animal photos
class AnimalPhoto(models.Model):
    image_id  = models.AutoField(primary_key=True,                  db_column="photoID")
    animal_id = models.ForeignKey(Animal, on_delete=models.CASCADE, db_column="animalID")
    # Store image in MEDIA_ROOT folder
    image = models.ImageField(db_column="imagePath")

    class Meta:
        # Specify table for storing images
        db_table = "AnimalPhoto"
