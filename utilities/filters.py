import django_filters
from accounts.models import Tenants
from django.forms.widgets import DateInput

from utilities.models import (ElectricityBilling, RentPayment,
                                       UnitRentDetails, WaterBilling, WaterMeter, ElectricityMeter)


class UnitTypeFilter(django_filters.FilterSet):
    class Meta:
        model = Tenants
        fields = ['rented_unit__unit_type','rented_unit__unit_number']
    def __init__(self, *args, **kwargs):
       super(UnitTypeFilter, self).__init__(*args, **kwargs)
       self.filters['rented_unit__unit_type'].label="Unit Type"
       self.filters['rented_unit__unit_number'].label="Unit Number"
        
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
        
class TenantElectricityBillsFilter(django_filters.FilterSet):
    class Meta:
        model = ElectricityBilling
        fields = ['bill_code','cleared','due_date']
        
class ManagerElectricityBillsFilter(django_filters.FilterSet):
    class Meta:
        model = ElectricityBilling
        fields = ['bill_code','cleared','lock_cycle','month','due_date']
        
class WaterMetersFilter(django_filters.FilterSet):
    class Meta:
        model = WaterMeter
        fields = ['ssid','number']
    def __init__(self, *args, **kwargs):
       super(WaterMetersFilter, self).__init__(*args, **kwargs)
       self.filters['number'].label="Meter Number"
     
class ElectricityMetersFilter(django_filters.FilterSet):
    class Meta:
        model = ElectricityMeter
        fields = ['ssid','number']
    def __init__(self, *args, **kwargs):
       super(ElectricityMetersFilter, self).__init__(*args, **kwargs)
       self.filters['number'].label="Meter Number"