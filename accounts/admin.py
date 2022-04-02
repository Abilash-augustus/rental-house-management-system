from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from accounts.models import Managers, Profile, Tenants, RelatedRecords

User = get_user_model()

@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Extended',
            {
                'fields': (
                    'avatar', 'is_verified', 'is_tenant', 'is_manager',
                ),
            },
        ),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'county', 'country', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['user', 'phone']

@admin.register(Managers)
class ManagersAdmin(admin.ModelAdmin):
    list_display = ['associated_account', 'fullname', 'status', 'active_phone_number', 'whatsapp_number', 'created', 'updated']
    list_filter = ['status', 'created']
    search_fields = ['user', ]
    
class RelatedRecordsAdmin(admin.StackedInline):
    model = RelatedRecords
    extra = 0
    
@admin.register(Tenants)
class TenantsAdmin(admin.ModelAdmin):
    list_display = ['associated_account', 'created', 'active_phone_number', 'updated']
    list_filter = ['created',]
    search_fields = ['user',]
    inlines = [RelatedRecordsAdmin,]

"""@admin.register(UserNotifications)
class UserNotificationsAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'message']"""