from datetime import datetime

from src.log_files_handler import LogFilesHandler


class LogAnalyzer:
    def __init__(self, config):
        self._report_size = config['REPORT_SIZE']
        self._report_dir = config['REPORT_DIR']
        self._log_dir = config['LOG_DIR']

    def parse_log(self, content):
        yield from content

    def _write_report(self, source, path):
        try:
            with open(path, "w") as file_handler:
                for line in source:
                    file_handler.write(line)
        except (IOError, OSError):
            print("An error opening / processing report file occurred")

    def main(self):
        log_files_handler = LogFilesHandler(log_dir=self._log_dir, report_dir=self._report_dir)
        log_file_obj = log_files_handler.get_file_to_parse()
        lines = self.parse_log(content=log_file_obj.content)

        date_string = log_file_obj.date.strftime('%Y.%m.%d')
        path = '{dir}/report-{date_string}.html'.format(dir=self._report_dir, date_string=date_string)
        self._write_report(source=lines, path=path)
