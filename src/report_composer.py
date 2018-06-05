class ReportComposer:
    def __init__(self, log_file_obj, report_dir, report_content):
        self._log_file_obj = log_file_obj
        self._report_dir = report_dir
        self._report_content = report_content

    def _write_file(self, source, path):
        try:
            with open(path, "w") as file_handler:
                for line in source:
                    file_handler.write(line)
        except (IOError, OSError):
            print("An error opening / processing report file occurred")

    def compose(self):
        log_file_date  = self._log_file_obj.date
        log_file_date_string = log_file_date.strftime('%Y.%m.%d')
        path = '{dir}/report-{date_string}.html'.format(dir=self._report_dir, date_string=log_file_date_string)
        self._write_file(source=self._report_content, path=path)
