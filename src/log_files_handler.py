import re
import gzip

from typing import Generator, TextIO, Iterable


# Namedtuple is immutable, so I can't set up 'content' param.
# The best idea is to use 'pip install recordtype' later
from src.classes import LogFile
from src.report_composer import ReportComposer
from src.utils import get_files_paths_of_dir, parse_date_from_string


class LogFilesHandler:
    """
    Finds the last dated Nginx log, reads its content, and returns it with another
    log file info.
    """
    _LOG_DATETIME_NAME_FORMAT = '%Y%m%d'

    def __init__(self, log_dir, report_dir):
        self._log_dir = log_dir
        self._report_dir = report_dir

    def _get_last_log_path_to_parse(self, dir_name: str, files_paths: Iterable[str]) -> LogFile:
        log_name_re = '^{dir}/nginx-access-ui\.log-(20\d{{6}})\.{{0,1}}(.{{0,2}})$'.format(dir=dir_name)
        log_files = []
        for file_path in files_paths:
            matching_lines = re.findall(log_name_re, file_path)[0]
            date_string, file_extension = matching_lines[0], matching_lines[1]
            date = parse_date_from_string(date_string, self._LOG_DATETIME_NAME_FORMAT, file_path)
            log_file = LogFile(
                date=date,
                path=file_path,
                file_extension=file_extension
            )
            log_files.append(log_file)

        log_files.sort(key=lambda log_f: log_f.date)

        if len(log_files) == 0:
            raise EnvironmentError('There are no log files in the passed directory. Check config settings')

        return log_files.pop()

    def _read_lines(self, file_object: TextIO) -> Generator[str, None, None]:
        while True:
            line = file_object.readline()
            if not line:
                break
            yield line

    def _read_plain_file(self, path: str) -> Generator[str, None, None]:
        try:
            with open(path) as file_handler:
                yield from self._read_lines(file_handler)

        except (IOError, OSError):
            raise EnvironmentError("An error writing/reading file occurred: {}".format(path))

    def _read_gzip_file(self, path: str) -> Generator[str, None, None]:
        try:
            with gzip.open(path, 'rb') as file_handler:
                yield from self._read_lines(file_handler)

        except (IOError, OSError):
            raise EnvironmentError("An error writing/reading file occurred: {}".format(path))

    def _read_file(self, path: str, extension: str) -> Generator[str, None, None]:
        extension_vs_handlers = {
            '': self._read_plain_file,
            'gz': self._read_gzip_file
        }
        if extension not in extension_vs_handlers:
            raise EnvironmentError('Unknown extension of found log file {}'.format(path))

        handler = extension_vs_handlers[extension]

        yield from handler(path=path)

    def get_file_to_parse(self) -> LogFile:
        log_files_paths = get_files_paths_of_dir(dir_name=self._log_dir)
        last_log_file = self._get_last_log_path_to_parse(dir_name=self._log_dir, files_paths=log_files_paths)

        report_composer = ReportComposer(log_file_obj=last_log_file, report_dir=self._report_dir)
        report_composer.check_if_report_already_exists()

        log_content = self._read_file(path=last_log_file.path, extension=last_log_file.file_extension)
        last_log_file.set_content(log_content)

        return last_log_file
