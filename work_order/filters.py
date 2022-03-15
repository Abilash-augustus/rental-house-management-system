import django_filters
from accounts.models import Tenants
from django.forms.widgets import DateInput
from work_order.models import HiredPersonnel, WorkOrder

class HiredPersonnelFilter(django_filters.FilterSet):
    hired_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = HiredPersonnel
        fields = ['full_name','personnel_email','id_number','is_active','hired_date']
        
class WorkOrderFilter(django_filters.FilterSet):
    due_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = WorkOrder
        fields = ['work_order_code','priority','due_date']
        