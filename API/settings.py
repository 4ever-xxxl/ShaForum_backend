"""
Django settings for API project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import datetime
import os.path
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-#f*1uytq7$&8+5o%qs@5)3&3=(q_os*o)gq+!kd3kt=)t5hky3"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"] # 部署时改为本地IP

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",  # 跨域

    "users.apps.UsersConfig",  # 用户
    "comments.apps.CommentsConfig",  # 评论
    'posts.apps.PostsConfig',  # 帖子

    "rest_framework.authtoken",  # token
    "taggit",  # 标签
    "mptt",  # 多级评论
    "notifications",  # 通知
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # 跨域
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "API.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = "API.wsgi.application"

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ShaForum',
        'USER': 'shaforum',
        'PASSWORD': 'shaforum',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # jwt
    ],
}

# 设置登录检查的URL
LOGIN_URL = '/api/login/'

# 设置邮箱
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_HOST_USER = 'lx10ng@qq.com'
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = 'lx10ng@qq.com'

# JWT settings
SIMPLE_JWT = {
    'USER_ID_FIELD': 'userID',
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=1),
}

# 上传文件的路径
MEDIA_URL = '/api/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 上传文件的大小限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# 上传文件的类型限制
FILE_UPLOAD_ALLOWED_TYPES = [
    'image/jpeg',
    'image/png',
    'image/jpg',
    'image/gif',
    'image/bmp',
    'image/webp',
    'video/mp4',
    'video/ogg',
    'video/webm',
    'audio/mpeg',
    'audio/ogg',
    'audio/wav',
    'audio/webm',
    'application/pdf',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
]


# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 定义输出格式
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s'
        },
    },
    'filters': {
        # 过滤器
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'skip_autoreload': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: not record.name.startswith('django.utils.autoreload'),
        },
    },
    'handlers': {
        # 定义处理器
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',  # 输出到控制台
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'filters': ['skip_autoreload'],
            'class': 'logging.FileHandler',  # 输出到文件
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': [],
            'class': 'django.utils.log.AdminEmailHandler',  # 发送邮件
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


# 跨域配置
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    'http://' + ALLOWED_HOSTS[0] + ':8000',
]
CORS_ALLOW_HEADERS = [
    'Content-Type',
    'Authorization',  # 添加 Authorization 到允许的请求头字段
]