#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from src.log_analyzer import LogAnalyzer

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
