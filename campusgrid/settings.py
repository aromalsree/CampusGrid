"""
Django settings for CampusGrid project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-campusgrid-master-key-2026-production-ready')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # CampusGrid Core App
    'marketplace.apps.MarketplaceConfig',
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

ROOT_URLCONF = 'campusgrid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'marketplace' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'marketplace.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'campusgrid.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'marketplace' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Public uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Protected Media (Digital files delivered only upon verified purchase)
PROTECTED_MEDIA_ROOT = BASE_DIR / 'protected_media'

# Auth URLs
LOGIN_URL = 'marketplace:login'
LOGIN_REDIRECT_URL = 'marketplace:dashboard'
LOGOUT_REDIRECT_URL = 'marketplace:login'

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Messages styling mapping for Tailwind
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'slate',
    messages.INFO: 'slate',
    messages.SUCCESS: 'emerald',
    messages.WARNING: 'amber',
    messages.ERROR: 'rose',
}

# Razorpay Integration Ready Config (Can be populated via env)
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_campusgrid_mock_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'mock_secret_key_for_testing')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
