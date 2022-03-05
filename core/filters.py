import django_filters

from core.models import UnitTour

class VisitFilter(django_filters.FilterSet):
    class Meta:
        model = UnitTour
        fields = ['visit_code','visit_status','visit_date','created']