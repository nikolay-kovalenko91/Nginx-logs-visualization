# Nginx log parser
Parses Nginx server logs and saves the longest requests parameters(url,
total request sum value, percentage relative to others, etc) as a table
in a html page.

## Running the app
The app uses Python 3. To run the app:

1) Create a file ```config.json``` with content ```{}``` in it in the
project root folder.

2) Create a folder ```reports``` in the root folder.
Also, you can use a custom folder path. Just declare it in
```config.json``` using ```REPORT_DIR``` key.
E.g.:
```
config.json:

{
    "REPORT_DIR": "./reports"
}
```

3) Create a folder ```log``` in the project root or declare a custom
path in ```config.json``` using ```LOG_DIR``` key. Nginx log files
should be there. The script will be parse the last log file.

4) Run the script:
```
$ python ./app.py
```
As a script will finish, the html report will appear in ```reports```
folder.

## Logging
You can specify a log file path to save the app logs into it instead of
putting it in stdout. To use that feature, declare the log path in
```config.json``` using ```LOG_FILE_PATH``` key

## Running tests
To run the tests, execute in the project folder:
```
$ python ./tests/tests.py
```

### A format used for parsing Nginx logs
```
$remote_addr $remote_user $http_x_real_ip [$time_local] "$request"
$status $body_bytes_sent "$http_referer"
"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID"
"$http_X_RB_USER" $request_time;
```
You can use your own format by changing ```_RE_PATTERN``` regex in
```LogParser``` class(```./src/parser/log_parser.py```).
