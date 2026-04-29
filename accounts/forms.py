from django import forms
from .models import Account
import re


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField(required=True)

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Minimum length
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters")

        # At least one uppercase
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter")

        # At least one lowercase
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter")

        # At least one digit
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("Password must contain at least one number")

        # At least one special character
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character")

        return password


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
