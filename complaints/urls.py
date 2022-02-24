from django.urls import path
from complaints import views

urlpatterns = [
    path('create-report/<slug:username>/<slug:unit_slug>/', views.create_a_report, name='create-report'),
    path('reports/building/<slug:building_slug>/', views.view_reports, name='reports'),
    path('reports/update-view/<slug:building_slug>/<slug:unit_slug>/<slug:report_code>/', views.update_reports, name='view-update-reports'),
    path('create-complaint/<slug:building_slug>/', views.create_complaint, name='create-complaint'),
    path('<slug:building_slug>/coplaints/', views.building_complaints, name='building-complaints'),
]