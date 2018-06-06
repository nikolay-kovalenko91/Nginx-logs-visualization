from src.log_files_handler import LogFilesHandler
from src.report_composer import ReportComposer


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
        report_content = self.parse_log(content=log_file_obj.content)

        report_composer = ReportComposer(log_file_obj=log_file_obj,
                                         report_dir=self._report_dir,
                                         table_content=report_content)
        report_composer.compose()
