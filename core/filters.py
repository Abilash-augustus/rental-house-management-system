from accounts.models import Tenants
import django_filters
from django.forms.widgets import DateInput
from django import forms

from core.models import ManagerTenantCommunication, UnitTour,EvictionNotice, MoveOutNotice

class VisitFilter(django_filters.FilterSet):
    class Meta:
        model = UnitTour
        fields = ['visit_code','visit_status','visit_date','created']
        
class EvictionNoticeFilter(django_filters.FilterSet):
    class Meta:
        model = EvictionNotice
        fields = ['notice_code','eviction_status','eviction_due']
        
class MoveOutNoticeFilter(django_filters.FilterSet):
    move_out_date = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))
    class Meta:
        model = MoveOutNotice
        fields = ['code','move_out_date','notice_status','drop']
        
    def __init__(self, *args, **kwargs):
       super(MoveOutNoticeFilter, self).__init__(*args, **kwargs)
       self.filters['drop'].label="Dropped?"

class MyNoticeFilter(django_filters.FilterSet):
    class Meta:
        model = MoveOutNotice
        fields = ['notice_status','drop']
    def __init__(self, *args, **kwargs):
       super(MyNoticeFilter, self).__init__(*args, **kwargs)
       self.filters['drop'].label="Dropped?"
        
class CommsFilter(django_filters.FilterSet):
    created = django_filters.DateFilter(widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = ManagerTenantCommunication
        fields = ['ref_number','subject','created']
    def __init__(self, *args, **kwargs):
       super(CommsFilter, self).__init__(*args, **kwargs)
       self.filters['created'].label="Sent On"