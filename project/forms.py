from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

# Function for constructing textInput with given args
def getTextWidget(elementName, placeholderText):
    return forms.TextInput(attrs={
        "class"       : "form-control",
        "name"        : elementName,
        "placeholder" : placeholderText
    })

# Singup form class
class SignUpForm(UserCreationForm):
    # Get new user information
    first_name   = forms.CharField(widget=getTextWidget("first_name", "Enter Your firstname"))
    last_name    = forms.CharField(widget=getTextWidget("last_name", "Enter Your lastname"))
    email        = forms.CharField(widget=getTextWidget("email", "Enter Your email"))
    phone_number = forms.CharField(widget=getTextWidget("phone_number", "Enter Your phone number"))

    # New user model class
    class NewUser:
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

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Enter Your username"
        self.fields["username"].label     = ""
        self.fields["username"].help_text = ""

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Enter Your password"
        self.fields["password1"].label     = ""
        self.fields["password1"].help_text = ""

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Enter Your password"
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
    role = forms.ChoiceField(choices=role_choices, required=True, label="Select role for new user")

    class NewUser(SignUpForm.NewUser):
        # Inherit fields from SignUpForm and add own role dropdown element
        fields = SignUpForm.NewUser.fields + ("userrole",)

    # Setup rest of form fields
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
