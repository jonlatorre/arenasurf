"""Clase para configurar webanalytics"""
from pinax.webanalytics.apps import AppConfig as BaseAppConfig


class WebanalyticsConfig(BaseAppConfig):
    """Configuración de la aplicación webanalytics."""
    name = "pinax.webanalytics"
    label = "pinax_webanalytics"  # Cambiado el guión por guión bajo
    verbose_name = "Pinax Web Analytics"
