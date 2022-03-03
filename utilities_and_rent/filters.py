import django_filters

"""from rental_property.models import RentalUnit, Building"""

from accounts.models import Tenants
from django.forms.widgets import DateInput

from utilities_and_rent.models import (RentPayment, UnitRentDetails,
                                       WaterBilling)


class UnitTypeFilter(django_filters.FilterSet):
    
    class Meta:
        model = Tenants
        fields = ['rented_unit__unit_type']
        
class RentDetailsFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    end_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = UnitRentDetails
        fields = ['start_date','end_date','status','cleared']
        
class PaymentsFilter(django_filters.FilterSet):
    class Meta:
        model = RentPayment
        fields = ['payment_method','status']
        
class WaterBilingFilter(django_filters.FilterSet):
    due_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = WaterBilling
        fields = ['bill_code','cleared', 'due_date']