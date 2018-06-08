class LogParser:
    def __init__(self, log_file_content):
        self._log_file_content = log_file_content

    def get_parsed_data(self):
        # TODO: Implement the logic
        """Re: https://regex101.com/r/K1jkk3/3/ https://gist.github.com/oinume/6837358
        ^(?P<remote_addr>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) (?P<remote_user>[^ ]{1,})  (?P<http_x_real_ip>[^ ]{1,}|\-) \[(?P<time_local>[0-9]{2}\/[A-Za-z]{3}\/[0-9]{1,4}:[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2} [+\-][0-9]{4})\] "(?P<request>[A-Z ]+) (?P<uri>[^"]*) (?P<protocol>[^"]*)" (?P<status>[0-9]{3}) (?P<body_bytes_sent>[0-9]{1,}|\-) "(?P<http_referer>[^"]*|\-)" "(?P<http_user_agent>[^"]+)" "(?P<http_x_forwarded_for>[^"]*|\-)" "(?P<http_X_REQUEST_ID>[^"]*|\-)" (?P<http_X_RB_USER>[^ ]{1,}) (?P<request_time>[\d\.]+)$
        """
        yield from self._log_file_content
