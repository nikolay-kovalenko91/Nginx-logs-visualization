import unittest
import os

from utils import TestEnvironment, read_file

import app
from src.log_files_handler import LogFilesHandler
from src.parser.log_parser import LogParser
from src.exceptions import ReportExists, NoLogFilesFound

TEST_CONFIG = {
    'TESTS_RUNNING_DIR': 'sandbox',
    'CONFIG_NAME': 'config.json'
}
# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';
_LOG_CONTENT = [
    '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] '
    '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" '
    '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" '
    '"1498697422-2190034393-4708-9752759" "dc7161be3" 0.390\n',
    '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] '
    '"GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" '
    '"Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133\n',
    '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] '
    '"GET /api/v2/banner/25019354 HTTP/1.1" 200 19415 "-" '
    '"Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n',
    '1.169.137.1 -  - [29/Jun/2017:03:50:24 +0300] '
    '"GET /api/v2/banner/25019354 HTTP/1.1" 200 19415 "-" '
    '"Python-urllib/2.7" "-" "1498697420-2118016444-4708-9752771" "-" 0.110\n',
]
_EXPECTED_REPORT_TABLE_CONTENT = [
    {
        'count': 3,
        'count_perc': 3 / 4 * 100,
        'time_sum': 0.390 + 0.199 + 0.11,
        'time_perc': ((0.390 + 0.199 + 0.11) / (0.390 + 0.199 + 0.133 + 0.11)) * 100,
        'time_max': 0.390,
        'time_avg': (0.390 + 0.199 + 0.11) / 3,
        'time_med': 0.390,
        'url': '/api/v2/banner/25019354'
    },
    {
        'count': 1,
        'count_perc': 1 / 4 * 100,
        'time_sum': 0.133,
        'time_perc': (0.133 / (0.390 + 0.199 + 0.133 + 0.11)) * 100,
        'time_max': 0.133,
        'time_avg': 0.133,
        'time_med': 0.133,
        'url': '/api/1/photogenic_banners/list/?server_name=WIN7RB4'
    },
]


class TestApp(unittest.TestCase):
    """
    A common integration(functional) test
    """
    _TEST_LOG_NAME = 'nginx-access-ui.log-20170630'
    _TEST_REPORT_NAME = 'report-2017.06.30.html'

    _TESTS_RUNNING_DIR = TEST_CONFIG['TESTS_RUNNING_DIR']
    _CONFIG_NAME = TEST_CONFIG['CONFIG_NAME']
    _LOG_CONTENT = _LOG_CONTENT
    _EXPECTED_REPORT_TABLE_CONTENT = _EXPECTED_REPORT_TABLE_CONTENT

    @classmethod
    def setUpClass(cls):
        cls.test_environment = TestEnvironment(
            test_running_dir=cls._TESTS_RUNNING_DIR,
            config_name=cls._CONFIG_NAME
        )

    def setUp(self):
        self.test_environment.setup_for_app()
        self._log_path = self.test_environment.create_log_file_and_get_its_path(
            name=self._TEST_LOG_NAME,
            content=self._LOG_CONTENT
        )

    def tearDown(self):
        self.test_environment.remove()

    def test_it_returns_correct_statistic(self):
        os.environ["config"] = self.test_environment.get_config_path()
        app.main()
        report_path = '{dir}/{report_name}'.format(
            dir=self.test_environment.get_report_dir(),
            report_name=self._TEST_REPORT_NAME)
        # if a report exists
        if not os.path.exists(report_path):
            self.fail('A report file was not created')
        report_content = read_file(report_path)

        # check a presence of url values, seems it is enough for now
        for row in self._EXPECTED_REPORT_TABLE_CONTENT:
            if not any(row['url'] in line for line in report_content):
                self.fail('Could not find correct url values in the report')


class TestLogParser(unittest.TestCase):
    """
    Unit tests for LogParser class
    """
    _LOG_CONTENT = _LOG_CONTENT
    _EXPECTED_REPORT_TABLE_CONTENT = _EXPECTED_REPORT_TABLE_CONTENT

    # log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
    #                     '$status $request_time';
    _LOG_CONTENT_FORMATTED_WRONG = [
        '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/v2/banner/25019354 HTTP/1.1" 200 0.390\n',
        '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 0.133\n',
        '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/v2/banner/25019354 HTTP/1.1" 200 0.199\n',
        '1.169.137.3 -  - [29/Jun/2017:03:50:23 +0300] '
        '"GET /api/v2/banner/46576387 HTTP/1.1" 200 0.239\n',
        '1.169.137.2 -  - [29/Jun/2017:03:50:23 +0300] '
        '"GET /api/v2/banner/23985394 HTTP/1.1" 200 0.180\n',
    ]

    def test_it_returns_correct_report_table_data(self):
        log_parser = LogParser(log_file_content=self._LOG_CONTENT, report_size=1000)
        report_table_content = log_parser.get_parsed_data()

        for passed_report_line, expected_report_line in zip(report_table_content,
                                                            self._EXPECTED_REPORT_TABLE_CONTENT):
            for metric_name, expected_value in expected_report_line.items():
                passed_value = passed_report_line[metric_name]
                if isinstance(passed_value, float):
                    self.assertAlmostEqual(passed_value,
                                           expected_value,
                                           delta=0.1,
                                           msg='for metric name {}'.format(metric_name))
                else:
                    self.assertEqual(passed_value, expected_value)

    def test_it_quits_if_log_format_is_wrong_100_percent(self):
        log_parser = LogParser(log_file_content=self._LOG_CONTENT_FORMATTED_WRONG, report_size=1000)
        with self.assertRaises(SystemExit):
            log_parser.get_parsed_data()

    def test_it_quits_if_log_format_is_wrong_20_percent(self):
        wrong_line = self._LOG_CONTENT_FORMATTED_WRONG[0]
        log_content_formatted_wrong_partly = self._LOG_CONTENT[:]
        log_content_formatted_wrong_partly.append(wrong_line)
        log_parser = LogParser(log_file_content=log_content_formatted_wrong_partly, report_size=1000)
        try:
            log_parser.get_parsed_data()
        except SystemExit:
            self.fail('20% errors percent is OK, but an exception was raised')


class TestLogfile(unittest.TestCase):
    """
    Integration tests for Logfile class
    """
    _TEST_LOGS_NAMES = {
        '2017.06.30': 'nginx-access-ui.log-20170630',
        '2017.06.29': 'nginx-access-ui.log-20170629',
    }

    _TESTS_RUNNING_DIR = TEST_CONFIG['TESTS_RUNNING_DIR']
    _CONFIG_NAME = TEST_CONFIG['CONFIG_NAME']

    @classmethod
    def setUpClass(cls):
        cls.test_environment = TestEnvironment(
            test_running_dir=cls._TESTS_RUNNING_DIR,
            config_name=cls._CONFIG_NAME
        )

    def setUp(self):
        self.test_environment.setup_for_app()

    def tearDown(self):
        self.test_environment.remove()

    def test_it_returns_log_file(self):
        log_path = self.test_environment.create_log_file_and_get_its_path(
            name=self._TEST_LOGS_NAMES['2017.06.30']
        )
        expected_log_content = read_file(path=log_path)

        log_dir = self.test_environment.get_log_dir()
        report_dir = self.test_environment.get_report_dir()
        log_files_handler = LogFilesHandler(log_dir=log_dir, report_dir=report_dir)
        returned_log_content = log_files_handler.get_file_to_parse().content

        self.assertListEqual(expected_log_content, list(returned_log_content))

    def test_it_returns_last_by_date_log_file_from_dir(self):
        old_log_path = self.test_environment.create_log_file_and_get_its_path(
            name=self._TEST_LOGS_NAMES['2017.06.29']
        )
        new_log_path = self.test_environment.create_log_file_and_get_its_path(
            name=self._TEST_LOGS_NAMES['2017.06.30']
        )
        expected_log_content = read_file(path=new_log_path)

        log_dir = self.test_environment.get_log_dir()
        report_dir = self.test_environment.get_report_dir()
        log_files_handler = LogFilesHandler(log_dir=log_dir, report_dir=report_dir)
        returned_log_content = log_files_handler.get_file_to_parse().content

        self.assertListEqual(expected_log_content, list(returned_log_content))

    def test_it_raises_exception_if_logs_dir_empty(self):
        log_dir = self.test_environment.get_log_dir()
        report_dir = self.test_environment.get_report_dir()
        log_files_handler = LogFilesHandler(log_dir=log_dir, report_dir=report_dir)

        with self.assertRaises(NoLogFilesFound):
            log_files_handler.get_file_to_parse()

    def test_it_raises_exception_if_logs_have_analyzed_and_report_exists(self):
        date = '2017.06.30'
        try:
            report_path = '{dir}/report-{date}.html'.format(dir=self.test_environment.get_report_dir(), date=date)
            with open(report_path, "w") as file_handler:
                file_handler.write('test')
        except (IOError, OSError):
            print("An error opening / processing report file occurred")

        self.test_environment.create_log_file_and_get_its_path(
            name=self._TEST_LOGS_NAMES[date]
        )

        log_dir = self.test_environment.get_log_dir()
        report_dir = self.test_environment.get_report_dir()
        log_files_handler = LogFilesHandler(log_dir=log_dir, report_dir=report_dir)

        with self.assertRaises(ReportExists):
            log_files_handler.get_file_to_parse()


if __name__ == '__main__':
    unittest.main(warnings='ignore')
