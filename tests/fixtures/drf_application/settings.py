from distutils.version import StrictVersion
from rest_framework import VERSION as REST_FRAMEWORK_VERSION

REST_FRAMEWORK_V3 = StrictVersion(REST_FRAMEWORK_VERSION) > StrictVersion('3.0.0')

SECRET_KEY = "SECRET KEY"

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'testapp',
]

MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.middleware.csrf.CsrfViewMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware')

# Django replaces this, but it still wants it. *shrugs*
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'urls'

DEBUG = True

