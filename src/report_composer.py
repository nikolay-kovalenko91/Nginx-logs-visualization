class ReportComposer:
    def __init__(self, log_file_obj, report_dir, table_content):
        self._log_file_obj = log_file_obj
        self._report_dir = report_dir
        self._table_content = table_content

    def _write_file(self, source, path):
        try:
            with open(path, "w") as file_handler:
                for line in source:
                    file_handler.write(line)
        except (IOError, OSError):
            print("An error opening / processing report file occurred")

    def compose(self):
        log_file_date = self._log_file_obj.date
        log_file_date_string = log_file_date.strftime('%Y.%m.%d')
        path = '{dir}/report-{date_string}.html'.format(dir=self._report_dir, date_string=log_file_date_string)
        #self._write_file(source=self._table_content, path=path)

# [{'count': 5579, 'count_perc': 0.21345333754705043, 'time_sum': 1480.1929999999986, 'time_perc': 0.07679145684672731, 'time_max': 119.954, 'time_avg': 0.2653151102348091, 'time_med': 0.188, url: '/1'},{"count": 2767, "time_avg": 62.994999999999997, "time_max": 9843.5689999999995, "time_sum": 174306.35200000001, "url": "/api/v2/internal/html5/phantomjs/queue/?wait=1m", "time_med": 60.073, "time_perc": 9.0429999999999993, "count_perc": 0.106}];
