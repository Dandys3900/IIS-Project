from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from django import forms
from .models import *

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
def createField(max_length, elementName, placeholderText, required=True):
    return forms.CharField(
        required   = required,
        max_length = max_length,
        label      = "",
        widget     = getTextWidget(elementName, placeholderText)
    )

# Singup form class
class SignUpForm(UserCreationForm):
    # Get new user information
    first_name   = createField(255, "first_name", "Enter firstname")
    last_name    = createField(255, "last_name", "Enter lastname")
    email        = createField(255, "email", "Enter email")
    phone_number = createField(9, "phone_number", "Enter phone number")

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
        self.fields["username"].initial = "Enter username"
        self.fields["username"].label     = ""

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].initial = "Enter password"
        self.fields["password1"].label     = ""

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].initial = "Enter password again"
        self.fields["password2"].label     = ""
        self.fields["password2"].help_text = ""

class CreateUserForm(SignUpForm):
    # Add dropdown menu to select role for new user
    userrole = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Select role for new user")

    class Meta(SignUpForm.Meta):
        # Inherit fields from SignUpForm and add own role dropdown element
        fields = SignUpForm.Meta.fields + ("userrole",)

    # Setup rest of form fields
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

class EditUserSelectForm(forms.Form):
    user_to_edit = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Select a user to edit", required=True)

class EditUserForm(forms.Form):
    user_name = createField(255, "user_name", "Username", False)
    first_name = createField(255, "first_name", "Firstname", False)
    last_name = createField(255, "last_name", "Lastname", False)
    email = createField(255, "email", "Email", False)
    phone_number = createField(9, "phone_number", "Phone number", False)
    userrole = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Role")
    reset_password = forms.BooleanField(label="Reset user password", required=False)

    def __init__(self, *args, **kwargs):
        # Retrieve user being edited
        self.user = kwargs.pop("user")
        super(EditUserForm, self).__init__(*args, **kwargs)

        self.fields["user_name"].label= "Username"
        self.fields["user_name"].initial = self.user.username
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
        for field in self.user.REQUIRED_FIELDS:
            if (value := self.cleaned_data.get(field)):
                setattr(self.user, field, value)
        if self.cleaned_data.get("reset_password"):
            self.user.password = "password1234"

        self.user.save()

class DeleteUserForm(forms.Form):
    user_to_delete = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Select a user to delete", required=True)
    confirm = forms.BooleanField(label="Are you sure you want to delete this account? (No undo)", required=True)

class UserInfoForm(EditUserForm):
    # Field to show user's current password with ability to change it
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class" : "form-control"
    }), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # From inherited fields, remove ones we don't need
        del self.fields["userrole"]
        del self.fields["reset_password"]

        # Init password fields
        self.fields["password"].label= "Password"
        self.fields["password"].initial = self.user.password

class UploadImageForm(forms.ModelForm):
    # Card_id taken from home.html
    image = forms.ImageField(widget=forms.FileInput())

    class Meta():
        model = AnimalPhoto
        fields = (
            "image",
        )

class CreateAnimalForm(forms.ModelForm):
    # Specify attributes for custom widgets
    attrs = {
        "type"  : "date",
        "class" : "form-control"
    }

    name         = createField(255, "name", "Enter animal name")
    species      = createField(255, "species", "Enter specie")
    breed        = createField(255, "breed", "Enter animal breed")
    gender       = forms.ChoiceField(choices=GENDER_CHOICES, required=True, label="Select gender")
    birth_date   = forms.DateField(required=False, widget=forms.DateInput(attrs=attrs), label="Enter birth date (if known)")
    arrival_date = forms.DateField(required=True, widget=forms.DateInput(attrs=attrs), label="Enter arrival date")
    description  = forms.CharField(widget=forms.Textarea, required=True, label="Animal description")

    class Meta:
        model = Animal
        # List user attributes
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

        # Set custom placeholders for each field
        self.fields['name'].initial = self.animal.name
        self.fields['name'].required = False
        self.fields['species'].initial = self.animal.species
        self.fields['species'].required = False
        self.fields['gender'].initial = self.animal.gender
        self.fields['gender'].required = False
        # Set if birth_date is known
        if self.animal.birth_date:
            self.fields['birth_date'].initial = self.animal.birth_date.strftime('%Y-%m-%d')
            self.fields['birth_date'].required = False
        self.fields['arrival_date'].initial = self.animal.arrival_date.strftime('%Y-%m-%d')
        self.fields['arrival_date'].required = False
        self.fields['breed'].initial = self.animal.breed
        self.fields['breed'].required = False
        self.fields['description'].initial = self.animal.description
        self.fields['description'].required = False
