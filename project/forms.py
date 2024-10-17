from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser
from django.contrib.auth import get_user_model

ROLE_CHOICES = [
    ("admin", "Administrator"),
    ("carer", "Caretaker"),
    ("vet"  , "Veterinarian"),
    ("volunteer", "Volunteer"),
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
def createField(max_length, elementName, placeholderText, required):
    return forms.CharField(
        required   = required,
        max_length = max_length,
        label      = "",
        widget     = getTextWidget(elementName, placeholderText)
    )

# Singup form class
class SignUpForm(UserCreationForm):
    # Get new user information
    first_name   = createField(255, "first_name", "Enter Your firstname", True)
    last_name    = createField(255, "last_name", "Enter Your lastname", True)
    email        = createField(255, "email", "Enter Your email", True)
    phone_number = createField(9, "phone_number", "Enter Your phone number", True)

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
    first_name = createField(255, "first_name", "Firstname", False)
    last_name = createField(255, "last_name", "Lastname", False)
    email = createField(255, "email", "Email", False)
    phone_number = createField(9, "phone_number", "Phone number", False)
    user_role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Role")
    # TODO add a checkbox that flags the account for password reset / add the password field directly here

    def __init__(self, *args, **kwargs):
        # Assumes that user_id is a valid account for simplicity. It should be checked in the caller view
        self.user = CustomUser.objects.get(username=kwargs.pop("user_to_edit_id"))
        super(EditUserForm, self).__init__(*args, **kwargs)

        self.fields["first_name"].label= "First name"
        self.fields["first_name"].widget.attrs["placeholder"] = self.user.first_name
        self.fields["last_name"].label= "Last name"
        self.fields["last_name"].widget.attrs["placeholder"] = self.user.last_name
        self.fields["email"].label= "Email"
        self.fields["email"].widget.attrs["placeholder"] = self.user.email
        self.fields["phone_number"].label= "Phone number"
        self.fields["phone_number"].widget.attrs["placeholder"] = self.user.phone_number
        self.fields["user_role"].choices = reorderChoices(ROLE_CHOICES, self.user.userrole)

    def save(self):
        self.user.userrole = self.cleaned_data["user_role"]
        for field in ["first_name", "last_name", "email", "phone_number"]:
            if (value := self.cleaned_data.get(field)):
                setattr(self.user, field, value)

        self.user.save()

class DeleteUserForm(forms.Form):
    user_to_delete = forms.ModelChoiceField(queryset=CustomUser.objects.all(), label="Select a user to delete", required=True)
    confirm = forms.BooleanField(label="Are you sure you want to delete this account? (No undo)", required=True)
