from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler500

handler500 = 'core.views.custom_system_error_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('rental_property.urls')),
    path('rent-and-utility/', include('utils.urls')),
    path('core/', include('core.urls')),
    path('crm/', include('complaints.urls')),
    path('work_order/', include('work_order.urls')),
    path('reports/', include('reporting.urls')),
    
]
if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "House Rental Management System"
admin.site.site_title = "HRMS"
admin.site.index_title = 'Welcome'