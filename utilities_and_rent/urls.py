from django.urls import path
from utilities_and_rent import views

urlpatterns = [
    path('my-rent/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_rent_details, name='my-rent'),
    path('submit-rent-pay-info/<slug:building_slug>/<slug:unit_slug>/<slug:rent_code>/<slug:username>/', views.submit_payment_record, name='pay-info'),
]