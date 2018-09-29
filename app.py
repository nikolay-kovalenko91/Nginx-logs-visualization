#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import json
from src.log_analyzer import log_analyzer

default_config_path = './config.json'
default_config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def _get_config(path: str) -> dict:
    try:
        with open(path) as config_file:
            return json.load(config_file)
    except (IOError, OSError):
        raise EnvironmentError("A config file not found")


def main() -> None:
    """
    Gets current config params and run the main logic
    """
    external_config_path = os.environ.get('config', default_config_path)
    external_config = _get_config(external_config_path)
    config = {**default_config, **external_config}

    logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s',
                        filename=config.get('LOG_FILE_PATH'),
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.INFO)

    try:
        log_analyzer(config)
    except KeyboardInterrupt:
        logging.error('"Ctrl + C" was pressed. The script was stopped.')
    except EnvironmentError as e:
        logging.error('{}\nCritical error occured. The script was stopped.'.format(e))
    except:
        logging.exception('Unknown exception occurred.')


if __name__ == '__main__':
    main()
