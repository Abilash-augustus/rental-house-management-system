from django.urls import path

from core import views

app_name = 'core'
urlpatterns = [
    path('', views.home, name='home'),
    path('eviction-notice/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.eviction_notice, name='eviction-notice'),
    path('contact/', views.CreateContact.as_view(), name='contact'),
    path('schedule-tour/<slug:unit_slug>/', views.schedule_unit_tour, name='schedule-tour'),
    path('visits/<slug:building_slug>/', views.scheduled_visits, name='visits'),
    path('updated-visit/<slug:building_slug>/<slug:visit_code>/', views.update_view_visits, name='update-visit'),
]
