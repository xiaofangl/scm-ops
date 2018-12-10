#!/usr/bin/env python
# encoding: utf-8
# author: xiaofangliu

import datetime
import logging
import logging.config

import os


def log_init():
    """"""
    BASE_DIR = '/tmp'
    LOG_DIR = os.path.join(BASE_DIR, "logs_ep_tools")
    print('log path is :', LOG_DIR)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # 创建路径

    LOG_FILE = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- '
                          '%(message)s'
            },
            'standard': {
                'format': '%(asctime)s [%(threadName)s:%(thread)d] '
                          '[%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },

            "default": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": os.path.join(LOG_DIR, LOG_FILE),
                'mode': 'w+',
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 20,
                "encoding": "utf8"
            },
        },

        # "loggers": {
        #     "app_name": {
        #         "level": "INFO",
        #         "handlers": ["console"],
        #         "propagate": "no"
        #     }
        # },

        "root": {
            'handlers': ['default'],
            'level': "DEBUG",
            'propagate': False
        }
    }

    logging.config.dictConfig(LOGGING)


# log_init()


def do_something():
    log = logging.getLogger(__file__)
    print("print A")
    log.info("log B")


if __name__ == '__main__':
    log_init()
    do_something()
