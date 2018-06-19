import re
import gzip
import sys
import logging

from os.path import isfile, join
from os import listdir
from datetime import datetime
from typing import List, Generator, TextIO, Iterable

from src.exceptions import ReportExists, NoLogFilesFound
from src.utils import catch_file_io_exceptions


# Namedtuple is immutable, so I can't set up 'content' param.
# The best idea is to use 'pip install recordtype' later
class LogFile:
    def __init__(self, date: datetime, path: str, file_extension: str, content: List[str]=None):
        self.date = date
        self.path = path
        self.content = content
        self.file_extension = file_extension

    def set_content(self, content):
        self.content = content

    def __repr__(self):
        return self.date.strftime('%m/%d/%Y')


class LogFilesHandler:
    """
    Finds the last dated Nginx log, reads its content, and returns it with another
    log file info.
    """
    _LOG_DATETIME_NAME_FORMAT = '%Y%m%d'

    def __init__(self, log_dir, report_dir):
        self._log_dir = log_dir
        self._report_dir = report_dir

    def _get_files_paths_of_dir(self, dir_name: str) -> Generator[str, None, None]:
        for relative_path in listdir(dir_name):
            full_path = join(dir_name, relative_path)
            if isfile(full_path):
                yield full_path

    def _parse_date_from_string(self, date_string: str, format_string: str, file_path=None) -> datetime:
        try:
            return datetime.strptime(date_string, format_string)
        except ValueError:
            msg_tail = ' for file {}'.format(file_path) if file_path else ''
            msg = 'Wrong datetime format {}{}. Expected {}'.format(date_string, msg_tail, format_string)
            logging.error(msg)

    def _is_report_exist_for_log(self, log_file_info: LogFile, files_paths: Iterable[str]) -> bool:
        report_name_re = '^{dir}/report-(20\d{{2}}\.\d{{2}}\.\d{{2}})\.html$'.format(dir=self._report_dir)
        for file_path in files_paths:
            matching_values = re.findall(report_name_re, file_path)
            date_string = matching_values[0]
            report_date = self._parse_date_from_string(date_string, '%Y.%m.%d', file_path)
            if log_file_info.date == report_date:
                return True

        return False

    def _get_last_log_path_to_parse(self, dir_name: str, files_paths: Iterable[str]) -> LogFile:
        log_name_re = '^{dir}/nginx-access-ui\.log-(20\d{{6}})\.{{0,1}}(.{{0,2}})$'.format(dir=dir_name)
        log_files = []
        for file_path in files_paths:
            matching_lines = re.findall(log_name_re, file_path)[0]
            date_string, file_extension = matching_lines[0], matching_lines[1]
            date = self._parse_date_from_string(date_string, self._LOG_DATETIME_NAME_FORMAT, file_path)
            log_file = LogFile(
                date=date,
                path=file_path,
                file_extension=file_extension
            )
            log_files.append(log_file)

        log_files.sort(key=lambda log_f: log_f.date)

        if len(log_files) == 0:
            raise NoLogFilesFound

        return log_files.pop()

    def _read_lines(self, file_object: TextIO) -> Generator[str, None, None]:
        while True:
            line = file_object.readline()
            if not line:
                break
            yield line

    @catch_file_io_exceptions()
    def _read_plain_file(self, path: str) -> Generator[str, None, None]:
        with open(path) as file_handler:
            yield from self._read_lines(file_handler)

    @catch_file_io_exceptions()
    def _read_gzip_file(self, path: str) -> Generator[str, None, None]:
        with gzip.open(path, 'rb') as file_handler:
            yield from self._read_lines(file_handler)

    def _read_file(self, path: str, extension: str) -> Generator[str, None, None]:
        extension_vs_handlers = {
            '': self._read_plain_file,
            'gz': self._read_gzip_file
        }
        if extension not in extension_vs_handlers:
            logging.error('Unknown extension of found log file {}'.format(path))
            sys.exit()

        handler = extension_vs_handlers[extension]

        yield from handler(path=path)

    def get_file_to_parse(self) -> LogFile:
        log_files_paths = self._get_files_paths_of_dir(dir_name=self._log_dir)
        last_log_file = self._get_last_log_path_to_parse(dir_name=self._log_dir, files_paths=log_files_paths)

        report_files_paths = self._get_files_paths_of_dir(dir_name=self._report_dir)
        if self._is_report_exist_for_log(log_file_info=last_log_file, files_paths=report_files_paths):
            raise ReportExists

        log_content = self._read_file(path=last_log_file.path, extension=last_log_file.file_extension)
        last_log_file.set_content(log_content)

        return last_log_file
