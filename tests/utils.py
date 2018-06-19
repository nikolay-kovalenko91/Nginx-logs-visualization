import os
import json
import shutil
import random
import string


class TestEnvironment:
    def __init__(self, test_running_dir, config_name):
        self._test_running_dir = test_running_dir
        self._report_dir = "./{}/reports_test".format(test_running_dir)
        self._log_dir = "./{}/log_test".format(test_running_dir)
        self._config_path = "./{}/{}".format(test_running_dir, config_name)
        self._app_log_path = "./{}/app_log.txt".format(test_running_dir)

    def _create_test_dirs(self):
        def create_dir(name):
            if not os.path.exists(name):
                os.makedirs(name)

        for name in [self._test_running_dir, self._report_dir, self._log_dir]:
            create_dir(name)

    def _create_config(self):
        config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": self._report_dir,
            "LOG_DIR": self._log_dir,
            "LOG_FILE_PATH": self._app_log_path
        }
        with open(self._config_path, "w") as config_file:
            json.dump(config, config_file, indent=2)

    def create_log_file_and_get_its_path(self, name, content=None):
        log_dir = self.get_log_dir()
        log_path = '{dir}/{name}'.format(dir=log_dir, name=name)
        if not content:
            random_line_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            random_line_2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            content = [random_line_1 + "\n", random_line_2 + "\n"]

        with open(log_path, "w") as log_file:
            for line in content:
                log_file.write(line)
        return log_path

    def setup_for_app(self):
        self._create_test_dirs()
        self._create_config()

    def remove(self):
        try:
            shutil.rmtree(self._test_running_dir)
        except OSError as e:
            print("An error occurred: {} - {}.".format(e.filename, e.strerror))

    def get_report_dir(self):
        return self._report_dir

    def get_log_dir(self):
        return self._log_dir

    def get_config_path(self):
        return self._config_path


def read_file(path):
    try:
        with open(path) as f:
            data = f.readlines()
        return data
    except (IOError, OSError):
        raise Exception("An error opening / processing file {} occurred".format(path))
