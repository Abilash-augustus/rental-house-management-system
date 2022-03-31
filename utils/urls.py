from django.urls import path
from utils import views

urlpatterns = [
    path('my-rent/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_rent_details, name='my-rent'),
    path('submit-rent-pay-info/<slug:building_slug>/<slug:unit_slug>/<slug:rent_code>/<slug:username>/', views.submit_rent_payments, name='pay-info'),
    path('rent-and-utilities/<slug:building_slug>/', views.rent_and_utilities, name='rent-and-utilities'),
    path('rent_increase_notices/<building_slug>/', views.rent_increase_notices, name='rent_increase_notices'),
    path('add-rent/<slug:building_slug>/<slug:unit_slug>/', views.add_tenant_rent, name='add-rent'),
    path('add_rent_increase_notice/<slug:building_slug>/', views.add_rentincrement_notice, name='add_rentincrement_notice'),
    path('view_rent_increase_notice_pdf/<slug:building_slug>/<slug:r_code>/', views.view_rent_increase_notice_pdf, name='view_rent_increase_notice_pdf'),
    path('rent_defaulters/<slug:building_slug>/', views.rent_defaulters, name='rent_defaulters'),
    path('defaulter_details/<slug:building_slug>/<slug:username>/', views.defaulter_details, name='defaulter_details'),
    
    path('my_water_billing/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_water_billing, name='my_water_billing'),
    path('my_water_billing_details/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/', views.my_water_billing_details, name="my_water_billing_details"),
    path('my-electric-bills/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_electric_bills, name="my_electric_bills"),
    path('my_electricity_billing_details/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/', views.my_electricity_billing_details, name='my_electricity_billing_details'),
    path('rent-history/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.tenant_rent_history, name='rent-history'),
    path('tenant-rent-update-view/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:rent_code>/', views.update_tenant_rent, name='view-update-rent'),
    path('update-payment/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:rent_code>/<slug:track_code>/', views.update_tenant_rent_payment, name='update-rent'),
    path('rent-chart/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.rent_chart, name='rent_chart'),
    path('water-usage/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.tenant_water_usage, name='tenant-water-usage'),
    path('electricity_usage/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.tenant_electricity_usage, name='tenant_electricity_usage'),
    path('water-billing/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.manage_tenant_water_billing, name='manager-water-billing'),
    path('water-bill-detail/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/', views.update_tenant_water_billing_details, name="water-billing-details"),
    path('manage-tenant-electric-bills/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.manage_tenant_electric_bills, name="manage_tenant_electric_bills"),
    path('update_water_payments/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/<slug:tracking_code>/', views.update_water_payments, name='update_water_payments'),
    path('manage-tenant-bill-details/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/', views.update_tenant_electric_bill_details, name="tenant_electric_bill_details"),
    path('update_electricity_payments/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/<slug:t_code>/', views.update_electricity_payments, name='update_electricity_payments'),    
    path('building_rent_chart/<slug:building_slug>/', views.building_rent_overview, name="building_rent_overview"),
    path('building_water_consumtion/<slug:building_slug>/', views.building_water_consumtion, name='building_water_consumtion'),
    path('building_electricity_consumption/<slug:building_slug>/', views.building_electricity_consumption, name='building_electricity_consumption'),
    
    path('water_meter_management/<slug:building_slug>/', views.water_meter_management, name='water_meter_management'),
    path('water_meter_update/<slug:building_slug>/<slug:meter_ssid>/', views.water_meter_update, name='water_meter_update'),
    path('electricity_meter_management/<slug:building_slug>/', views.electricity_meter_management, name='electricity_meter_management'),
    path('electricity_meter_update/<slug:building_slug>/<slug:meter_ssid>/', views.electricity_meter_update, name='electricity_meter_update'),
    
    path('stripe/<slug:building_slug>/<slug:unit_slug>/<slug:rent_code>/<slug:username>/stripe_pay/', views.stripe_pay, name='stripe_pay'),
    path('online_pay/<slug:building_slug>/<slug:unit_slug>/<slug:rent_code>/<slug:username>/', views.mpesa_pay, name='mpesa_pay'),
    path('daraja/stk-push/callback/', views.stk_push_callback, name='mpesa_stk_push_callback'),
    ]