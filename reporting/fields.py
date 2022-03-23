from django.db.models import Count, Avg, Sum
from slick_reporting.fields import SlickReportField
from slick_reporting.registry import field_registry
from django.utils.translation import gettext_lazy as _

class CountLogin(SlickReportField):
    name = 'count__logins'
    verbose_name = _('Logins')
    calculation_field = 'created_at'
    calculation_method = Count 
    is_summable = True
field_registry.register(CountLogin)

class CountStatusContacts(SlickReportField):
    name = 'count_status'
    verbose_namme = 'Status Count'
    calculation_field = 'status'
    calculation_method = Count
field_registry.register(CountStatusContacts)

class VisiStatusCount(SlickReportField):
    name = 'visit_status_count'
    verbose_name = 'Visits'
    calculation_field = 'building'
    calculation_method = Count
field_registry.register(VisiStatusCount)

class MoveOutNoticeStatusCount(SlickReportField):
    name = 'move_out_notice_status_count'
    verbose_name = 'Notices'
    calculation_field = 'building'
    calculation_method = Count
field_registry.register(MoveOutNoticeStatusCount)

class EvictionNoticeStatusCount(SlickReportField):
    name = 'eviction_status_count'
    verbose_name = 'Notices'
    calculation_field = 'building'
    calculation_method = Count
field_registry.register(EvictionNoticeStatusCount)

class ScoreAvgField(SlickReportField):
    name = 'score_calc'
    verbose_name = 'Score'
    calculation_field = 'score'
    calculation_method = Avg
field_registry.register(ScoreAvgField)    
    

class CountSentEmails(SlickReportField):
    name = 'count_sent_emails'
    verbose_name = _('Emails')
    calculation_field = 'created'
    calculation_method = Count 
    is_summable = True
field_registry.register(CountSentEmails)

#complaints
class UnitReportsByTenants(SlickReportField):
    name = 'report__count'
    verbose_name = 'Tenant Reports'
    calculation_field = 'building'
    calculation_method = Count
field_registry.register(UnitReportsByTenants)

class ComplaintsReportField(SlickReportField):
    name = 'complaints__count'
    verbose_name=_('Complaints')
    calculation_field = 'building'
    calculation_method = Count
field_registry.register(ComplaintsReportField)

#utilities reports
class WaterConsumptionReportField(SlickReportField):
    name = 'w_units__sum'
    verbose_name = _('Units (m³)')
    calculation_field = 'units'
    calculation_method = Sum
field_registry.register(WaterConsumptionReportField)

class ElectricityConsumptionReportField(SlickReportField):
    name = 'e_units__sum'
    verbose_name = _('Units (KwH)')
    calculation_field = 'units'
    calculation_method = Sum
field_registry.register(ElectricityConsumptionReportField)

#work order app
class HiredPersonnelReportField(SlickReportField):
    name = 'personnel__count'
    verbose_name = _('Personnels')
    calculation_field = 'building'
    calculation_method = Count
field_registry.register(HiredPersonnelReportField)

class WorkOrderReportFiels(SlickReportField):
    name = 'work_order__count'
    verbose_name = _('Work Orders')
    calculation_field = 'building'
    calcution_method = Count
field_registry.register(WorkOrderReportFiels)