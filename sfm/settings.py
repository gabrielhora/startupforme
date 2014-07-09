# -*- coding: utf-8 -*-

# Django settings for sfm project.

import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ('127.0.0.1',)

ADMINS = (
    ('Gabriel Hora', 'gabrielhora@gmail.com'),
)

MANAGERS = ADMINS

LOGIN_URL = '/login'

INVALID_STARTUP_NAMES = (
    'startups', 'startup', 'login', 'logout', 'criar', 'registrar', 'signin', 'signout', 'signup',
    'vagas', 'pessoas', 'pessoa', 'busca', 'search', 'admin', 'admins', 'sobre', 'about', 'quem-somos', 'who',
    'mudar-senha', 'recuperar-senha', 'editar', 'excluir', 'subscribe', 'unsubscribe', 'assinar', 'desassinar',
)

RECORDS_PER_PAGE = 10

# Linkedin

LINKEDIN_KEY = ''
LINKEDIN_SECRET = ''
LINKEDIN_RETURN_URL = 'http://localhost:8000/pessoas/autorizado'

# Twitter
TWITTER_MAX_LENGTH = 100
TWITTER_OAUTH_TOKEN = ''
TWITTER_OAUTH_SECRET = ''
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

# Email
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
SERVER_EMAIL = ''
EMAIL_SUBJECT_PREFIX = ''
DEFAULT_FROM_EMAIL = ''

# Mandrill
MANDRILL_API_KEY = ''

# MailChimp
MAILCHIMP_APIKEY = ''
MAILCHIMP_DATACENTER = ''
MAILCHIMP_LISTID = ''


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'startupforme',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
        'ATOMIC_REQUESTS': 'True', # one transaction per request
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, '../media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = 'http://localhost:8000/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, '../static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, '../media'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '123ksdjlkj2lkj31l2k3j12lk3gkj1fgkj12gh3k1j2g31j2hgk'

# Custom template context processors
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'sfm.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sfm.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'south',
    'taggit',
    'imagekit',
    'front',
    'django.contrib.admin',
    'debug_toolbar',
    'storages',
    'djrill',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
