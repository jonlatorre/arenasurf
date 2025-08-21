"""Configuración Docker con MySQL"""
import os
from pathlib import Path
from django.conf import settings as django_settings

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Importar configuración base
try:
    from .settings import *
except ImportError:
    pass

# Base de datos MySQL para Docker
if os.environ.get('USE_MYSQL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'arenasurf'),
            'USER': os.environ.get('MYSQL_USER', 'arenasurf'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'arenasurf123'),
            'HOST': os.environ.get('MYSQL_HOST', 'db'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# Configuración para producción
DEBUG = os.environ.get('DEBUG', '0').lower() in ['true', '1', 'yes']

if not DEBUG:
    # Configuración de archivos estáticos
    STATIC_ROOT = '/app/static/'
    STATIC_URL = '/static/'
    
    # Configuración de archivos media
    MEDIA_ROOT = '/app/media/'
    MEDIA_URL = '/media/'
    
    # Configuración de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Configuración de sesiones
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Hosts permitidos
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Configuración de archivos estáticos para Docker
STATIC_ROOT = '/app/static/'
STATIC_URL = '/static/'

# Archivos estáticos - usar el storage simple en lugar de ManifestStaticFilesStorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Directorios de archivos estáticos
STATICFILES_DIRS = [
    '/app/static_source/dist',
]

# Media files
MEDIA_ROOT = '/app/media/'
MEDIA_URL = '/media/'

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
