from django import forms
from django.contrib.auth import get_user_model

from accounts.models import Managers, Profile, Tenants

User = get_user_model()

class DateInput(forms.DateInput):
    input_type = 'date'

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar']
        widgets = {
            'avatar': forms.FileInput,
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['prefered_payment_method', 'street_address', 'county', 'country']


class AddManagerForm(forms.ModelForm):
    class Meta:
        model = Managers
        exclude = ['added_by', 'status', 'created', 'updated']