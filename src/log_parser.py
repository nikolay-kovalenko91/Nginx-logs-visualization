class LogParser:
    def __init__(self, log_file_content):
        self._log_file_content = log_file_content

    def get_parsed_data(self):
        # TODO: Implement the logic
        yield from self._log_file_content
