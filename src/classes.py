from datetime import datetime
from typing import List


class LogFile:
    def __init__(self, date: datetime, path: str, file_extension: str, content: List[str]=None):
        self.date = date
        self.path = path
        self.content = content
        self.file_extension = file_extension

    def set_content(self, content):
        self.content = content

    def __repr__(self):
        return self.date.strftime('%m/%d/%Y')