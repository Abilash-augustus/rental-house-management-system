from django.urls import path
from complaints import views

urlpatterns = [
    path('create-report/<slug:username>/<slug:unit_slug>/', views.create_a_report, name='create-report'),
    path('reports/building/<slug:building_slug>/', views.view_reports, name='reports'),
]