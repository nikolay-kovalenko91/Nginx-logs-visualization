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
        self._log_path = self.test_environment.create_log_file_and_get_its_path(name=self._TEST_LOG_NAME)

    def tearDown(self):
        self.test_environment.remove()

    def test_it_returns_correct_statistic(self):
        os.environ["config"] = self.test_environment.get_config_path()
        app.main()
        report_path = '{dir}/{report_name}'.format(
            dir=self.test_environment.get_report_dir(),
            report_name=self._TEST_REPORT_NAME)
        report_content = read_file(report_path)
        #TODO: read appropriate content
        self.assertIn(
            "<td>hello!<td>\n",
            report_content
        )


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
