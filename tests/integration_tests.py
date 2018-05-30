import unittest
import os

import log_analyzer


class TestLogAnalyzer(unittest.TestCase):
    TEST_LOG_PATH = './test_nginx_acess.log'
    RESULT_REPORT_PATH = './report.html'

    def setUp(self):
        with open(self.TEST_LOG_PATH, "w") as log_file:
            log_file.write("<td>hello!<td>\n"
                           "I am Nick!\n")

    def tearDown(self):
        def remove_file(path):
            if os.path.isfile(path):
                os.remove(path)

        remove_file(self.TEST_LOG_PATH)
        remove_file(self.RESULT_REPORT_PATH)

    def _read_file(self, path):
        with open(path) as f:
            data = f.readlines()
        return data

    def test_it_returns_correct_statistic(self):
        os.environ["NGINX_LOG_PATH"] = self.TEST_LOG_PATH
        log_analyzer.main()
        report_content = self._read_file(self.RESULT_REPORT_PATH)
        self.assertIn(
            "<td>hello!<td>\n",
            report_content
        )


if __name__ == '__main__':
    unittest.main(warnings='ignore')
