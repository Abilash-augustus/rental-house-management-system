import django_filters
from complaints.models import UnitReport

class UnitReportFilter(django_filters.FilterSet):
    class Meta:
        model = UnitReport
        fields = ['code','report_type','status','created']