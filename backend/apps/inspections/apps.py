from django.apps import AppConfig

class InspectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inspections'

    def ready(self):
        import apps.inspections.signals
