"""
Django settings for ManageMachine project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_h7d767f8gaalyksue+%qmlo#htup&(m*jq6v$n+kcf01ri%1n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup',
    # 'django-pandas',
    'ManageMachine',
    'MainMenu',
    'ReadCsv',
    'OrderDetail',
    'Schedule',
    'MachineInfo',
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

ROOT_URLCONF = 'ManageMachine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ManageMachine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'UTC'   # 'Asia/Tokyo'にするとDB登録時の時刻がおかしくなる

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'ManageMachine/static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# インラインフレームを許可するための設定
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 一度に送れるフォームフィールドの数
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

# サイト名
SITE_NAME = '印刷機予約システム'

# アップロードファイル格納場所設定
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CSVファイル保存数
CSV_FILE_REMAIN = 3

# 曜日名
WEEKDAY_NAME = ('月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日')

# 工数予測CSVカラム名
CSV_COL_NAME = ('受注番号', '号機名', '正味作業時間', '付帯作業時間', '合計作業時間')

# Plotlyで使用するカラム名
PLOTLY_COL_NAME = ('Task', 'Start', 'Finish')
ORDER_COL_NAME = 'Order'
TIME_COL_NAME = 'Time'

# 一括予約リストファイル
REGIST_LIST_FILE = 'regist_list.txt'
REGIST_LIST_PATH = os.path.join(MEDIA_ROOT, REGIST_LIST_FILE)
