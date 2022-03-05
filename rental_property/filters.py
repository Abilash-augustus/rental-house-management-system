import django_filters
from rental_property.models import RentalUnit
from accounts.models import Tenants

class UnitsFilter(django_filters.FilterSet):
    class Meta:
        model = RentalUnit
        fields = ['unit_type','unit_number','bathrooms','bedrooms','status','maintanance_status']
        
class TenantsFilter(django_filters.FilterSet):
    class Meta:
        model = Tenants
        fields = ['id_number','moved_in','policy_agreement','moved_in']