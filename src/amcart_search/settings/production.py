from .base import *


LOG_DIR = os.environ.get('DASHBOARD_LOG_DIR', "")
LOG_LEVEL = 'DEBUG'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '\n%(levelname)s %(asctime)s [%(pathname)s:%(lineno)s] '
                      '%(message)s'
        },
        'simple': {
            'format': '\n%(levelname)s %(message)s'
        },
    },
    'handlers': {
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'filters': ['require_debug_false'],
        #     'class': 'django.utils.log.AdminEmailHandler'
        # },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'all_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'all.log'),
            'maxBytes': 1048576,
            'backupCount': 99,
            'formatter': 'verbose',
        },
        # 'django_log': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(LOG_DIR, 'django.log'),
        #     'maxBytes': 1048576,
        #     'backupCount': 99,
        #     'formatter': 'verbose',
        # },
        # 'django_request_log': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(LOG_DIR, 'django_request.log'),
        #     'maxBytes': 1048576,
        #     'backupCount': 99,
        #     'formatter': 'verbose',
        # },
        # 'django_elasticsearch_dsl_drf_log': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(LOG_DIR, 'debug_tool_bar.log'),
        #     'maxBytes': 1048576,
        #     'backupCount': 99,
        #     'formatter': 'verbose',
        # },
    },
    'loggers': {
        # 'django.request': {
        #     'handlers': ['django_request_log'],
        #     'level': 'INFO',
        #     'propagate': True,
        # },
        # 'django': {
        #     'handlers': ['django_log'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        '': {
            'handlers': ['all_log'],
            'level': 'INFO',
            'propagate': False,
        },
        # 'django_elasticsearch_dsl_drf': {
        #     'handlers': ['django_request_log', 'django_elasticsearch_dsl_drf_log'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # }
    },
}

