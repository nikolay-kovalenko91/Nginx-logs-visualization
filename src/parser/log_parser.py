import re
import sys
import logging
from typing import List, Generator, Iterable

from src.parser.median_calc import median

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';


class LogParser:
    """
    Parses a passed log content extracting requests metrics for each url.
    """
    _ALLOWED_PARSE_FAILURES_PERCENT = 60
    _RE_PATTERN = '^(?P<remote_addr>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ' \
                  '(?P<remote_user>[^ ]{1,})  ' \
                  '(?P<http_x_real_ip>[^ ]{1,}|\-) ' \
                  '\[(?P<time_local>[0-9]{2}\/[A-Za-z]{3}\/[0-9]{1,4}:[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2} ' \
                  '[+\-][0-9]{4})\] ' \
                  '"(?P<request>[A-Z ]+) ' \
                  '(?P<url>[^"]*) ' \
                  '(?P<protocol>[^"]*)" ' \
                  '(?P<status>[0-9]{3}) ' \
                  '(?P<body_bytes_sent>[0-9]{1,}|\-) ' \
                  '"(?P<http_referer>[^"]*|\-)" ' \
                  '"(?P<http_user_agent>[^"]+)" ' \
                  '"(?P<http_x_forwarded_for>[^"]*|\-)" ' \
                  '"(?P<http_X_REQUEST_ID>[^"]*|\-)" ' \
                  '(?P<http_X_RB_USER>[^ ]{1,}) ' \
                  '(?P<request_time>[\d\.]+)$'

    def __init__(self, log_file_content: List[str], report_size: int):
        self._log_file_content = log_file_content
        self._report_size = report_size

    def _exit_on_failures_handler(self, failures_count, total_lines_handled):
        if total_lines_handled < 5 or not failures_count:
            return
        failures_percent = failures_count / total_lines_handled * 100
        if failures_percent > self._ALLOWED_PARSE_FAILURES_PERCENT:
            msg = 'There are more than {}% parsing failures while reading log content. Going to quit.'
            logging.error(msg.format(self._ALLOWED_PARSE_FAILURES_PERCENT))
            sys.exit()

    def _parse_lines(self, lines: List[str]) -> Generator[dict, None, None]:
        failures_count = 0
        total_lines_handled = 0
        for line in lines:
            decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line
            matched_obj = re.match(self._RE_PATTERN, decoded_line)
            total_lines_handled += 1
            if not matched_obj:
                failures_count += 1
                logging.error('Can not recognize line {} in the log'.format(line))
            else:
                matching_values = matched_obj.groupdict()
                yield matching_values

            self._exit_on_failures_handler(failures_count, total_lines_handled)

    def get_parsed_data(self) -> List[dict]:
        matching_values_list = self._parse_lines(lines=self._log_file_content)

        statistic = ParseStatistic(requests_info=matching_values_list)
        report = statistic.get_report()
        sorted_report = sorted(report, key=lambda value: value['time_sum'], reverse=True)
        cutted_report = sorted_report[:self._report_size]

        return cutted_report


class ParseStatistic:
    """
    Calculates all the required requests metrics
    """
    def __init__(self, requests_info: Iterable[dict]):
        self._requests_info = requests_info
        self._total_requests_time = 0
        self._total_requests_count = 0

    def _update_single_url_statistic_values(self, item: dict, request_time: float) -> None:
        item['time_occurrences'].append(request_time)
        report = item['report']
        report['count'] += 1
        report['time_sum'] += request_time
        time_max = float(report['time_max'])
        report['time_max'] = request_time if request_time > time_max else time_max

    def _calculate_common_statistic_values(self, requests_statistic: dict) -> dict:
        for item in requests_statistic.values():
            report = item['report']
            report['count_perc'] = report['count'] / self._total_requests_count * 100
            report['time_perc'] = report['time_sum'] / self._total_requests_time * 100
            report['time_avg'] = report['time_sum'] / report['count']
            report['time_med'] = median(item['time_occurrences'])
        return requests_statistic

    def _get_raw_requests_values(self, matching_values_list: Iterable[dict]) -> dict:
        requests_statistic = {}
        for matching_values in matching_values_list:
            log_statistic_urls = [url for url in requests_statistic.keys()]
            url = matching_values['url']
            request_time = float(matching_values['request_time'])
            if url in log_statistic_urls:
                statistic_item = requests_statistic[url]
                self._update_single_url_statistic_values(item=statistic_item, request_time=request_time)
            else:
                new_statistic_item = {
                    'time_occurrences': [request_time],
                    'report': {
                        'count': 1,
                        'count_perc': 0.0,
                        'time_sum': request_time,
                        'time_perc': 0.0,
                        'time_avg': 0.0,
                        'time_max': request_time,
                        'time_med': 0.0,
                        'url': url
                    }
                }
                requests_statistic[url] = new_statistic_item
            self._total_requests_time += request_time
            self._total_requests_count += 1

        return requests_statistic

    def get_report(self) -> Generator[dict, None, None]:
        requests_statistic = self._get_raw_requests_values(self._requests_info)
        filled_requests_statistic = self._calculate_common_statistic_values(requests_statistic)

        report = (statistic['report'] for statistic in filled_requests_statistic.values())
        return report
