from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, AnimalPhoto

# Function for constructing textInput with given args
def getTextWidget(elementName, placeholderText):
    return forms.TextInput(attrs={
        "class"       : "form-control",
        "name"        : elementName,
        "placeholder" : placeholderText
    })

# Function for constructing charFields
def createField(max_length, elementName, placeholderText):
    return forms.CharField(
        required   = True,
        max_length = max_length,
        label      = "",
        widget     = getTextWidget(elementName, placeholderText)
    )

# Singup form class
class SignUpForm(UserCreationForm):
    # Get new user information
    first_name   = createField(255, "first_name", "Enter Your firstname")
    last_name    = createField(255, "last_name", "Enter Your lastname")
    email        = createField(255, "email", "Enter Your email")
    phone_number = createField(9, "phone_number", "Enter Your phone number")

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
        self.fields["username"].widget.attrs["placeholder"] = "Enter Your username"
        self.fields["username"].label     = ""
        self.fields["username"].help_text = ""

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Enter Your password"
        self.fields["password1"].label     = ""
        self.fields["password1"].help_text = ""

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Enter Your password again"
        self.fields["password2"].label     = ""
        self.fields["password2"].help_text = ""

class CreateUserForm(SignUpForm):
    # Array of possible new roles
    role_choices = [
        ("admin", "Administrator"),
        ("carer", "Caretaker"),
        ("vet"  , "Veterinarian")
    ]
    # Add dropdown menu to select role for new user
    userrole = forms.ChoiceField(choices=role_choices, required=True, label="Select role for new user")

    class Meta(SignUpForm.Meta):
        # Inherit fields from SignUpForm and add own role dropdown element
        fields = SignUpForm.Meta.fields + ("userrole",)

    # Setup rest of form fields
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

class UploadImageForm(forms.ModelForm):
    # Card_id taken from home.html
    card_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta():
        model = AnimalPhoto
        fields = (
            "animal_id",
            "image",
        )
