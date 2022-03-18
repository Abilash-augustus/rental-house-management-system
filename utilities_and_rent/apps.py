from django.apps import AppConfig
import os

class UtilitiesAndRentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilities_and_rent'
    verbose_name = 'Rent and Utilities Tracking'
    
    def ready(self):
        from utilities_and_rent import jobs
        if os.environ.get('RUN_MAIN', None) != 'true':
            jobs.start()