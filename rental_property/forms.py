from django import forms

from rental_property.models import RentalUnit, UnitType, UnitAlbum

class AddRentalUnitForm(forms.ModelForm):
    class Meta:
        model = RentalUnit
        fields = ['unit_number', 'unit_type', 'bathrooms', 
        'bedrooms', 'status', 'total_occupants', 'water_available', 'electricity_available']

class UnitAlbumForm(forms.ModelForm):
    class Meta:
        model = UnitAlbum
        fields = ['image', ]