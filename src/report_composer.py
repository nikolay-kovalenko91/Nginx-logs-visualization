import re
from string import Template
from typing import List, Iterable

from src.classes import LogFile
from src.utils import get_files_paths_of_dir, parse_date_from_string


class ReportComposer:
    """
    Creates html report page
    """
    _TEMPLATE_PATH = './templates/report.html'

    def __init__(self, log_file_obj: LogFile, report_dir: str) -> None:
        self._log_file_obj = log_file_obj
        self._report_dir = report_dir

    def _write_file(self, content: str, path: str) -> None:
        try:
            with open(path, "w") as file_handler:
                file_handler.write(content)

        except (IOError, OSError):
            raise EnvironmentError("An error writing/reading file occurred: {}".format(path))

    def _get_template(self) -> str:
        try:
            with open(self._TEMPLATE_PATH) as file_handler:
                return file_handler.read()

        except (IOError, OSError):
            raise EnvironmentError("An error writing/reading file occurred: {}".format(self._TEMPLATE_PATH))

    def _get_report_content(self, table_content: List[dict]) -> str:
        template_string = self._get_template()
        template = Template(template_string)
        return template.substitute(table_json=table_content)

    def _is_report_exist_for_log(self, log_file_info: LogFile, files_paths: Iterable[str]) -> bool:
        report_name_re = '^{dir}/report-(20\d{{2}}\.\d{{2}}\.\d{{2}})\.html$'.format(dir=self._report_dir)
        for file_path in files_paths:
            matching_values = re.findall(report_name_re, file_path)
            date_string = matching_values[0]
            report_date = parse_date_from_string(date_string, '%Y.%m.%d', file_path)
            if log_file_info.date == report_date:
                return True

        return False

    def check_if_report_already_exists(self):
        report_files_paths = get_files_paths_of_dir(dir_name=self._report_dir)
        if self._is_report_exist_for_log(log_file_info=self._log_file_obj, files_paths=report_files_paths):
            raise EnvironmentError('A report already exists for a last found log file')

    def compose(self, table_content: List[dict]) -> None:
        log_file_date = self._log_file_obj.date
        log_file_date_string = log_file_date.strftime('%Y.%m.%d')
        path = '{dir}/report-{date_string}.html'.format(dir=self._report_dir, date_string=log_file_date_string)
        report_content = self._get_report_content(table_content)
        self._write_file(content=report_content, path=path)
