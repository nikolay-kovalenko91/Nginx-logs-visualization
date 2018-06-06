import unittest
import os

from utils import TestEnvironment, read_file

import app
from src.log_files_handler import LogFilesHandler

TEST_CONFIG = {
    'TESTS_RUNNING_DIR': 'sandbox',
    'CONFIG_NAME': 'config.py'
}


#@unittest.skip("just for developing")
class TestApp(unittest.TestCase):
    """
    An integration test
    """
    _TEST_LOG_NAME = 'nginx-access-ui.log-20170630'
    _TEST_REPORT_NAME = 'report-2017.06.30.html'
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
    ]
    _EXPECTED_REPORT_TABLE_CONTENT = [
        {
            'count': 5579,
            'count_perc': 0.21345333754705043,
            'time_sum': 1480.1929999999986,
            'time_perc': 0.07679145684672731,
            'time_max': 119.954,
            'time_avg': 0.2653151102348091,
            'time_med': 0.188,
            'url': '/api/v2/banner/25019354 HTTP/1.1'
        },
        {
            'count': 5579,
            'count_perc': 0.21345333754705043,
            'time_sum': 1480.1929999999986,
            'time_perc': 0.07679145684672731,
            'time_max': 119.954,
            'time_avg': 0.2653151102348091,
            'time_med': 0.188,
            'url': '/api/v2/banner/25019354 HTTP/1.1'
        },
    ]

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


#@unittest.skip("just for developing")
class TestLogfile(unittest.TestCase):
    """
    Unit tests for Logfile class
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

        with self.assertRaises(StopIteration):
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

        with self.assertRaises(ValueError):
            log_files_handler.get_file_to_parse()


if __name__ == '__main__':
    unittest.main(warnings='ignore')
