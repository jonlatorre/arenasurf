from importlib import import_module

from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):

    name = "arenasurf"

    def ready(self):
        import_module("arenasurf.receivers")


class WebanalyticsConfig(BaseAppConfig):
    name = "pinax.webanalytics"
    label = "pinax_webanalytics"  # Cambiado el guión por guión bajo
    verbose_name = "Pinax Web Analytics"
