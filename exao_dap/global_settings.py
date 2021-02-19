"""
Django settings for exao_dap project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = [
    'dap.xwcl.science',
    'localhost',
    '127.0.0.1',
]

INTERNAL_IPS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'exao_dap.registrar',
    # 'exao_dap.undertaker',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'social_django',
    'django_extensions',
    'django_filters',
    'rest_framework',
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'exao_dap.urls'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'exao_dap' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'exao_dap.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATICFILES_DIRS = [
    BASE_DIR / "exao_dap" / "static",
]

STATIC_URL = '/static/'

AUTHENTICATION_BACKENDS = (
    'exao_dap.cyverse.CyVerseOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# LOGIN_URL = '/accounts/login/'
LOGIN_URL = '/login/cyverse-oauth2/'
LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_CYVERSE_OAUTH2_KEY = os.environ.get('DAP_SOCIAL_AUTH_CYVERSE_OAUTH2_KEY')
SOCIAL_AUTH_CYVERSE_OAUTH2_SECRET = os.environ.get('DAP_SOCIAL_AUTH_CYVERSE_OAUTH2_SECRET')
IRODS_URL = os.environ.get('DAP_IRODS_URL', 'irods://data.cyverse.org/iplant/home/exao_dap')
REGISTRAR_IGNORED_FILES = set(['.DS_Store'])
Q_CLUSTER = {
    'name': 'exao_dap',
    'orm': 'default',
}

DEBUG = os.environ.get('DAP_DEBUG') is not None

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    # Django Debug Toolbar
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}
