from django.urls import path

from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.CreateContact.as_view(), name='contact'),
    path('schedule-tour/<slug:unit_slug>/', views.schedule_unit_tour, name='schedule-tour'),
    path('visits/<slug:building_slug>/', views.scheduled_visits, name='visits'),
]
