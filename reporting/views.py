from complaints.models import Complaints, UnitReport
from core.models import (Contact, ContactReply, EvictionNotice,
                         ManagerTenantCommunication, MoveOutNotice,
                         ServiceRating, TenantEmails, UnitTour)
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from django.shortcuts import render
from django.template.defaultfilters import date
from django.utils.translation import gettext_lazy as _
from slick_reporting.fields import SlickReportField
from slick_reporting.registry import field_registry
from slick_reporting.views import SlickReportView
from rental_property.models import Building, MaintananceNotice, RentalUnit
from utilities.models import ElectricityBilling, UnitRentDetails, WaterBilling
import itertools
import operator

from work_order.models import HiredPersonnel, WorkOrder

User = get_user_model()

class LogIns(SlickReportView):
    report_model = User
    date_field = 'last_login'
    group_by = 'is_verified'
    columns = ['is_verified','count__login','__time_series__'] 
    time_series_pattern = 'monthly'
    time_series_columns = ['count__login',]
    chart_settings = [{
        'type': 'bar',
        'data_source': ['count__login'],
        'title_source': 'last_login',
        'plot_total': True,
        'title': _('Logins Per Day'),

    }, ]
    """
    def format_row(self, creation_date):
        creation_date['last_login'] = date(creation_date['last_login'], 'd-m-y H:i')
        return creation_date
    """
    
#core app reports
class ContactReportView(SlickReportView):
    report_model = Contact
    date_field = 'created'
    group_by = 'status'
    columns = ['status', 'count_status']

    
    chart_settings = [{
        'type': 'pie',
        'data_source': ['count_status'],
        'title_source': ['status'],
        'plot_total': False,
        'title': 'Contacts By Status'
        },
        {'type': 'bar',
         'title_source': ['status'],
         'data_source': ['count_status'],
         'title': 'Contacts By Status'
         }
        ]
    
class UnitTourReportView(SlickReportView):
    report_model = UnitTour
    date_field = 'visit_date'
    group_by = 'building'
    columns = ['name','visit_status_count']
    time_series_pattern = 'monthly'
    time_series_columns = ['visit_status_count',]
    chart_settings = [{
        'type': 'line',
        'data_source': ['visit_status_count'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Unit Tours Line Chart'
        },
        {'type': 'Column',
         'data_source': ['visit_status_count'],
         'title': 'Unit Tours Column Graph'
         }
        ]
    
class MoveOutNoticeReportView(SlickReportView):
    report_model = MoveOutNotice
    date_field = 'created'
    group_by = 'notice_status'
    columns = ['notice_status','move_out_notice_status_count']
    chart_settings = [{
        'type': 'pie',
        'data_source': ['move_out_notice_status_count'],
        'title_source': ['notice_status'],
        'plot_total': False,
        'title': 'Move Out Notice Report'
        },]
    
class EvictionNoticeReportView(SlickReportView):
    report_model = EvictionNotice
    date_field = 'created'
    group_by = 'eviction_status'
    columns = ['eviction_status','eviction_status_count']
    chart_settings = [{
        'type': 'pie',
        'data_source': ['eviction_status_count'],
        'title_source': ['eviction_status'],
        'plot_total': False,
        'title': 'Eviction Notice Report'
        },]
    
class ServiceRatingReportView(SlickReportView):
    report_model = ServiceRating
    date_field = 'created'
    group_by = 'building'
    columns = ['name', 'score_calc'
               ]
    time_series_pattern = 'monthly'
    time_series_columns = ['score_calc',]
    chart_settings = [{
        'type': 'column',
        'data_source': ['score_calc'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Service Rating Report'
        },]
    
class ManagerTenantCommsReportView(SlickReportView):
    report_model = ManagerTenantCommunication
    date_field = 'created'
    group_by = 'building'
    columns = ['name', 'count_sent_emails']
    time_series_pattern = 'monthly'
    time_series_columns = ['count_sent_emails',]
    chart_settings = [{
        'type': 'column',
        'data_source': ['count_sent_emails'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Manager &rarr; Tenants Emails'
        },]
        
class ReceivedEmailsReportView(SlickReportView):
    report_model = TenantEmails
    date_field = 'created'
    group_by = 'building'
    columns = ['name','count_sent_emails']
    time_series_pattern = 'monthly'
    time_series_columns = ['count_sent_emails',]
    chart_settings = [{
        'type': 'column',
        'data_source': ['count_sent_emails'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Tenants &rarr; Manager Emails Report'
        },]

#complaints app reports

class UnitReportView(SlickReportView):
    report_model = UnitReport
    date_field = 'created'
    group_by = 'report_type'
    columns = ['name',
               SlickReportField.create(Count, 'report_type',
                                       name='report_type__count', verbose_name=_('Reports'))]
    time_series_pattern = 'monthly'
    time_series_columns = ['report_type__count']
    chart_settings = [{
        'type': 'column',
        'data_source': ['report_type__count'],
        'title_source': ['name'],
        'title': 'Tenant Reports',
    }]
    
class ComplaintsReportView(SlickReportView):
    report_model = Complaints
    date_field = 'created'
    group_by = 'building'
    columns = ['name','status__count']
    time_series_pattern = 'monthly'
    time_series_columns = ['status__count']
    chart_settings = [{
        'type': 'line',
        'data_source': ['status__count'],
        'title_source': ['name'],
        'title': 'Complaints Report',
    }]
    
# rental property app reports
class RentalUnitReports(SlickReportView):
    report_model = RentalUnit
    date_field = 'updated'
    group_by = 'building'
    columns = ['name',SlickReportField.create(Count, 'status',
                                       name='status__count', verbose_name=_('Units'))]
    crosstab_model = 'unit_type'
    crosstab_columns = [SlickReportField.create(Count, 'status', name='status__count', verbose_name=_('Unit Status'))
                        ]
    crostab_model = 'maintanance_status'
    chart_settings = [{
        'type': 'column',
        'data_source': ['status__count'],
        'title_source': ['name'],
        'title': 'Rental Units Report',
    }]
    
class MaintananceNoticeReportView(SlickReportView):
    report_model = MaintananceNotice
    date_field = 'created'
    group_by = 'maintanance_status'
    columns = ['maintanance_status',
               SlickReportField.create(Count, 'maintanance_status', name='status__count', verbose_name=_('Status'))
               ]
    chart_settings = [{
        'type': 'pie',
        'data_source': ['status__count'],
        'title_source': ['maintanance_status'],
        'title': 'Maintanance Report',
    }]
    
    #utilities app
class WaterConsumptionReportView(SlickReportView):
    report_model = WaterBilling
    date_field = 'added'
    group_by = 'building'
    columns = ['name','w_units__sum']
    
    time_series_pattern = 'monthly'
    time_series_columns = ['w_units__sum']
    chart_settings = [{
        'type': 'column',
        'data_source': ['w_units__sum'],
        'title_source': ['name'],
        'title': 'Water Consumption Report',
    }]
    
class ElectricityConsumptionReportView(SlickReportView):
    report_model = ElectricityBilling
    date_field = 'added'
    group_by = 'building'
    columns = ['name','e_units__sum']
    
    time_series_pattern = 'monthly'
    time_series_columns = ['e_units__sum']
    chart_settings = [{
        'type': 'column',
        'data_source': ['e_units__sum'],
        'title_source': ['name'],
        'title': 'Water Consumption Report',
    }]

# work order reports

class HiredPersonnelReportView(SlickReportView):
    report_model = HiredPersonnel
    date_field = 'hired_date'
    group_by = 'building'
    columns = ['name', 'personnel__count']
    time_series_pattern = 'annually'
    time_series_columns = ['personnel__count']
    chart_settings = [{
        'type': 'pie',
        'data_source': ['personnel__count'],
        'title_source': ['name'],
        'title': 'Personnels Report',
    }]
    
class WorkOrderReportView(SlickReportView):
    report_model = WorkOrder
    date_field = 'created'
    group_by = 'building'
    columns = ['name','work_order__count']
    time_series_pattern = 'monthly'
    time_series_columns = ['work_order__count']
    
    chart_settings = [{
        'type': 'column',
        'data_source': ['work_order__count'],
        'title_source': ['name'],
        'title': 'Work Order Report',
    }]
# todo add payment reports