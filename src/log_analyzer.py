class LogAnalyzer:
    _RESULT_REPORT_PATH = './report.html'

    def _write_report(self, source):
        try:
            with open(self._RESULT_REPORT_PATH, "w") as file_handler:
                for line in source:
                    file_handler.write(line)
        except (IOError, OSError):
            print("An error opening / processing report file occurred")

    def main(self, config):
        pass
        # for line in self._read_file(log_path):
        # source = self._read_file(log_path)
        # self._write_report(source)
