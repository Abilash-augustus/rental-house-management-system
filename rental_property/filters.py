import django_filters
from rental_property.models import MaintananceNotice, RentalUnit, Building
from accounts.models import Tenants
from django.forms.widgets import DateInput

class BuildingUpdateFilter(django_filters.FilterSet):
    address_line = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Building
        fields = ['county','address_line']
    def __init__(self, *args, **kwargs):
       super(BuildingUpdateFilter, self).__init__(*args, **kwargs)
       self.filters['address_line'].label="Location"

class UnitsFilter(django_filters.FilterSet):
    class Meta:
        model = RentalUnit
        fields = ['unit_type','unit_number','bathrooms','bedrooms','status','maintanance_status']
        
class TenantsFilter(django_filters.FilterSet):
    class Meta:
        model = Tenants
        fields = ['id_number','moved_in','policy_agreement','moved_in']
        
class MaintananceNoticeFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    to_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = MaintananceNotice
        fields = ['ref_number','from_date','to_date','send_email']
        
    def __init__(self, *args, **kwargs):
       super(MaintananceNoticeFilter, self).__init__(*args, **kwargs)
       self.filters['send_email'].label="Email Sent ?"
       
class UserUnitsFilter(django_filters.FilterSet):
    class Meta:
        model = RentalUnit
        fields = ['unit_type','bathrooms','bedrooms']