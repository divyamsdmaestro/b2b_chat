from pathlib import Path

import environ
from corsheaders.defaults import default_headers
from django.db import DEFAULT_DB_ALIAS

# Directory Initialization
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# Environment Helpers
# ------------------------------------------------------------------------------
env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# Timezone & Localization
# ------------------------------------------------------------------------------
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "daphne",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
]

THIRD_PARTY_APPS = [
    # architecture
    "django_celery_beat",
    # cmd functions
    "django_extensions",
    # rest api
    "rest_framework",
    "rest_framework.authtoken",
    # cors & request
    "corsheaders",
    "django_user_agents",
    # azure helpers
    "storages",
    # model helpers
    "phonenumber_field",
    # sendgrid email
    "anymail",
]

CUSTOM_APPS = [
    "apps.common",
    "apps.chat",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

# IDP Communication Configuration
# ------------------------------------------------------------------------------
IDP_B2B_TENANT_ID = env.int("IDP_B2B_TENANT_ID")
IDP_ADMIN_EMAIL = env.str("IDP_ADMIN_EMAIL")
IDP_ADMIN_PASSWORD = env.str("IDP_ADMIN_PASSWORD")
IDP_ADMIN_TENANCY_NAME = env.str("IDP_ADMIN_TENANCY_NAME")
IDP_CONFIG = {
    "host": env.str("IDP_SERVICE_HOST", default="=https://iamserver.azurewebsites.net"),
    "authenticate_url": env.str("IDP_AUTHENTICATE_URL", default=""),
    "get_current_login_info": env.str("IDP_GET_CURRENT_LOGIN_INFO", default=""),
    "get_user_info_by_ids": env.str("IDP_GET_USER_INFO_BY_IDS", default=""),
    "get_tenant_info_by_id": env.str("IDP_TENANT_BY_ID_URL", default=""),
    "b2b_id": env.str("IDP_B2B_TENANT_ID", default=""),
    "b2b_name": env.str("IDP_ADMIN_TENANCY_NAME", default=""),
}

# DATABASES & ROUTER Settings for multi-tenant applications
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {
    # default database user and credentials | others are added on runtime
    DEFAULT_DB_ALIAS: {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB", default=""),
        "USER": env.str("POSTGRES_USER", default=""),
        "PASSWORD": env.str("POSTGRES_PASSWORD", default=""),
        "HOST": env.str("POSTGRES_HOST", default=""),
        "PORT": env.str("POSTGRES_PORT", default=""),
        "ATOMIC_REQUESTS": True,
    },
}

# ADMIN
# ------------------------------------------------------------------------------
ADMIN_URL = env.str("DJANGO_ADMIN_URL", default="django-admin/")
ADMINS = [("""Jeevan""", "jeevan.jeevu94@gmail.com")]
MANAGERS = ADMINS
CSRF_TRUSTED_ORIGINS = ["https://*.techademyb2b.site/", "https://*.127.0.0.1"]

# App Super Admin
# ------------------------------------------------------------------------------
APP_SUPER_ADMIN = {
    "email": env.str("APP_SUPER_ADMIN_EMAIL", default="superadmin@app.com"),
    "password": env.str("APP_SUPER_ADMIN_PASSWORD", default="superadmin@app.com"),
    "first_name": env.str("APP_SUPER_ADMIN_NAME", default="Super Admin"),
}

# MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "apps.common.middlewares.DisableCSRFMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.common.middlewares.AppAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

# URLS
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"
APPEND_SLASH = True

# CHANNELS / WEBSOCKETS
# ------------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env.str("REDIS_URL")],
        },
    },
}

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# STATIC
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATICFILES_DIRS = [str(APPS_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
AZURE_ACCOUNT_KEY = env("DJANGO_AZURE_ACCOUNT_KEY")
AZURE_ACCOUNT_NAME = env("DJANGO_AZURE_ACCOUNT_NAME")
AZURE_CONTAINER = env("DJANGO_AZURE_CONTAINER_NAME")
if DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "apps.common.storages.MediaRootAzureStorage",
        },
    }
MEDIA_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/media/"
MEDIA_ROOT = str(APPS_DIR / "media")
TEMP_ROOT = f"{MEDIA_ROOT}/temp"

# AUTHENTICATION
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = "chat.User"  # custom app user model

# PASSWORDS
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# SECURITY
# ------------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# CORS
# ------------------------------------------------------------------------------
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    *default_headers,
    "Token",
    "Issuer-Url",
    "Issuer",
]

# Api & Rest Framework
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.chat.auth_backends.AppIDPTokenAuthBackend",
    ],
}

# App Switches
# ------------------------------------------------------------------------------
APP_SWITCHES = {
    # should emails be sent or not
    "SEND_EMAILS": env.bool("SWITCH_SEND_EMAILS", default=True),
    # performance debugging mode
    "DB_DEVELOPER_LOG": env.bool("SWITCH_DB_DEVELOPER_LOG", default=False),
    # periodic tasks debugging mode | call tasks every one minute
    "CELERY_BEAT_DEBUG_MODE": env.bool("SWITCH_CELERY_BEAT_DEBUG_MODE", default=False),
    # supervisor/celery is not running | only django is running, not even cache
    "CELERY_WORKER_DEBUG_MODE": env.bool("SWITCH_CELERY_WORKER_DEBUG_MODE", default=False),
    # redis container is running or not? | use in-memory cache
    "REDIS_CACHE_DEBUG_MODE": env.bool("SWITCH_REDIS_CACHE_DEBUG_MODE", default=False),
}

# CACHES
# ------------------------------------------------------------------------------
if not APP_SWITCHES["REDIS_CACHE_DEBUG_MODE"]:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env.str("CELERY_BROKER_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": False,
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
EMAIL_SENDER_ADDRESS = env.str("EMAIL_SENDER_ADDRESS", default="noreply@example.com")
EMAIL_SENDER_NAME = env.str("EMAIL_SENDER_NAME", default="App")
EMAIL_SUBJECT_PREFIX = env.str("DJANGO_EMAIL_SUBJECT_PREFIX", default=f"[{EMAIL_SENDER_NAME}]")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = f"'{EMAIL_SENDER_NAME}' <{EMAIL_SENDER_ADDRESS}>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 5
ANYMAIL = {
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),
    "SENDGRID_API_URL": env("SENDGRID_API_URL", default="https://api.sendgrid.com/v3/"),
}

# Default Overrides
# ------------------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = None  # prevents some idiotic upload bug | 500 => 400

# App Configurations
# ------------------------------------------------------------------------------
APP_DATE_FORMAT = "%Y-%m-%d"
APP_TIME_FORMAT = "%H:%M:%S"
APP_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Azure & Services
# ------------------------------------------------------------------------------
AZURE_MS_AAD_TENANT_DOMAIN = env.str("AZURE_MS_AAD_TENANT_DOMAIN", default="")
AZURE_MS_ARM_RESOURCE = env.str("AZURE_MS_ARM_RESOURCE", default="")
AZURE_MS_SUBSCRIPTION_ID = env.str("AZURE_MS_SUBSCRIPTION_ID", default="")
AZURE_MS_STORAGE_ACCOUNT_CONNECTION = env.str("AZURE_MS_STORAGE_ACCOUNT_CONNECTION", default="")
AZURE_MS_RESOURCE_GROUP = env.str("AZURE_MS_RESOURCE_GROUP", default="")
AZURE_MS_ACCOUNT_NAME = env.str("AZURE_MS_ACCOUNT_NAME", default="")
AZURE_CLIENT_SECRET = env.str("AZURE_CLIENT_SECRET", default="")
AZURE_TENANT_ID = env.str("AZURE_TENANT_ID", default="")
AZURE_CLIENT_ID = env.str("AZURE_CLIENT_ID", default="")

# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s - %(message)s",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": [],
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "DEBUG",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}
