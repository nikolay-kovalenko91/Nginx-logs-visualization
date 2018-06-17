from string import Template
import logging


class ReportComposer:
    _TEMPLATE_PATH = './templates/report.html'

    def __init__(self, log_file_obj, report_dir, table_content):
        self._log_file_obj = log_file_obj
        self._report_dir = report_dir
        self._table_content = table_content

    def _write_file(self, content, path):
        try:
            with open(path, "w") as file_handler:
                file_handler.write(content)
        except (IOError, OSError):
            logging.exception("An error writing report file occurred")

    def _get_template(self):
        with open(self._TEMPLATE_PATH) as file_handler:
            return file_handler.read()

    def _get_report_content(self):
        template_string = self._get_template()
        template = Template(template_string)
        return template.substitute(table_json=self._table_content)

    def compose(self):
        log_file_date = self._log_file_obj.date
        log_file_date_string = log_file_date.strftime('%Y.%m.%d')
        path = '{dir}/report-{date_string}.html'.format(dir=self._report_dir, date_string=log_file_date_string)
        report_content = self._get_report_content()
        self._write_file(content=report_content, path=path)
