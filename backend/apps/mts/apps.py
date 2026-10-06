from django.apps import AppConfig

class MtsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mts'

    def ready(self):
        import apps.mts.signals
