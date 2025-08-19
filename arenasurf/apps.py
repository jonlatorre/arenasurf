"""" Lanzador de la app"""
from importlib import import_module
from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):

    """Lanzador de la app"""
    name = "arenasurf"

    def ready(self):
        import_module("arenasurf.receivers")

