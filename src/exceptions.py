class ReportExists(Exception):

    def __init__(self, *args, **kwargs):
        self.message = 'A report already exists for a last found log file'
        super().__init__(*args, **kwargs)


class NoLogFilesFound(Exception):

    def __init__(self, *args, **kwargs):
        self.message = 'There are no log files in the passed directory. Check config settings'
        super().__init__(*args, **kwargs)
