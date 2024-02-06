from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Certification
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import os
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1')

from django import forms
from .models import Certification  # Import the Certification model from your app

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification  # Update the model name to OrganicCertification
        fields = [
            'certification_image',
            'first_name',
            'last_name',
            'expiry_date_from',  # Remove 'expiry_date_from'
            'certification_authority',
            'phone_number',  # Add 'phone_number' field
            'certification_number',# Add 'certification_number' field
            'address',  
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['certification_image'].required = False

    def clean_certification_image(self):
        certification_image = self.cleaned_data.get('certification_image')

        if certification_image:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(certification_image.name)[1].lower()

            if file_extension not in allowed_extensions:
                raise forms.ValidationError("Only JPG, JPEG, PNG, and GIF images are allowed.")

        return certification_image


