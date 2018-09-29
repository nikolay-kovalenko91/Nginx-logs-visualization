import logging
from datetime import datetime
from os import listdir
from os.path import join, isfile
from typing import Generator


def get_files_paths_of_dir(dir_name: str) -> Generator[str, None, None]:
    for relative_path in listdir(dir_name):
        full_path = join(dir_name, relative_path)
        if isfile(full_path):
            yield full_path


def parse_date_from_string(date_string: str, format_string: str, file_path=None) -> datetime:
    try:
        return datetime.strptime(date_string, format_string)
    except ValueError:
        msg_tail = ' for file {}'.format(file_path) if file_path else ''
        msg = 'Wrong datetime format {}{}. Expected {}'.format(date_string, msg_tail, format_string)
        logging.error(msg)
