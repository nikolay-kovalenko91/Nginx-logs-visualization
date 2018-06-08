#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from src.log_analyzer import LogAnalyzer

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';

default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def _get_config(path):
    try:
        with open(path) as config_file:
            return json.load(config_file)
    except (IOError, OSError):
        # TODO: Integrate logging library
        print("An error opening / processing config file occurred")


def main():
    # TODO: Check a task for appropriate config behaviour
    config_path = os.environ.get('config')
    config = default_config
    if config_path:
        config = _get_config(config_path)
    LogAnalyzer(config=config).main()


if __name__ == '__main__':
    main()
