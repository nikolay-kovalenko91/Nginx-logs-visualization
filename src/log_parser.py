import re

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';


class LogParser:
    _RE_PATTERN = '^(?P<remote_addr>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ' \
                 '(?P<remote_user>[^ ]{1,})  ' \
                 '(?P<http_x_real_ip>[^ ]{1,}|\-) ' \
                 '\[(?P<time_local>[0-9]{2}\/[A-Za-z]{3}\/[0-9]{1,4}:[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2} [+\-][0-9]{4})\] ' \
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

    # Todo : refactoring
    # Todo : time_med evaluation

    def _parse_lines(self, lines):
        for line in lines:
            matched_obj = re.match(self._RE_PATTERN, line)
            if not matched_obj:
                print('Can not recognize line {} in the log'.format(line))
                continue
            matching_values = matched_obj.groupdict()
            yield matching_values

    def _update_single_url_statistic_values(self, item, request_time):
        item['count'] += 1
        item['time_sum'] += request_time
        time_max = float(item['time_max'])
        item['time_max'] = request_time if request_time > time_max else time_max

    def _calculate_common_statistic_values(self, log_statistic, total_requests_time, total_requests_count):
        for item in log_statistic.values():
            item['count_perc'] = item['count'] / total_requests_count * 100
            item['time_perc'] = item['time_sum'] / total_requests_time * 100
            item['time_avg'] = item['time_sum'] / item['count']
            item['time_med'] = item['time_sum'] / item['count']
        return log_statistic

    def _get_statistic(self, matching_values_list):
        log_statistic = {}
        total_requests_time = 0
        total_requests_count = 0

        for matching_values in matching_values_list:
            log_statistic_urls = [url for url in log_statistic.keys()]
            url = matching_values['url']
            request_time = float(matching_values['request_time'])
            if url in log_statistic_urls:
                statistic_item = log_statistic[url]
                self._update_single_url_statistic_values(item=statistic_item, request_time=request_time)
            else:
                new_statistic_item = {
                    'count': 1,
                    'count_perc': 0.0,
                    'time_sum': request_time,
                    'time_perc': 0.0,
                    'time_avg': 0.0,
                    'time_max': request_time,
                    'time_med': 0.0,
                    'url': url
                }
                log_statistic[url] = new_statistic_item

            total_requests_time += request_time
            total_requests_count += 1

        full_log_statistic = self._calculate_common_statistic_values(
            log_statistic=log_statistic,
            total_requests_time=total_requests_time,
            total_requests_count=total_requests_count
        )

        sorted_statistic = sorted(full_log_statistic.values(), key=lambda value: value['time_sum'])
        cutted_statistic = sorted_statistic[self._report_size:]
        return cutted_statistic

    def get_parsed_data(self):
        self._log_file_content = list(self._log_file_content)
        matching_values_list = self._parse_lines(lines=self._log_file_content)
        log_statistic = self._get_statistic(matching_values_list)

        return log_statistic
