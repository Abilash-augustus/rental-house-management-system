from django.urls import path

from core import views

app_name = 'core'
urlpatterns = [
    path('', views.home, name='home'),
    path('evictions/<slug:building_slug>/', views.view_eviction_notices, name='evictions'),
    path('create-eviction-notice/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.create_eviction_notice, name='create-eviction-notice'),
    path('eviction-notice/<slug:building_slug>/<slug:notice_code>/', views.eviction_notice_display, name='eviction-notice-detail'),
    path('contact/', views.CreateContact.as_view(), name='contact'),
    path('schedule-tour/<slug:unit_slug>/', views.schedule_unit_tour, name='schedule-tour'),
    path('visits/<slug:building_slug>/', views.scheduled_visits, name='visits'),
    path('updated-visit/<slug:building_slug>/<slug:visit_code>/', views.update_view_visits, name='update-visit'),
    path('my-notice-to-vacate/<slug:building_slug>/<slug:username>/', views.my_notice_to_vacate, name='my-notice-to-vacate'),
    path('move-out-notices/<slug:building_slug>/', views.move_out_notices, name="move-out-notices"),
    path('cancel-notice/<slug:building_slug>/<slug:username>/<slug:notice_code>/', views.cancel_vacate_notice, name='cancel-notice'),
    path('view-notice/<slug:building_slug>/<slug:username>/<slug:notice_code>/', views.view_move_out_notice, name="views-moveout-notice"),
    path('vacate-notice-update/<slug:building_slug>/<slug:notice_code>/', views.vacate_notice_update, name='vacate-notice-update'),
]
