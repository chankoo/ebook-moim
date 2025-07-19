import pymysql

pymysql.install_as_MySQLdb()

from os.path import basename, dirname, join, normpath
from pathlib import Path

from sys import path


# 경로 설정
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
path.append(PROJECT_ROOT)
DJANGO_ROOT = str(Path(__file__).resolve().parent.parent)
SITE_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)
# 경로 설정 끝

# DB 설정
ATOMIC_REQUESTS = True
# DB 설정 끝

# Django 기본 설정
TIME_ZONE = "Asia/Seoul"

LANGUAGE_CODE = "ko-kr"

SITE_ID = 1

USE_I18N = True
USE_THOUSAND_SEPARATOR = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Django 기본 설정 끝

# 미디어 파일 설정
# END MEDIA CONFIGURATION

# 정적 파일 설정
STATIC_URL = "/static/"
STATICFILES_DIRS = [join(DJANGO_ROOT, "static")]
STATIC_ROOT = join(DJANGO_ROOT, "staticfiles")
# 정적 파일 설정 끝

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "--4n2@df2atc^c5t0f-rbm@huex)32*p6&@@i=j4ln96)xkld+"

# 템플릿 설정
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            normpath(join(DJANGO_ROOT, "templates")),
        ],
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
# 템플릿 설정 끝


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "apps.book",
    "apps.log",
    "apps.users",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ebookFinder.urls"

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


SERVICE_DOMAIN = ""


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Instagram OAuth2 settings
INSTAGRAM_CLIENT_ID = "1950225982466334"
INSTAGRAM_CLIENT_SECRET = "YOUR_INSTAGRAM_CLIENT_SECRET"
INSTAGRAM_REDIRECT_URI = "YOUR_INSTAGRAM_REDIRECT_URI"

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}
