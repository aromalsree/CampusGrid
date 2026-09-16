from django import forms
from .models import App_users
from django.contrib.auth.forms import AuthenticationForm

class UserRegForm(forms.ModelForm):
    '''Form for User registeation '''
    conform_passwoed = forms.PasswordInput(attrs={'class':'form-control'})
    class Meta:
        modul
        fields = ['username', 'password', 'first_name', 'last_name', 'institution', 'phone', 'email']
        widgets = {
            "username": forms.TextInput(attrs={'class':'form-control'}),
            "last_name": forms.TextInput(attrs={'class':'form-control'}),
            "first_name": forms.TextInput(attrs={'class':'form-control'}),
            "institution": forms.TextInput(attrs={'class':'form-control'}),
            "phone": forms.NumberInput(attrs={'class':'form-control'}),
            "email": forms.EmailField(attrs={'class':'form-control'}),
            "password": forms.TextInput(attrs={'class':'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        conform_password = cleaned_data.get("conform_password")
        
        if password and conform_password and password != conform_password:
            raise ValidationError("Password not maching")
        if not cleaned_data.get("first_name"):
            raise ValidationError("Provide first name")
        if not cleaned_data.get("last_name"):
            raise ValidationError("Provide last name")


        return cleaned_data
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user    
