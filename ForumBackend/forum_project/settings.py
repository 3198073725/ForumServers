"""
Django settings for forum_project project.
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8$3-9*i%vr$0xkzs+6)3y=5%a!x9s=4!hs0+g2kw_4b@&r3&$f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方应用
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    # 缓存相关
    'django_redis',
    # 自定义应用
    'users',
    'boards',
    'posts',
    'comments',
    'notifications',
    'reports',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS中间件，必须放在最前面
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'forum_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'forum_project.wsgi.application'
ASGI_APPLICATION = 'forum_project.asgi.application'  # 添加ASGI应用配置

# Channels配置
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database
# 使用MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'forum_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# SQLite配置示例
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# 缓存配置
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# 原Redis缓存配置（注释掉）
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "PARSER_CLASS": "redis.connection.HiredisParser",
#             "CONNECTION_POOL_KWARGS": {"max_connections": 100},
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#         }
#     }
# }

# 缓存超时设置（单位：秒）
CACHE_TTL = {
    'home_posts': 60 * 5,  # 首页帖子缓存5分钟
    'board_posts': 60 * 3,  # 板块帖子缓存3分钟
    'post_detail': 60 * 10,  # 帖子详情缓存10分钟
    'user_profile': 60 * 30,  # 用户资料缓存30分钟
}

# 会话缓存
SESSION_ENGINE = "django.contrib.sessions.backends.db"
# SESSION_CACHE_ALIAS = "default"  # 注释掉，因为不再使用缓存作为会话存储

# Password validation
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
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 普通QQ邮箱的SMTP服务器
EMAIL_PORT = 465  # SSL加密端口
EMAIL_USE_SSL = True  # 启用SSL加密
EMAIL_HOST_USER = '3198073725@qq.com'
EMAIL_HOST_PASSWORD = 'fluqgjmedlnedeii'  # 必须使用授权码！
DEFAULT_FROM_EMAIL = 'Forum <3198073725@qq.com>'

# 验证码设置
VERIFICATION_CODE_EXPIRE_MINUTES = 15  # 验证码过期时间（分钟）

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# 自定义认证后端
AUTHENTICATION_BACKENDS = [
    'users.auth.CustomAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': 'forum_project.utils.custom_exception_handler',
}

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:5173',  # Vite 默认开发服务器端口
    'http://127.0.0.1:5173',
]
CORS_ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
