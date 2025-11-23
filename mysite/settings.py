"""
Django settings for mysite project.
"""

from pathlib import Path
import os
import environ

# -----------------------------------
# BASE DIR
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------
# ENVIRONMENT VARIABLES
# -----------------------------------

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# امنیت
SECRET_KEY = env("SECRET_KEY", default="dummy-secret-key-for-dev")

# برای دولوپمنت
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# اگر API Key نداری این مقدار True باشه
USE_MOCK = env.bool("USE_MOCK", default=True)

# API Key
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")

# -----------------------------------
# APPS
# -----------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'users',
    'chat',

    # Third-party apps
    'rest_framework',
]

# -----------------------------------
# MIDDLEWARE
# -----------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------------
# URL & WSGI
# -----------------------------------

ROOT_URLCONF = 'mysite.urls'
WSGI_APPLICATION = 'mysite.wsgi.application'

# -----------------------------------
# TEMPLATES
# -----------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -----------------------------------
# DATABASE
# -----------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------------------
# PASSWORD VALIDATION
# -----------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------------
# INTERNATIONALIZATION
# -----------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------------
# STATIC FILES
# -----------------------------------

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mysite/static'),
]

# -----------------------------------
# DEFAULT PRIMARY KEY
# -----------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
