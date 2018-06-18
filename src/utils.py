import logging
import sys


def catch_file_io_exceptions(filename=''):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (IOError, OSError):
                filename_msg = filename if filename else kwargs.get('path', '')
                logging.exception("An error writing/reading file occurred: {}".format(filename_msg))
                sys.exit()

        return wrapper

    return decorator
