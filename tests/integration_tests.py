import unittest
import os
import json
import shutil

import log_analyzer


class TestLogAnalyzer(unittest.TestCase):
    _TEST_LOG_NAME = 'test_nginx_acess.log'
    _TESTS_RUNNING_DIR = 'test'
    _CONFIG_NAME = "config.py"

    @classmethod
    def setUpClass(cls):
        cls._report_dir = "./{}/reports".format(cls._TESTS_RUNNING_DIR)
        cls._log_dir = "./{}/log".format(cls._TESTS_RUNNING_DIR)
        cls._config_path = "./{}/{}".format(cls._TESTS_RUNNING_DIR, cls._CONFIG_NAME)

    def _create_test_dirs(self):
        def create_dir(name):
            if not os.path.exists(name):
                os.makedirs(name)

        for name in [self._TESTS_RUNNING_DIR, self._report_dir, self._log_dir]:
            create_dir(name)

    def _create_config(self):
        config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": self._report_dir,
            "LOG_DIR": self._log_dir
        }
        with open(self._config_path, "w") as config_file:
            json.dump(config, config_file, indent=2)

    def setUp(self):
        self._create_test_dirs()
        self._create_config()
        log_path = '{dir}/{name}'.format(dir=self._log_dir, name=self._TEST_LOG_NAME)
        with open(log_path, "w") as log_file:
            log_file.write("<td>hello!<td>\n"
                           "I am Nick!\n")

    def tearDown(self):
        try:
            shutil.rmtree(self._TESTS_RUNNING_DIR)
        except OSError as e:
            self.fail("An error occurred: {} - {}.".format(e.filename, e.strerror))

    def _read_file(self, path):
        try:
            with open(path) as f:
                data = f.readlines()
            return data
        except (IOError, OSError):
            self.fail("An error opening / processing config file occurred")

    def test_it_returns_correct_statistic(self):
        os.environ["config"] = self._config_path
        log_analyzer.main()
        report_path = '{dir}/{report_name}.html'.format(dir=self._report_dir, report_name=self._TEST_LOG_NAME)
        report_content = self._read_file(report_path)
        self.assertIn(
            "<td>hello!<td>\n",
            report_content
        )


if __name__ == '__main__':
    unittest.main(warnings='ignore')
