from django.urls import path

from rental_property import views

urlpatterns = [
    path('', views.buildings, name='operational-buildings'),
    path('building-units/<slug:building_slug>/', views.building_units, name='building-units'),
    path('<slug:building_slug>/tenants/', views.building_dashboard, name='building-tenants'),
    path('unit-details/<slug:building_slug>/<slug:unit_slug>/', views.unit_details, name='unit-details'),
    path('by-county/<slug:county_slug>/', views.property_by_county, name='by-county'),
    path('add-rental-unit/<slug:building_slug>/', views.add_rental_unit, name='add-rental-unit'),
]