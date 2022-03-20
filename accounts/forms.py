from django import forms
from django.contrib.auth import get_user_model

from accounts.models import Managers, Profile, Tenants
from rental_property.models import RentalUnit
  
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
        fields = ['phone','street_address', 'county', 'country']

class AddManagerForm(forms.ModelForm):
    class Meta:
        model = Managers
        exclude = ['added_by', 'status', 'created', 'updated']

class TenantsForm(forms.ModelForm):
    def __init__(self, building, *args, **kwargs):
        super(TenantsForm,self).__init__(*args, **kwargs)
        self.fields['rented_unit'].queryset = RentalUnit.objects.filter(building=building,status='ready')
    class Meta:
        model = Tenants
        fields = ['associated_account', 'full_name', 'id_number', 'id_front', 'id_back', 'active_phone_number', 
        'rented_unit','policy_agreement', 'moved_in', 'move_in_date']
        widgets = {
            'move_in_date': DateInput(),
            'id_back': forms.FileInput,
            'id_front': forms.FileInput,
        }

class TenantUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TenantUpdateForm,self).__init__(*args, **kwargs)
        self.fields['rented_unit'].disabled = True
        self.fields['created'].disabled = True
    class Meta:
        model = Tenants
        fields = "__all__"
        widgets = {
            'move_in_date': DateInput(),
            'id_back': forms.FileInput,
            'id_front': forms.FileInput,
        }
