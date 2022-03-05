from django.urls import path

from rental_property import views

urlpatterns = [
    path('', views.buildings, name='operational-buildings'),
    path('building-units/<slug:building_slug>/', views.open_building_units, name='building-units'),
    path('building/<slug:building_slug>/rental-units/', views.managed_building_units, name="managed-building-units"),
    path('update-building-status/<slug:building_slug>/', views.update_building_status, name='update-building-status'),
    path('building-dashboard/<slug:building_slug>/', views.building_dashboard, name='building-dashboard'),
    path('unit-details/<slug:building_slug>/<slug:unit_slug>/', views.unit_details, name='unit-details'),
    path('vacancies/county/<slug:county_slug>/', views.property_by_county, name='by-county'),
    path('add-rental-unit/<slug:building_slug>/', views.add_rental_unit, name='add-rental-unit'),
    path('update-rental-unit/<slug:building_slug>/<slug:unit_slug>/', views.update_unit, name="update-unit"),
    
    path('units_overview/<slug:building_slug>/', views.units_overview, name="units_overview"),
]