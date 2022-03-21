from django.apps import AppConfig
import os


class UtilitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilities'
    verbose_name = 'Rent and Utilities Tracking'
    
    def ready(self):
        from utilities import jobs
        if os.environ.get('RUN_MAIN', None) != 'true':
            jobs.start()