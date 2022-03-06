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
    path('my-notice-to-vacate/<slug:building_slug>/<slug:username>/', views.my_move_out_notice, name='my-notice-to-vacate'),
    path('my_move_out_notices/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_move_out_notices, name='my_move_out_notices'),
    path('move-out-notices/<slug:building_slug>/', views.move_out_notices, name="move-out-notices"),
    path('cancel-notice/<slug:building_slug>/<slug:username>/<slug:notice_code>/', views.cancel_move_out_notice, name='cancel-notice'),
    path('view-notice/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:notice_code>/', views.move_out_pdf, name="view-moveout-notice"),
    path('eviction_view_pdf/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:code>/', views.eviction_view_pdf, name='eviction_view_pdf'),
    path('vacate-notice-update/<slug:building_slug>/<slug:notice_code>/', views.move_out_notice_update, name='vacate-notice-update'),
    
    path('building/<slug:building_slug>/stats/', views.building_dashboard, name="building_stats"),
    path('visits_overview/<slug:building_slug>/', views.visits_overview, name="visits_overview"),
    path('evictions_overview/<slug:building_slug>/', views.evictions_overview, name="evictions_overview"),
    path('moveouts_overview/<slug:building_slug>/', views.moveouts_overview, name='moveouts_overview'),
]
