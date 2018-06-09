import re

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER"
#                     '$request_time';


class LogParser:
    RE_PATTERN = '^(?P<remote_addr>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) ' \
                 '(?P<remote_user>[^ ]{1,})  ' \
                 '(?P<http_x_real_ip>[^ ]{1,}|\-) ' \
                 '\[(?P<time_local>[0-9]{2}\/[A-Za-z]{3}\/[0-9]{1,4}:[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2} [+\-][0-9]{4})\] ' \
                 '"(?P<request>[A-Z ]+) ' \
                 '(?P<uri>[^"]*) ' \
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
        for line in self._log_file_content:
            matched_obj = re.match(self.RE_PATTERN, line)
            if not matched_obj:
                print('Can not recognize line {} in the log'.format(line))
                continue
            matching_values = matched_obj.groupdict()
            yield matching_values

    def get_parsed_data(self):
        self._log_file_content = list(self._log_file_content)
        matching_values_list = self._parse_lines(self._log_file_content)

        # for line in logfile:
        #     item = parse(line)
        #     statistic[item.route].count + +
        #     statistic[item.route].total_time += item.time
        #
        # total_lines = 0
        # for k, v in statistic:
        #     total_lines = v.count
        #
        # for k, v in statistic:
        #     v.count = v.count / total_lines
        #
        # route = [(s.count, route): route
        # for route, s in statistic]
        # keys = sort(count_to_route_dict.keys(), lambda x, y: x > y)[1000😏
        # for

        yield from self._log_file_content
