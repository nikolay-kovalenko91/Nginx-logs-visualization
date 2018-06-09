from os import listdir
from os.path import isfile, join
import re
from datetime import datetime

from src.exceptions import ReportExists, NoLogFilesFound


class LogFilesHandler:
    _LOG_DATETIME_NAME_FORMAT = '%Y%m%d'

    def __init__(self, log_dir, report_dir):
        self._log_dir = log_dir
        self._report_dir = report_dir

    def _get_files_paths_of_dir(self, dir_name):
        for relative_path in listdir(dir_name):
            full_path = join(dir_name, relative_path)
            if isfile(full_path):
                yield full_path

    def _parse_date_from_string(self, date_string, format, file_path=None):
        try:
            return datetime.strptime(date_string, format)
        except ValueError:
            msg_tail = ' for file {}'.format(file_path) if file_path else ''
            msg = 'Wrong datetime format {}{}. Expected {}'.format(date_string, msg_tail, format)
            print(msg)

    def is_report_exist_for_log(self, log_file_info, files_paths):
        report_name_re = '^{dir}/report-(20\d{{2}}\.\d{{2}}\.\d{{2}})\.html$'.format(dir=self._report_dir)
        for file_path in files_paths:
            matching_values = re.findall(report_name_re, file_path)
            date_string = matching_values[0]
            report_date = self._parse_date_from_string(date_string, '%Y.%m.%d', file_path)
            if log_file_info.date == report_date:
                return True

        return False

    def _get_log_file_info(self):
        pass

    def _get_last_log_path_to_parse(self, dir_name, files_paths):
        log_name_re = '^{dir}/nginx-access-ui\.log-(20\d{{6}})\.{{0,1}}(.{{0,2}})$'.format(dir=dir_name)
        log_files = []
        for file_path in files_paths:
            matching_lines = re.findall(log_name_re, file_path)[0]
            date_string, file_extension = matching_lines[0], matching_lines[1]
            # TODO: check if date and extension are ok, and then add only in that case
            # self._get_log_file_info()
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

    def _read_lines(self, file_object):
        while True:
            line = file_object.readline()
            if not line:
                break
            yield line

    def _read_file(self, path):
        # TODO: write a decorator for try/exc
        # TODO: compressed files reading
        try:
            with open(path) as file_handler:
                for line in self._read_lines(file_handler):
                    yield line
        except (IOError, OSError):
            print("An error opening / processing log file occurred")

    def get_file_to_parse(self):
        log_files_paths = self._get_files_paths_of_dir(dir_name=self._log_dir)
        last_log_file = self._get_last_log_path_to_parse(dir_name=self._log_dir, files_paths=log_files_paths)

        report_files_paths = self._get_files_paths_of_dir(dir_name=self._report_dir)
        if self.is_report_exist_for_log(log_file_info=last_log_file, files_paths=report_files_paths):
            raise ReportExists

        log_content = self._read_file(path=last_log_file.path)
        last_log_file.content = log_content

        return last_log_file


class LogFile:
    def __init__(self, date, path, file_extension, content=None):
        self.date = date
        self.path = path
        self.content = content
        self.file_extension = file_extension

    def __repr__(self):
        return self.date.strftime('%m/%d/%Y')
