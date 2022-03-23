from django.urls import path
from reporting import views

urlpatterns = [
    path('logins_report/', views.LogIns.as_view(), name='logins_report'),
    
    path('contact_report/', views.ContactReportView.as_view(), name='contact_report'),
    path('unit_tour_report/', views.UnitTourReportView.as_view(), name='unit_tour_report'),
    path('move_out_notice_report/', views.MoveOutNoticeReportView.as_view(), name='move_out_notice_eport'),
    path('eviction_notice_report/', views.EvictionNoticeReportView.as_view(), name='eviction_notice_report'),
    path('manager_to_tenants_comms_report/', views.ManagerTenantCommsReportView.as_view(), name='manager_to_tenants_comms_report'),
    path('tenants_to_managers_comms_report/', views.ReceivedEmailsReportView.as_view(), name='tenants_to_managers_comms_report'),
    path('service_rating_report/', views.ServiceRatingReportView.as_view(), name='service_rating_report'),
    
    path('by_tenant_unit_reports/', views.UnitReportView.as_view(), name='unit_reports_by_tenants'),
    path('complaints_report/', views.ComplaintsReportView.as_view(), name='complaints_report'),
    path('building_houses_report/', views.RentalUnitReports.as_view(), name='building_house_report'),
    path('maintanance_notices_report/', views.MaintananceNoticeReportView.as_view(), name='maintanance_notices_report'),
    
    path('water_consumption_report/', views.WaterConsumptionReportView.as_view(), name='water_consumption_report'),
    path('electricity_consumption_report/', views.ElectricityConsumptionReportView.as_view(), name='electricity_consumption_report'),
    path('rent_payment_report/', views.RentPaymentsReportView.as_view(), name='rent_payment_report'),
    path('water_billing_payment_report/', views.WaterBillPaymentsReportView.as_view(), name='water_billing_payment_report'),
    path('electricity_bill_payment_report/', views.ElectricityBillPaymentsReportView.as_view(), name='electricity_bill_payment_report'),
    
    path('hired_personnel_report/', views.HiredPersonnelReportView.as_view(), name='hired_personnel_report'),
    path('work_order_report/', views.WorkOrderReportView.as_view(), name='work_order_report'),
    path('work_order_payment_report/', views.WorkOrderPaymentsReportView.as_view(), name='work_order_payment_report'),
]
