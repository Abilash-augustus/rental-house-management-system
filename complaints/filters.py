import django_filters
from complaints.models import UnitReport, Complaints

class UnitReportFilter(django_filters.FilterSet):
    class Meta:
        model = UnitReport
        fields = ['code','report_type','status','created']
        
class ComplaintsFilter(django_filters.FilterSet):
    class Meta:
        model = Complaints
        fields = ['complaint_code','name','status',]