from django import forms

from rental_property.models import RentalUnit, UnitType, UnitAlbum, Building

class AddRentalUnitForm(forms.ModelForm):
    class Meta:
        model = RentalUnit
        fields = ['unit_number', 'unit_type', 'bathrooms', 
        'bedrooms', 'status', 'total_occupants', 'water_available', 'electricity_available']

class UnitAlbumForm(forms.ModelForm):
    class Meta:
        model = UnitAlbum
        fields = ['image', ]
        
class BuildingUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BuildingUpdateForm, self).__init__(*args, **kwargs)
        self.fields['estate'].disabled = True
        self.fields['name'].disabled = True
        self.fields['registered_owner'].disabled = True
        self.fields['manager'].disabled = True
        self.fields['address_line'].disabled = True
        self.fields['county'].disabled = True
        self.fields['added'].disabled = True
    class Meta:
        model = Building
        fields = ['name', 'estate','registered_owner', 'manager', 
                       'address_line', 'county','added', 'building_status']
        
class UpdateRentalUnit(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateRentalUnit, self).__init__(*args, **kwargs)
        self.fields['building'].disabled = True
    class Meta:
        model = RentalUnit
        exclude = ['slug','updated',]