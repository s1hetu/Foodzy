import os


def get_logging_configs(base_dir, debug):
    return {
        'version': 1,
        'disable_existing_loggers': False if debug else True,
        'formatters': {
            'verbose': {
                # exact format is not important, this is the minimum information
                'format': '%(levelname)s %(asctime)s %(module)s %(lineno)s %(message)s',
                # 'style': '{',
            },
            'simple': {
                # exact format is not important, this is the minimum information
                'format': '%(levelname)s %(asctime)s %(funcName)s %(module)s %(lineno)s %(message)s',
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue'
            },
            'filter_info_level': {
                '()': 'FDA.logging_filter.FilterLevels',
                'filter_levels': [
                    "INFO"
                ]
            },
            'filter_error_level': {
                '()': 'FDA.logging_filter.FilterLevels',
                'filter_levels': [
                    "ERROR"
                    "ERROR"
                ]
            },
            'filter_warning_level': {
                '()': 'FDA.logging_filter.FilterLevels',
                'filter_levels': [
                    "WARNING"
                ]
            }
    
        },
        'handlers': {
            # console logs to stderr
            'console': {
                'level': 'DEBUG' if debug else 'INFO',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
    
            'debug': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(base_dir, 'log/debug.log'),
                'formatter': 'verbose',
                'filters': ['require_debug_true'],
            },
            'info': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(base_dir, 'log/info.log'),
                'filters': ['filter_info_level'],
                'maxBytes': 300 * 1024 * 1024,  # 300M Size,
                'backupCount': 10,
                'formatter': 'verbose',
                'encoding': 'utf-8'
            },
            'warning': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(base_dir, 'log/warning.log'),
                'maxBytes': 1024 * 1024 * 50,  # 50M Size,
                'filters': ['filter_warning_level'],
                'backupCount': 5,
                'formatter': 'verbose',
                'encoding': 'utf-8'
            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': os.path.join(base_dir, 'log/error.log'),
                'formatter': 'simple',
            },
        },
        'loggers': {
            # default for all undefined Python modules
            '': {
                'level': 'INFO',
                'handlers': ['console', 'info', 'debug', 'warning', 'error'],
                'propagate': False,
            },
            'info_log': {
                'level': 'INFO',
                'handlers': ['warning', 'info'],
                'propagate': False,
            },
            'debug_log': {
                'level': 'DEBUG',
                'handlers': ['debug'],
                'propagate': False,
            },
        },
    }