"""
Django settings for core project.
For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
#############################
### SUMI - Version 1.5.1 ###
#############################
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from apps.home.utils import *

load_dotenv()  # take environment variables from .env.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', default='S#perS3crEt_007_D@xter_CRX_MCL$2024#')

# Render Deployment Code
DEBUG = False#'RENDER' not in os.environ

ALLOWED_HOSTS = ['192.168.5.202', '192.168.4.126', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = [
    'http://192.168.5.202:9090', 'http://192.168.5.202:9000', 'http://192.168.5.202:*/', 'http://192.168.5.202/',
    'http://192.168.4.126:9090', 'http://192.168.4.126:9000', 'http://192.168.4.126:*/', 'http://192.168.4.126/'
    ]
CSRF_FAILURE_VIEW = 'apps.home.utils.csrf_failure'

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:    
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

TIME_ZONE = 'America/Caracas'

ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets') 
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets') 
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.core.files.storage',
    'whitenoise.runserver_nostatic',
    'documents', 
    'apps.authentication',
    'apps.essays',
    'apps.graphics',
    'apps.home',
    'apps.production',
    'apps.sales',
    'django_filters',
    'simple_history',
    'django_quill',
    'django_cleanup.apps.CleanupConfig',
]

QUILL_CONFIGS = {
    'default':{
        'theme': 'snow',
        'language': 'es-VE',
        'modules': {
            'syntax': True,
            'toolbar': [
                [
                    'bold', 'italic', 'underline', 'strike',
                    {'background': [
                        '#FF2C2C',
                        '#FBC501',
                        '#27E52E',
                        '#1A73E8',
                        '#6f42c1',
                        '#ED4899',

                        '#ff5100',
                        '#f47b48',
                        '#f68c5e',
                        '#fab08b',
                        '#fdd5bf',
                        '#fee8db',
                        
                        '#946037',
                        '#a77a58',
                        '#b18969',
                        '#bc987b',
                        '#c7a990',
                        '#decebf',

                        '#344767',
                        '#7b809a',
                        '#b4b5c4',
                        '#D1D3E0',
                        '#F5F5FF',
                        '',
                    ]},
                    {'color': [
                        '#FF2C2C',
                        '#FBC501',
                        '#27E52E',
                        '#1A73E8',
                        '#6f42c1',
                        '#ED4899',

                        '#ff5100',
                        '#f47b48',
                        '#f68c5e',
                        '#fab08b',
                        '#fdd5bf',
                        '#fee8db',
                        
                        '#946037',
                        '#a77a58',
                        '#b18969',
                        '#bc987b',
                        '#c7a990',
                        '#decebf',

                        '#344767',
                        '#7b809a',
                        '#b4b5c4',
                        '#D1D3E0',
                        '#F5F5FF',
                        '',
                    ]},
                    {'align': []},
                ],
                [
                    { 'list': 'ordered'}, 
                    { 'list': 'bullet' }
                ],
                [
                    'image',
                ],
            ],
            'imageResize': {  # open imageResize
                'displaySize': True
            }
        }        
    }
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.IntegrityCheck',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = "core.urls"

TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.cfg_assets_root',
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
  'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'prueba_migrada.sqlite3',
    },
    # '': {
    #     'ENGINE': 'mssql',
    #     'NAME': 'Prueba',
    #     'USER': 'sa',
    #     'PASSWORD': 'saleon21',
    #     'HOST': 'srvsql02',
    #     'PORT': '',
    #     'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server',},
    # },
    # 'test_local': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': 'db.sqlite3',
    # },
    # 'default': {
    #     'ENGINE': 'mssql',
    #     'NAME': 'Prueba',
    #     'USER': 'sa',
    #     'PASSWORD': 'saleon21',
    #     'HOST': 'srvsql02',
    #     'PORT': '',
    #     'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server',},
    # },
    # 'test': {
    #     'ENGINE': 'mssql',
    #     'NAME': 'sumi',
    #     'USER': 'sa',
    #     'PASSWORD': 'saleon21',
    #     'HOST': 'srvsql02',
    #     'PORT': '',
    #     'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server',},
    # },
}
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/


LANGUAGE_CODE = 'es-VE'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
DATA_UPLOAD_MAX_MEMORY_SIZE = None

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media/' 
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    os.path.join(CORE_DIR, 'apps/static'),
    BASE_DIR / 'media'
]

FIXTURE_DIRS = [os.path.join(CORE_DIR, 'apps/fixtures')]

#if not DEBUG:
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "home"  
LOGOUT_REDIRECT_URL = "home"  
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING', #la configuraci�n por efecto es WARNING, DEBUG para mostrar peticiones SQL
        },
    },
}
