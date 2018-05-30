#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


class LogAnalyzer:
    _RESULT_REPORT_PATH = './report.html'

    def _read_lines(self, file_object):
        while True:
            line = file_object.readline()
            if not line:
                break
            yield line

    def _read_file(self, path):
        try:
            with open(path) as file_handler:
                for line in self._read_lines(file_handler):
                    yield line
        except (IOError, OSError):
            print("An error opening / processing log file occurred")

    def _write_report(self, source):
        try:
            with open(self._RESULT_REPORT_PATH, "w") as file_handler:
                for line in source:
                    file_handler.write(line)
        except (IOError, OSError):
            print("An error opening / processing report file occurred")

    def main(self, log_path):
        # for line in self._read_file(log_path):
        source = self._read_file(log_path)
        self._write_report(source)


def main():
    log_path = os.environ.get('NGINX_LOG_PATH',
                              './nginx-access-ui.log-20170630.gz')
    LogAnalyzer().main(log_path)


if __name__ == '__main__':
    main()
