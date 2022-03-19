import os

import dj_database_url
import django_heroku
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = str(os.getenv('DJANGO_SECRET_KEY'))
DEBUG = True

# Authentication handler for django/allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrmsysytem.herokuapp.com','.ngrok.io']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'django.contrib.sites',

    # installed apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'cloudinary_storage',
    'crispy_forms',
    'django_summernote',
    'django_filters',

    'accounts.apps.AccountsConfig',
    'rental_property',
    'utilities_and_rent.apps.UtilitiesAndRentConfig',
    'core',
    'complaints',
    'work_order',
]

SITE_ID = 1
AUTH_USER_MODEL = 'accounts.User'

CSRF_TRUSTED_ORIGINS = ['https://ea66-154-122-7-113.ngrok.io',]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STRIPE_PUBLISHABLE_KEY = str(os.getenv('STRIPE_PUBLISHABLE_KEY'))
STRIPE_SECRET_KEY = str(os.getenv('STRIPE_SECRET_KEY'))
    
#handle staticfiles
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rental_property.context_processors.my_managed_buildings',
                'complaints.context_processors.get_contacts',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600)


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

#sendgrig email settings for notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org' #'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@sandboxbdd5463522f84dc9bb8a887714075ada.mailgun.org'#'apikey'
EMAIL_HOST_PASSWORD =  'd94e94834d566c1284aa110ccce96e37-90346a2d-09e3ab9c' # os.environ.get('SENDGRID_EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'Rental House Management System <bravinshumwe@gmail.com>'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
COLLECTSTATIC = 1

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

#cloudinary storage : handling imaeges in deployment

if DEBUG == False:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': 'hqrwhofew',
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'



# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#django-allauth settings
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =2
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400 #1 day

ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/' 
LOGIN_REDIRECT_URL = '/accounts/profile/'

# Heroku settings
django_heroku.settings(locals())
options = DATABASES['default'].get('OPTIONS', {})
options.pop('sslmode', None)


SUMMERNOTE_THEME = 'bs4'
