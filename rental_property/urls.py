from django.urls import path

from rental_property import views

urlpatterns = [
    path('', views.buildings, name='operational-buildings'),
    path('building-units/<slug:building_slug>/', views.vacant_building_units, name='building-units'),
    path('building/<slug:building_slug>/rental-units/', views.managed_building_units, name="managed-building-units"),
    path('update-building-status/<slug:building_slug>/', views.update_building_status, name='update-building-status'),
    path('building-dashboard/<slug:building_slug>/', views.building_dashboard, name='building-dashboard'),
    path('unit-details/<slug:building_slug>/<slug:unit_slug>/', views.unit_details, name='unit-details'),
    path('add-rental-unit/<slug:building_slug>/', views.add_rental_unit, name='add-rental-unit'),
    path('update-rental-unit/<slug:building_slug>/<slug:unit_slug>/', views.update_unit, name="update-unit"),
    path('property_maintanance_notice/<slug:building_slug>/', views.property_maintanance_notice, name='property_maintanance_notice'),
    path('maintanance_notices/<slug:building_slug>/', views.maintanance_notices, name='maintanance_notices'),
    path('view_maintanance_notice_pdf/<slug:building_slug>/<slug:ref_number>/', views.view_maintanance_notice_pdf, name='view_maintanance_notice_pdf'),
    path('update_maintanance_notice/<slug:building_slug>/<slug:ref_number>/', views.update_maintanance_notice, name='update_maintanance_notice'),
    path('units_overview/<slug:building_slug>/', views.units_overview, name="units_overview"),
]