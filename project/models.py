from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.db.models import Max, Min
from copy import deepcopy

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
            first_name   = extra_fields.get("first_name"),
            last_name    = extra_fields.get("last_name"),
            email        = self.normalize_email(extra_fields.get("email")),
            phone_number = extra_fields.get("phone_number"),
            userrole     = extra_fields.get("userrole")
        )
        # Set user's password
        user.set_password(password)
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
    phone_number = models.CharField(max_length=13,    db_column="phoneNumber")
    userrole     = models.CharField(max_length=20,    db_column="userRole")
    verified     = models.BooleanField(default=False, db_column="verified")

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

    # Method for determining role of currently logged user
    def userRole(self):
        return self.userrole

    # Model's username getter
    def userName(self):
        return self.username

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

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
    image_id  = models.AutoField(primary_key=True, db_column="photoID")
    animal_id = models.ForeignKey(Animal, related_name="photos", on_delete=models.CASCADE, db_column="animalID")
    # Store image in MEDIA_ROOT folder
    image = models.ImageField(db_column="imagePath")

    class Meta:
        # Specify table for storing images
        db_table = "AnimalPhoto"

# Model for animal medical record
class HealthRecord(models.Model):
    record_id    = models.AutoField(primary_key=True, db_column="recordID")
    name         = models.CharField(max_length=255, db_column="name")
    detail       = models.TextField(db_column="detail")
    animal_id    = models.ForeignKey(Animal, related_name="med_records", on_delete=models.CASCADE, db_column="animalID")
    veterinarian = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL, db_column="veterinarianID")

    class Meta:
        # Specify table for storing animal medical records
        db_table = "HealthRecord"

class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True, db_column="reservationID")
    start_time = models.DateTimeField(db_column="start")
    end_time = models.DateTimeField(db_column="end")
    type = models.CharField(max_length=16, db_column="type")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, db_column="animalID")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column="ownerID")
    confirmation = models.CharField(max_length=16, db_column="confirmation")

    class Meta:
        db_table = "Reservation"

    def has_conflict(self, reservations_with_confirmation=["approved"]):
        return Reservation.objects.filter(
            animal_id = self.animal_id,      # Only consider reservations for the same animal
            start_time__lt = self.end_time,  # Check overlap: starts before this ends
            end_time__gt = self.start_time,  # Check overlap: ends after this starts
            confirmation__in = reservations_with_confirmation,
        ).exclude(reservation_id=self.reservation_id).exists()

    def is_fully_contained(self, reservations_with_confirmation=["available"]):
        return Reservation.objects.filter(
            animal_id = self.animal_id, # Only consider reservations for the same animal
            start_time__lte = self.start_time, # Existing starts before or at the same time as this
            end_time__gte = self.end_time, # Existing ends after or at the same time as this
            confirmation__in = reservations_with_confirmation # For some reason, this cannot be a tuple
        ).exclude(reservation_id=self.reservation_id).exists()

    def get_containing_reservation(self, reservations_with_confirmation=["available"]):
        return Reservation.objects.filter(
            animal_id = self.animal_id,  # Only consider reservations for the same animal
            start_time__lte = self.start_time, # Existing starts before or at the same time as this
            end_time__gte = self.end_time, # Existing ends after or at the same time as this
            confirmation__in = reservations_with_confirmation # For some reason, this cannot be a tuple
        ).exclude(reservation_id=self.reservation_id).first()  # Return the first matching reservation

    def get_combineable_reservations(self, reservations_with_confirmation=["available"]):
        return Reservation.objects.filter(
            animal_id = self.animal_id,
            confirmation__in = reservations_with_confirmation,
        ).filter(
            Q(start_time__lte = self.start_time, end_time__gte=self.start_time) | # Overlaps from the left
            Q(start_time__lte = self.end_time, end_time__gte=self.end_time) | # Overlaps from the right
            Q(start_time__gte = self.start_time, end_time__lte=self.end_time) # Fully contained
        ) # Do not exclude self - it itself has to be combined

    def combine_neighboring_reservations(self):
        combineable_reservations = self.get_combineable_reservations([self.confirmation])
        if combineable_reservations.count():
            # Find the maximum and minimum time
            result = combineable_reservations.aggregate(
                min_time=Min("start_time"),
                max_time=Max("end_time"),
            )
            # In case this reservation is not saved yet
            self.start_time = result['min_time'] if self.start_time > result['min_time'] else self.start_time
            self.end_time = result['max_time'] if self.end_time < result['max_time'] else self.end_time
        # Delete all rows from the query except this combined reservation
        combineable_reservations.exclude(reservation_id=self.reservation_id).delete()

    def split_by_reservation(self, reservation):
        # Create duplicates before deleting the original reservation to be modified later.
        # If the original reservation is not deleted beforehand, it would be automatically merged
        new_reservation_left = deepcopy(self)
        new_reservation_right = deepcopy(self)
        # Delete this original availability that is replaced with up to two new ones
        self.delete()
        # Modify and save the duplicates
        if new_reservation_left.start_time < reservation.start_time: # Before walk - left
            new_reservation_left.end_time = reservation.start_time
            new_reservation_left.save()
        if new_reservation_right.end_time > reservation.end_time: # After walk - right
            new_reservation_right.start_time = reservation.end_time
            new_reservation_right.save()

    # Call this before calling save() to retreive the error
    def can_be_saved(self):
        if self.type == "walk" and self.confirmation == "pending" and self.pk == None: # Allow walks to be created only inside availability reservations - any modification after is allowed
            if not self.is_fully_contained(["available"]):
                return (False, "Could not create walk reservation because it is not inside a available walk timeframe.")
        elif self.type == "availability": # Disallow creation of availability reservations that conflict with approved (checkup/walk)
            if self.has_conflict(["approved"]):
                return (False, "Could not create walk availability reservation due to conflicting schedules.")
        elif self.type == "checkup": # Allow checkup only in completely free time
            if self.has_conflict(["approved", "available", "pending"]):
                return (False, "Could not create checkup reservation due to conflicting schedules.")
        return (True, "") # ok, no error

    def save(self, *args, **kwargs):
        can_be_saved, _ = self.can_be_saved()
        if not can_be_saved:
            return None

        if self.type == "availability":
            self.combine_neighboring_reservations()
        elif self.type == "walk":
            if self.confirmation == "pending": # Split the availability
                containing_availability = self.get_containing_reservation(["available"])
                if containing_availability:
                    containing_availability.split_by_reservation(self)
            elif self.confirmation == "declined": # Give the availability back
                replacement_reservation = deepcopy(self)
                replacement_reservation.type = "availability"
                replacement_reservation.confirmation = "available"
                if "decliner" in kwargs:
                    replacement_reservation.owner = kwargs.pop("decliner")

                replacement_reservation.save()


        return super(Reservation, self).save(*args, **kwargs)

class AnimalTask(models.Model):
    task_id      = models.AutoField(primary_key=True, db_column="taskID")
    detail       = models.TextField(db_column="detail")
    is_done      = models.BooleanField(default=False, db_column="isDone")
    animal_id    = models.ForeignKey(Animal, related_name="animal_tasks", on_delete=models.CASCADE, db_column="animalID")
    veterinarian = models.ForeignKey(CustomUser, related_name="assigned_tasks", null=True, on_delete=models.SET_NULL, db_column="veterinarianID")
    reservation  = models.ForeignKey(Reservation, null=True, blank=True, on_delete=models.SET_NULL, db_column="reservationID")

    class Meta:
        # Specify table for storing animal task for veterinarians
        db_table = "Task"
