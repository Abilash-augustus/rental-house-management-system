from django.urls import path
from accounts import views

urlpatterns = [
    path('add-new-manager/', views.add_new_manager, name='add-new-manager'),
    path('profile/', views.my_profile, name='profile'),
    path('my-profile-settings/', views.profile_info_update, name='profile-settings'),
]