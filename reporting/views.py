from django.contrib import messages
from complaints.models import Complaints, UnitReport
from core.models import (Contact, ContactReply, EvictionNotice,
                         ManagerTenantCommunication, MoveOutNotice,
                         ServiceRating, TenantEmails, UnitTour)
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.template.defaultfilters import date
from django.utils.translation import gettext_lazy as _
from slick_reporting.fields import SlickReportField
from slick_reporting.registry import field_registry
from slick_reporting.views import SlickReportView
from rental_property.models import Building, MaintananceNotice, RentalUnit
from utils.models import ElectricityBilling, RentPayment, UnitRentDetails, WaterBilling
import itertools
import operator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from work_order.models import HiredPersonnel, WorkOrder, WorkOrderPayments
from user_visit.models import UserVisit

User = get_user_model()
        
class LogIns(UserPassesTestMixin,SlickReportView):
    report_model = UserVisit
    date_field = 'created_at'
    columns = ['count__logins','__time_series__'] 
    time_series_pattern = 'monthly'
    time_series_columns = ['count__logins',]
    chart_settings = [{
        'type': 'column',
        'data_source': ['count__logins'],
        'title_source': 'created_at',
        'plot_total': True,
        'title': 'Monthly Logins',
    },]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
#core app reports
class ContactReportView(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class UnitTourReportView(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
    
class MoveOutNoticeReportView(UserPassesTestMixin,SlickReportView):
    report_model = MoveOutNotice
    date_field = 'created'
    group_by = 'building'
    columns = ['name','move_out_notice_status_count']
    time_series_pattern = 'monthly'
    time_series_columns = ['move_out_notice_status_count',]
    chart_settings = [{
        'type': 'line',
        'data_source': ['move_out_notice_status_count'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Move Out Notice Report'
        },]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class EvictionNoticeReportView(UserPassesTestMixin,SlickReportView):
    report_model = EvictionNotice
    date_field = 'created'
    group_by = 'building'
    columns = ['name','eviction_status_count']
    chart_settings = [{
        'type': 'line',
        'data_source': ['eviction_status_count'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Eviction Notice Report'
        },]
    
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')    
    
class ManagerTenantCommsReportView(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
        
class ReceivedEmailsReportView(UserPassesTestMixin,SlickReportView):
    report_model = TenantEmails
    date_field = 'created'
    group_by = 'building'
    columns = ['name','count_sent_emails']
    time_series_pattern = 'monthly'
    time_series_columns = ['count_sent_emails',]
    chart_settings = [{
        'type': 'line',
        'data_source': ['count_sent_emails'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Tenants &rarr; Manager Emails Report'
        },]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class ServiceRatingReportView(UserPassesTestMixin,SlickReportView):
    report_model = ServiceRating
    date_field = 'created'
    group_by = 'building'
    columns = ['name', 'score_calc'
               ]
    time_series_pattern = 'monthly'
    time_series_columns = ['score_calc',]
    chart_settings = [{
        'type': 'line',
        'data_source': ['score_calc'],
        'title_source': ['name'],
        'plot_total': False,
        'title': 'Service Rating Report'
        },]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')    

#complaints app reports

class UnitReportView(UserPassesTestMixin,SlickReportView):
    report_model = UnitReport
    date_field = 'created'
    group_by = 'building'
    columns = ['name','report__count',]
    time_series_pattern = 'monthly'
    time_series_columns = ['report__count']
    chart_settings = [{
        'type': 'line',
        'data_source': ['report__count'],
        'title_source': ['name'],
        'title': 'Tenant Report',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
    
class ComplaintsReportView(UserPassesTestMixin,SlickReportView):
    report_model = Complaints
    date_field = 'created'
    group_by = 'building'
    columns = ['name','complaints__count']
    time_series_pattern = 'monthly'
    time_series_columns = ['complaints__count']
    chart_settings = [{
        'type': 'line',
        'data_source': ['complaints__count'],
        'title_source': ['name'],
        'title': 'Complaints Report',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
    
# rental property app reports
class RentalUnitReports(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
    
class MaintananceNoticeReportView(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
    
    #utilities app
class RentPaymentsReportView(UserPassesTestMixin,SlickReportView):
    report_model = RentPayment
    date_field = 'added_on'
    group_by = 'building'
    columns = ['name',
               SlickReportField.create(Sum, 'amount', name='amount__sum', verbose_name=_('Total (KES)'))
               ]
    
    time_series_pattern = 'monthly'
    time_series_columns = [
                           SlickReportField.create(Sum, 'amount', name='amount__sum', verbose_name=_('Total (KES)'))
                           ]
    chart_settings = [{
        'type': 'column',
        'data_source': ['amount__sum'],
        'title_source': ['name'],
        'title': 'Rent Payments Report',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class WaterConsumptionReportView(UserPassesTestMixin,SlickReportView):
    report_model = WaterBilling
    date_field = 'added'
    group_by = 'building'
    columns = ['name','w_units__sum']
    
    time_series_pattern = 'monthly'
    time_series_columns = ['w_units__sum']
    chart_settings = [{
        'type': 'line',
        'data_source': ['w_units__sum'],
        'title_source': ['name'],
        'title': 'Water Consumption Report',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class WaterBillPaymentsReportView(UserPassesTestMixin,SlickReportView):
    report_model = WaterBilling
    date_field = 'added'
    group_by = 'building'
    columns = ['name',
               SlickReportField.create(Sum, 'amount_paid', name='amount_paid__sum', verbose_name=_('Total (KES)'))
               ]
    
    time_series_pattern = 'monthly'
    time_series_columns = [
                           SlickReportField.create(Sum, 'amount_paid', name='amount_paid__sum', verbose_name=_('Total (KES)'))
                           ]
    chart_settings = [{
        'type': 'column',
        'data_source': ['amount_paid__sum'],
        'title_source': ['name'],
        'title': 'Water Bill Payments',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
    
class ElectricityConsumptionReportView(UserPassesTestMixin,SlickReportView):
    report_model = ElectricityBilling
    date_field = 'added'
    group_by = 'building'
    columns = ['name','e_units__sum']
    
    time_series_pattern = 'monthly'
    time_series_columns = ['e_units__sum']
    chart_settings = [{
        'type': 'line',
        'data_source': ['e_units__sum'],
        'title_source': ['name'],
        'title': 'Electricity Consumption Report',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class ElectricityBillPaymentsReportView(UserPassesTestMixin,SlickReportView):
    report_model = ElectricityBilling
    date_field = 'added'
    group_by = 'building'
    columns = ['name',
               SlickReportField.create(Sum, 'amount_paid', name='amount_paid__sum', verbose_name=_('Total (KES)'))
               ]
    
    time_series_pattern = 'monthly'
    time_series_columns = [
                           SlickReportField.create(Sum, 'amount_paid', name='amount_paid__sum', verbose_name=_('Total (KES)'))
                           ]
    chart_settings = [{
        'type': 'column',
        'data_source': ['amount_paid__sum'],
        'title_source': ['name'],
        'title': 'Electricity Bill Payments',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
# work order reports

class HiredPersonnelReportView(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    

class WorkOrderReportView(UserPassesTestMixin,SlickReportView):
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
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')
    
class WorkOrderPaymentsReportView(UserPassesTestMixin,SlickReportView):
    report_model = WorkOrderPayments
    date_field = 'created'
    group_by = 'building'
    columns = ['name',
               SlickReportField.create(Sum, 'amount', name='amount_paid__sum', verbose_name=_('Total (KES)'))
               ]
    
    time_series_pattern = 'monthly'
    time_series_columns = [
                           SlickReportField.create(Sum, 'amount', name='amount_paid__sum', verbose_name=_('Total (KES)'))
                           ]
    chart_settings = [{
        'type': 'column',
        'data_source': ['amount_paid__sum'],
        'title_source': ['name'],
        'title': 'Work Order Payments',
    }]
    def test_func(self):
        return self.request.user.is_superuser
    def handle_no_permission(self):
        messages.info(self.request, 'You have no permission')
        return redirect('profile')