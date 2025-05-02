import os
from pathlib import Path

from django.conf.global_settings import AUTH_USER_MODEL, EMAIL_USE_TLS
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-nvek$+#fx_1&q!dd6^x$6r57xw6@3)*8*n))ge5ob2c41xr54@'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'django.contrib.flatpages',

    # Allauth
    'allauth',
    'allauth.account',

    'board',
    'django_ckeditor_5'
]

SITE_ID = 1


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'allauth.account.middleware.AccountMiddleware',

    'django.middleware.locale.LocaleMiddleware',

]

ROOT_URLCONF = 'Board_project.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'Board_project.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

# Для локализации на русский
USE_I18N = True
USE_L10N = True  # Локальное форматирование дат

USE_TZ = True


STATIC_URL = 'static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# работает только с VPN
load_dotenv()

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Обычная авторизация
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth
]

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Обязательно подтверждать email
LOGIN_REDIRECT_URL = '/'  # Куда отправлять после входа

AUTH_USER_MODEL = 'board.User'  # Кастомная модель юзера

LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/login/'  # Куда перенаправлять после выхода
LOGIN_REDIRECT_URL = '/profile/'  # Куда перенаправлять после входа

SITE_DOMAIN = "127.0.0.1:8000"

SITE_URL = 'http://127.0.0.1:8000'

# Настройки Django для генерации ссылок
DEFAULT_DOMAIN = SITE_DOMAIN
EMAIL_USE_TLS = True


# CKEditor 5
customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]


CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'pdf', 'png', 'webp']  # optional

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "ru",
        "toolbar": {
            "items": [
                "|", "heading",
                "|", "outdent", "indent",
                "|", "bold", "italic", "link", "underline", "strikethrough", "code", "subscript", "superscript",
                "highlight", "undo", "redo",
                "|", "codeBlock", "insertImage", "bulletedList", "numberedList", "todoList",
                "|", "blockQuote",
                "|", "fontSize", "fontFamily", "fontColor", "fontBackgroundColor", "mediaEmbed", "removeFormat",
                "insertTable"
            ],
            "shouldNotGroupWhenFull": True
        },
        "image": {
            "toolbar": [
                "|", "imageUpload", "imageTextAlternative",
                "|", "imageStyle:alignLeft", "imageStyle:alignRight", "imageStyle:alignCenter", "imageStyle:side",
                "|", "toggleImageCaption"
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter"
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties"
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette
            }
        },
        "list": {
            "properties": {
                "styles": True,
                "startIndex": True,
                "reversed": True
            }
        },
    }
}
CKEDITOR_5_MAX_FILE_SIZE = 1  # Максимальный размер загружаемого изображения - 1 Мб
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "any"
