import re
import logging

from src.parser.median_calc import median

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';


class LogParser:
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

    def __init__(self, log_file_content, report_size):
        self._log_file_content = log_file_content
        self._report_size = report_size

    def _parse_lines(self, lines):
        for line in lines:
            decoded_line = line.decode('utf-8') if isinstance(line, bytes) else line
            matched_obj = re.match(self._RE_PATTERN, decoded_line)
            if not matched_obj:
                logging.error('Can not recognize line {} in the log'.format(line))
                continue
            matching_values = matched_obj.groupdict()
            yield matching_values

    def _update_single_url_statistic_values(self, item, request_time):
        item['time_occurrences'].append(request_time)
        report = item['report']
        report['count'] += 1
        report['time_sum'] += request_time
        time_max = float(report['time_max'])
        report['time_max'] = request_time if request_time > time_max else time_max

    def _calculate_common_statistic_values(self, log_statistic):
        for item in log_statistic['requests'].values():
            report = item['report']
            report['count_perc'] = report['count'] / log_statistic['total_requests_count'] * 100
            report['time_perc'] = report['time_sum'] / log_statistic['total_requests_time'] * 100
            report['time_avg'] = report['time_sum'] / report['count']
            report['time_med'] = median(item['time_occurrences'])
        return log_statistic

    def _get_raw_requests_values(self, matching_values_list):
        log_statistic = {
            'requests': {},
            'total_requests_count': 0,
            'total_requests_time': 0
        }
        total_requests_time = 0
        total_requests_count = 0
        for matching_values in matching_values_list:
            requests = log_statistic['requests']
            log_statistic_urls = [url for url in requests.keys()]
            url = matching_values['url']
            request_time = float(matching_values['request_time'])
            if url in log_statistic_urls:
                statistic_item = requests[url]
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
                requests[url] = new_statistic_item
            total_requests_time += request_time
            total_requests_count += 1

        log_statistic['total_requests_count'] = total_requests_count
        log_statistic['total_requests_time'] = total_requests_time
        return log_statistic

    def _get_full_statistic(self, matching_values_list):
        log_statistic = self._get_raw_requests_values(matching_values_list)
        full_log_statistic = self._calculate_common_statistic_values(log_statistic=log_statistic)

        requests = full_log_statistic['requests']
        report = [statistic['report'] for statistic in requests.values()]
        sorted_report = sorted(report, key=lambda value: value['time_sum'], reverse=True)
        cutted_report = sorted_report[:self._report_size]
        return cutted_report

    def get_parsed_data(self):
        matching_values_list = self._parse_lines(lines=self._log_file_content)
        log_statistic = self._get_full_statistic(matching_values_list)

        return log_statistic
