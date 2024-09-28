from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

# Singup form class
class SignUpForm(UserCreationForm):
    # Lambda for constructing textInput with given args
    getTextWidget = lambda elementName, placeholderText: forms.TextInput(attrs={
        "class"       : "form-control",
        "name"        : elementName,
        "placeholder" : placeholderText
    })

    # Get new user information
    email     = forms.EmailField(widget=getTextWidget("email", "Enter Your email"))
    firstname = forms.CharField(widget=getTextWidget("firstname", "Enter Your firstname"))
    lastname  = forms.CharField(widget=getTextWidget("lastname", "Enter Your lastname"))

    # New user model class
    class NewUser:
        model = User
        # List user attributes
        fields = (
            "username",
            "firstname",
            "lastname",
            "email",
            "password1",
            "password2"
        )

    # Setup rest of form fields (username, password1+2)
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Enter Your username"
        self.fields['username'].label = ""
        self.fields['username'].help_text = ""

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Enter Your password"
        self.fields['password1'].label = ""
        self.fields['password1'].help_text = ""

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Enter Your password"
        self.fields['password2'].label = ""
        self.fields['password2'].help_text = ""
