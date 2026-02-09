from django.apps import AppConfig


class PlatformUiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.platform_ui'
    verbose_name = '플랫폼 및 AI'

    def ready(self):
        import apps.platform_ui.signals
