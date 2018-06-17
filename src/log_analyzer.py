import logging

from src.log_files_handler import LogFilesHandler
from src.report_composer import ReportComposer
from src.parser.log_parser import LogParser


class LogAnalyzer:
    def __init__(self, config):
        self._report_size = config['REPORT_SIZE']
        self._report_dir = config['REPORT_DIR']
        self._log_dir = config['LOG_DIR']

    def main(self):
        log_files_handler = LogFilesHandler(log_dir=self._log_dir, report_dir=self._report_dir)
        log_file_obj = log_files_handler.get_file_to_parse()
        logging.info('Running a parsing for the found log file: {} ...'.format(log_file_obj.path))

        log_parser = LogParser(log_file_content=log_file_obj.content, report_size=self._report_size)
        report_content = log_parser.get_parsed_data()
        logging.info('The parsing completed successfully. Saving a report...')

        report_composer = ReportComposer(log_file_obj=log_file_obj,
                                         report_dir=self._report_dir,
                                         table_content=report_content)
        report_composer.compose()
