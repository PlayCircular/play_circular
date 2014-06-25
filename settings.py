# coding=utf-8

# Copyright (C) 2014 by Víctor Romero <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

import os
import sys
gettext = lambda s: s

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG  # False
THUMBNAIL_DEBUG = DEBUG  # False
DATE_INPUT_FORMATS = ('%d/%m/%Y','%Y-%m-%d')

ADMINS = ()

MANAGERS = ADMINS

ALLOWED_HOSTS = []

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'
SITE_ID = 1


DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': '',                      # Or path to database file if using sqlite3.
		'USER': '',                      # Not used with sqlite3.
		'PASSWORD': '',                  # Not used with sqlite3.
		'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
		'PORT': ''
		}
}


LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

LANGUAGES = (
	('es', gettext('Spanish')),
	('ca', gettext('Catalan')),
	('en', gettext('English')),
	('fr', gettext('French')),
)

USE_THOUSAND_SEPARATOR = True
USE_I18N = True
USE_L10N = False
DECIMAL_SEPARATOR = '.'
USE_TZ = True



SITE_ROOT = os.path.join(PROJECT_ROOT, 'site')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_ROOT = 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_ROOT = 'static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(SITE_ROOT, 'static_media'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.gzip.GZipMiddleware',
	#idiomas
	'localeurl.middleware.LocaleURLMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'middleware.variables.globales',
)

TEMPLATE_CONTEXT_PROCESSORS =(
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.contrib.messages.context_processors.messages',
	'django.core.context_processors.request',
	'django.core.context_processors.i18n',
	# django-allaut
	"django.core.context_processors.request",
	# allauth specific context processors
	"allauth.account.context_processors.account",
	"allauth.socialaccount.context_processors.socialaccount",
	
)


AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
	"allauth.account.auth_backends.AuthenticationBackend",
)



if DEBUG:
	TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)

#idiomas localeurl
REDIRECT_LOCALE_INDEPENDENT_PATHS = False
PREFIX_DEFAULT_LANGUAGE = True
		

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(SITE_ROOT, 'templates'),
)

INSTALLED_APPS = (
	# Debe ir al inicio
	'localeurl',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.humanize',
	'django.contrib.sitemaps',
	'south',
	'registration',
	'sorl.thumbnail',
	'mptt',
	'django_mptt_admin',
	'metatags',
	'usuarios',
	'portada',
	'grupos',
	'configuracion',
	'economia',
	'actividades',
	'paginas',
	'ces',
	'utilidades',
	'twitter',
	'taggit',
	'qsstats',  
	'rosetta',
	'datatrans',
	'tinymce',
	'middleware',
	'allauth',
	'allauth.account',
	'allauth.socialaccount',
)

ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/usuarios/visita/"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/usuarios/visita/"
LOGIN_REDIRECT_URL = '/usuarios/visita/'
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = u'mandatory'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_COOKIE_AGE = 1814400 #3 semanas

SOUTH_MIGRATION_MODULES = {
	'taggit': 'taggit.south_migrations',
}


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


# Configuración tiny_mce 4
TINYMCE_JS_URL = os.path.join(STATIC_URL, "js/tinymce/tinymce.min.js")
TINYMCE_JS_ROOT = os.path.join(STATIC_URL, "js/tinymce")
TINYMCE_DEFAULT_CONFIG = {'theme': "simple", 'relative_urls': False}
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False
TINYMCE_DEFAULT_CONFIG = {
	'plugins': ["advlist autolink lists link image charmap hr pagebreak",
			 "searchreplace code fullscreen media nonbreaking",
			  "table contextmenu directionality textcolor textcolor"],
	'theme': "modern",
	'menubar': False,
	'toolbar_items_size': 'small',
	'toolbar1': "undo redo | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | hr removeformat | link unlink image media| forecolor backcolor | table | fullscreen | searchreplace| code",
	'width': 850,
	'height': 500,
	'theme_advanced_toolbar_align' : "left",
}


AUTH_PROFILE_MODULE = 'usuarios.Perfil'
handler404 = 'utilidades.views.error_404'
handler500 = 'utilidades.views.error_500'


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587

#Para las imagenes 2.5 megas x default
FILE_UPLOAD_HANDLERS = (
	"django.core.files.uploadhandler.MemoryFileUploadHandler",
	"django.core.files.uploadhandler.TemporaryFileUploadHandler",
)
FILE_UPLOAD_MAX_MEMORY_SIZE = 621440


ROSETTA_MESSAGES_PER_PAGE = 18
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True 
ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = 'es'
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = 'Spanish'
ROSETTA_WSGI_AUTO_RELOAD = True
ROSETTA_UWSGI_AUTO_RELOAD = True
ROSETTA_EXCLUDED_APPLICATIONS = ()
ROSETTA_REQUIRES_AUTH = True
ROSETTA_POFILE_WRAP_WIDTH = 78.

