from django.urls import path
from work_order import views


urlpatterns = [
    path('hired_personnel/<slug:building_slug>/', views.hired_personnel, name='hired_personnel'),
    path('hired_personnel_details/<slug:building_slug>/<slug:p_code>/', views.hired_personnel_details, name='hired_personnel_details'),
    path('update_hired_personnel/<slug:building_slug>/<slug:p_code>/', views.update_hired_personnel, name='update_hired_personnel'),
    path('work_orders/<slug:building_slug>/', views.work_orders, name='work_orders'),
    path('work_order_details/<slug:building_slug>/<slug:order_code>/', views.work_order_details, name='work_order_details'),
    path('update_work_order_payment/<slug:building_slug>/<slug:order_code>/<slug:t_code>/', views.update_work_order_payment, name='update_work_order_payment'),
    path('work_order_pdf/<slug:building_slug>/<slug:order_code>/', views.work_order_pdf, name='work_order_pdf'),
]