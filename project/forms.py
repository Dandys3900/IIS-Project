from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from django.forms import inlineformset_factory
from django import forms
from .models import *
from datetime import datetime, timezone, date

ROLE_CHOICES = [
    ("admin", "Administrator"),
    ("carer", "Caretaker"),
    ("vet"  , "Veterinarian"),
    ("volunteer", "Volunteer")
]

GENDER_CHOICES = [
    (0, "Male"),
    (1, "Female")
]

SELECT_FORM_STYLE = {
    "class": "form-control",
    "style": "width: 50%;"
}

phone_regex = RegexValidator(
    regex=r"^\+420[0-9]{9}$",
    message="Enter phone number in correct format +420XXXYYYZZZ."
)

email_regex = RegexValidator(
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    message="Email should have format: account@server.domain"
)

def reorderChoices(role_choices, first_choice):
    # Separate the first choice tuple from the rest
    first_choice = [role_choice for role_choice in role_choices if role_choice[0] == first_choice]
    # Get the unused rest
    remaining = [role_choice for role_choice in role_choices if role_choice[0] != first_choice]
    # Return the reordered list
    return first_choice + remaining

# Function for constructing textInput with given args
def getTextWidget(elementName, placeholderText):
    return forms.TextInput(attrs={
        "class"       : "form-control",
        "name"        : elementName,
        "placeholder" : placeholderText
    })

# Function for constructing charFields
def createField(max_length, elementName, placeholderText, required=True, validators=[]):
    return forms.CharField(
        required   = required,
        max_length = max_length,
        label      = "",
        validators = validators,
        widget     = getTextWidget(elementName, placeholderText)
    )

# Singup form class
class SignUpForm(UserCreationForm):
    # Get new user information
    first_name   = createField(255, "first_name", "Enter firstname")
    last_name    = createField(255, "last_name", "Enter lastname")
    email        = createField(255, "email", "Enter email (account@server.domain)", validators=[email_regex])
    phone_number = createField(13, "phone_number", "Enter phone number (+420XXXYYYZZZ)", validators=[phone_regex])

    # New user model class
    class Meta:
        model = CustomUser
        # List user attributes
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2"
        )

    # Setup rest of form fields (username, password1+2)
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Setup pre-defined fields of UserCreationForm class
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Enter username"
        self.fields["username"].label     = ""

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Enter password"
        self.fields["password1"].label     = ""

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Enter password again"
        self.fields["password2"].label     = ""
        self.fields["password2"].help_text = ""

class CreateUserForm(SignUpForm):
    # Add dropdown menu to select role for new user
    userrole = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Select role for new user", widget=forms.Select(attrs=SELECT_FORM_STYLE))

    class Meta(SignUpForm.Meta):
        # Inherit fields from SignUpForm and add own role dropdown element
        fields = SignUpForm.Meta.fields + ("userrole",)

    # Setup rest of form fields
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

class EditUserSelectForm(forms.Form):
    user_to_edit = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Select a user to edit", required=True, widget=forms.Select(attrs=SELECT_FORM_STYLE))

class EditUserForm(forms.ModelForm):
    first_name = createField(255, "first_name", "Firstname")
    last_name = createField(255, "last_name", "Lastname")
    email = createField(255, "email", "Email (account@server.domain)", validators=[email_regex])
    phone_number = createField(13, "phone_number", "Phone number (+420XXXYYYZZZ)", validators=[phone_regex])
    userrole = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Role", widget=forms.Select(attrs=SELECT_FORM_STYLE))
    reset_password = forms.BooleanField(label="Reset user password", required=False)

    class Meta:
        model = CustomUser
        # List user attributes
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "userrole"
        )

    def __init__(self, *args, **kwargs):
        # Retrieve user being edited
        self.user = kwargs.pop("user")
        super(EditUserForm, self).__init__(*args, **kwargs)

        self.fields["first_name"].label= "First name"
        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].label= "Last name"
        self.fields["last_name"].initial = self.user.last_name
        self.fields["email"].label= "Email"
        self.fields["email"].initial = self.user.email
        self.fields["phone_number"].label= "Phone number"
        self.fields["phone_number"].initial = self.user.phone_number
        self.fields["userrole"].choices = reorderChoices(ROLE_CHOICES, self.user.userrole)

    def save(self):
        if self.cleaned_data.get("reset_password"):
            self.user.set_password("password1234")

        self.user.save()

class DeleteUserForm(forms.Form):
    user_to_delete = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Select a user to delete", required=True, widget=forms.Select(attrs=SELECT_FORM_STYLE))
    confirm = forms.BooleanField(label="Are you sure you want to delete this account? (No undo)", required=True)

class UserInfoForm(forms.ModelForm):
    first_name = createField(255, "first_name", "Firstname")
    last_name = createField(255, "last_name", "Lastname")
    email = createField(255, "email", "Email (account@server.domain)", validators=[email_regex])
    phone_number = createField(13, "phone_number", "Phone number (+420XXXYYYZZZ)", validators=[phone_regex])

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number"
        )

    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)

        # Fill form with user data
        self.fields["first_name"].widget.attrs["class"] = "form-control"
        self.fields["first_name"].label= "First name"
        self.fields["first_name"].initial = self.instance.first_name

        self.fields["last_name"].widget.attrs["class"] = "form-control"
        self.fields["last_name"].label= "Last name"
        self.fields["last_name"].initial = self.instance.last_name

        self.fields["email"].widget.attrs["class"] = "form-control"
        self.fields["email"].label= "Email"
        self.fields["email"].initial = self.instance.email

        self.fields["phone_number"].widget.attrs["class"] = "form-control"
        self.fields["phone_number"].label= "Phone number"
        self.fields["phone_number"].initial = self.instance.phone_number

class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs["class"] = "form-control"
        self.fields["old_password"].label= ""
        self.fields["old_password"].widget.attrs["placeholder"] = "Current password"

        self.fields["new_password1"].widget.attrs["class"] = "form-control"
        self.fields["new_password1"].label= ""
        self.fields["new_password1"].widget.attrs["placeholder"] = "New password"

        self.fields["new_password2"].widget.attrs["class"] = "form-control"
        self.fields["new_password2"].label= ""
        self.fields["new_password2"].widget.attrs["placeholder"] = "Confirm new password"

class UploadImageForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput())

    class Meta():
        model = AnimalPhoto
        fields = (
            "image",
        )

class CreateAnimalForm(forms.ModelForm):
    name         = createField(255, "name", "Enter animal name")
    species      = createField(255, "species", "Enter specie")
    breed        = createField(255, "breed", "Enter animal breed")
    gender       = forms.ChoiceField(choices=GENDER_CHOICES, required=True, label="Select gender", widget=forms.Select(attrs=SELECT_FORM_STYLE))
    birth_date   = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type" : "date",
            "id"   : "birth_date"
        }),
        label="Enter birth date (if known)"
    )
    arrival_date = forms.DateField(
        initial=date.today,
        required=True,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type" : "date",
            "id"   : "arrival_date"
        }),
        label="Enter arrival date"
    )
    description  = forms.CharField(widget=forms.Textarea(attrs={
        "class" : "form-control"
    }), required=True, label="Animal description")

    class Meta:
        model = Animal
        # List animal attributes
        fields = (
            "name",
            "species",
            "gender",
            "birth_date",
            "arrival_date",
            "breed",
            "description"
        )

AnimalPhotoFormSet = inlineformset_factory(Animal, AnimalPhoto, form=UploadImageForm, extra=1)

class EditAnimalForm(CreateAnimalForm):
    def __init__(self, *args, **kwargs):
        # Retrieve animal being edited
        self.animal = kwargs.pop("animal")
        super().__init__(*args, **kwargs)

        # Fill fields with animal's data
        self.fields["name"].initial = self.animal.name
        self.fields["species"].initial = self.animal.species
        self.fields["gender"].initial = self.animal.gender
        # Set if birth_date is known
        if self.animal.birth_date:
            self.fields["birth_date"].initial = self.animal.birth_date.strftime("%Y-%m-%d")
            self.fields["birth_date"].required = False
        # Arrival date is compulsory
        self.fields["arrival_date"].initial = self.animal.arrival_date.strftime("%Y-%m-%d")
        self.fields["breed"].initial = self.animal.breed
        self.fields["description"].initial = self.animal.description

class CreateMedicalRecordForm(forms.ModelForm):
    name   = createField(255, "name", "Enter record name")
    detail = forms.CharField(widget=forms.Textarea(attrs={
        "class" : "form-control"
    }), required=True, label="Record description")

    class Meta:
        model = HealthRecord
        # List health record attributes
        fields = (
            "name",
            "detail"
        )

class CreateAnimalTaskForm(forms.ModelForm):
    target_vet = forms.ModelChoiceField(queryset=CustomUser.objects.filter(userrole="vet"), label="Assign task to", required=True, widget=forms.Select(attrs=SELECT_FORM_STYLE))
    detail = forms.CharField(widget=forms.Textarea(attrs={
        "class" : "form-control"
    }), required=True, label="Task description")

    class Meta:
        model = AnimalTask
        # List animal task attributes
        fields = (
            "detail",
        )

class BookAnimalForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "id": "date_input"}),
        label="Date",
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "id": "start_time"}),
        label="Start time",
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "id": "end_time"}),
        label="End time",
    )

    def __init__(self, *args, **kwargs):
        self.animal = kwargs.pop("animal") # Retrieve animal being booked
        self.user = kwargs.pop("user") # Retrieve volunteer
        self.type = kwargs.pop("type") if "type" in kwargs else "walk" # Retrieve confirmation
        super().__init__(*args, **kwargs)

    class Meta:
        model = Reservation
        fields = ()

    def save(self, commit=True):
        reservation = Reservation()
        # Combine date and time into datetime
        date = self.cleaned_data["date"]
        start_time = self.cleaned_data["start_time"]
        end_time = self.cleaned_data["end_time"]
        # Set fields
        reservation.owner = self.user
        reservation.animal = self.animal
        reservation.type = self.type
        reservation.start_time = datetime.combine(date, start_time).replace(tzinfo=timezone.utc)
        reservation.end_time = datetime.combine(date, end_time).replace(tzinfo=timezone.utc)
        reservation.confirmation = "pending" if self.type == "walk" else "approved"

        if commit:
            reservation.save()
        return reservation

class AnimalSearchForm(forms.Form):
    # Search bar for animal
    search_bar = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "class": "form-control me-2",
            "placeholder": "Search animal",
            "aria-label": "Search"
        }),
    )
    # Selection for animal specie
    specie_choice = forms.MultipleChoiceField(choices=[], required=False, widget=forms.CheckboxSelectMultiple(), label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get all unique species values from animals
        species = [(breed, breed) for breed in Animal.objects.filter(is_active=True).values_list("species", flat=True).distinct()]
        self.fields["specie_choice"].choices = species
