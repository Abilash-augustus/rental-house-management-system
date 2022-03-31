from django.apps import AppConfig

import os

class UtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utils'
    verbose_name = 'Rent and Utilities Tracking'
    
    def ready(self):
        from utils import jobs
        if os.environ.get('RUN_MAIN', None) != 'true':
            jobs.start()