from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from .models import App_users

class UserRegForm(forms.ModelForm):
    '''Form for User registration '''
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = App_users
        fields = ['username', 'password', 'first_name', 'last_name', 'institution', 'phone', 'email']
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-control'}),
            "last_name": forms.TextInput(attrs={'class': 'form-control'}),
            "first_name": forms.TextInput(attrs={'class': 'form-control'}),
            "institution": forms.TextInput(attrs={'class': 'form-control'}),
            "phone": forms.TextInput(attrs={'class': 'form-control'}),
            "email": forms.EmailInput(attrs={'class': 'form-control'}),
            "password": forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = (
            cleaned_data.get("password_confirm")
            or cleaned_data.get("confirm_password")
            or self.data.get("password_confirm")
            or self.data.get("confirm_password")
        )
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Password not maching")
        if password and not confirm_password:
            raise ValidationError("Please confirm your password")

        if "first_name" in self.data and not cleaned_data.get("first_name"):
            raise ValidationError("Provide first name")
        if "last_name" in self.data and not cleaned_data.get("last_name"):
            raise ValidationError("Provide last name")

        cleaned_data["confirm_password"] = confirm_password
        cleaned_data["password_confirm"] = confirm_password
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user
            


# custom login auth form 
class LoginForm(AuthenticationForm):


    username = forms.CharField(widget=forms.TextInput(attrs={"name": "username", "id": "id_username", "class": "form-control",
                                                            "required": true, "autofocus": true, "placeholder": "student@university.edu"}))
    password = forms.CharField(widget=forms.TextInput(attrs={
                                                                "name": "password",
                                                                "id": "id_password",
                                                                "class": "form-control",
                                                                "required": True,
                                                                "placeholder": "••••••••",
                                                            }))

    