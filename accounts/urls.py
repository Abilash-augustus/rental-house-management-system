from django.urls import path
from accounts import views

urlpatterns = [
    path('add-new-manager/', views.add_new_manager, name='add-new-manager'),
    path('profile/', views.my_profile, name='profile'),
    path('my-profile-settings/', views.profile_info_update, name='profile-settings'),
    path('view-tenant/<slug:building_slug>/<slug:username>/', views.view_tenant_profile, name='view-tenant'),
    path('add-new-tenant/<slug:building_slug>/', views.add_tenant, name='add-new-tenant'),
    path('update-tenant/<slug:building_slug>/<slug:username>/', views.update_tenant, name='update-tenant'),
    path('tenant_associated_records/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.tenant_associated_records, name='tenant_associated_records'),
]