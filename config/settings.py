"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-rz1==a=z8!4-5_s9v$5yg=01l^+m(+0ysyk(165lq2wrkmwk1l"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'ckeditor',
    'ckeditor_uploader',
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "hotelbooking",
    "django_dump_die",
    "crispy_forms",
    "crispy_bootstrap4",
    # django all auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_dump_die.middleware.DumpAndDieMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
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
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Set STATIC_ROOT to an absolute path where collectstatic will collect static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CRISPY_TEMPLATE_PACK = "bootstrap4"


# Django ALl Auth settings

SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_REDIRECT = "/"
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)


LOGIN_URL = "/accounts/login/"

JAZZMIN_SETTINGS = {
    "site_title": "Hotel Booking",
    "site_header": "Hotel Booking",
}


# CKEditor Settings
CKEDITOR_UPLOAD_PATH = 'uploads/'