# -*- coding: utf-8 -*-


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(levelname)-4s %(name)-10s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'file': {
            'format': '%(asctime)s %(levelname)-4s %(name)-10s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'console',
        },
        'logs': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'console',
        }
    },
    'loggers': {
        'irc3': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'raw': {
            'handlers': ['logs'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
