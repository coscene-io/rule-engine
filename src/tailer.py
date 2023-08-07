import sys
from collections import namedtuple

import pygtail
import os
import re
from datetime import datetime
import pytz

hint_options = [
    (re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"), "%Y-%m-%d %H:%M:%S"),
    (re.compile(r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}"), "%Y/%m/%d %H:%M:%S")
]
ts_schema = [
    (re.compile(r"\d{4}\s+\d{2}:\d{2}:\d{2}.\d{6}"), "%m%d %H:%M:%S.%f"),
    (re.compile(r"[a-zA-Z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}"), "%b %d %H:%M:%S"),
]


def get_timestamp_hint_from_file(filename):
    with open(filename, "r") as f:
        first_line = f.readline()

        for regex, date_format in hint_options:
            time_candidate = regex.search(first_line)
            if time_candidate:
                try:
                    parsed_time = datetime.strptime(time_candidate.group(), date_format).replace(
                        tzinfo=pytz.timezone('Asia/Shanghai'))
                    return parsed_time
                except ValueError:
                    pass

        return None


def get_timestamp_with_hint(dt, hint):
    if hint:
        candidate = dt.replace(year=hint.year)
        if candidate < hint:
            return candidate.replace(year=hint.year + 1)
        return candidate
    else:
        candidate = dt.replace(year=datetime.now().year)
        if candidate > datetime.now().replace(tzinfo=pytz.timezone('Asia/Shanghai')):
            return candidate.replace(year=datetime.now().year - 1)
        return candidate


def get_timestamp_from_line(line, hint):
    for regex, date_format in ts_schema:
        time_candidate = regex.search(line)
        if time_candidate:
            try:
                parsed_time = datetime.strptime(time_candidate.group(), date_format).replace(
                    tzinfo=pytz.timezone('Asia/Shanghai'))
                return get_timestamp_with_hint(parsed_time, hint)
            except ValueError:
                pass

    return None


def update_tail_dict(tail_dict, dirname):
    for entry in os.scandir(dirname):
        if entry.is_file() and not entry.name.endswith(".offset"):
            filename = entry.name
            if filename not in tail_dict:
                tail_dict[filename] = \
                    (pygtail.Pygtail(os.path.join(dirname, filename), save_on_end=False),
                     get_timestamp_hint_from_file(os.path.join(dirname, filename)))
    return tail_dict


watch_log_dir = sys.argv[1]

LogDataItem = namedtuple('LogDataItem', 'topic msg ts')
def tail_lines_from_dir(dir):
    tail_dict = dict()
    latest_timestamps = dict()

    while True:
        tail_dict = update_tail_dict(tail_dict, dir)
        for filename, (tail, hint) in tail_dict.items():
            for line in tail:
                timestamp = get_timestamp_from_line(line, hint)
                if timestamp:
                    latest_timestamps[filename] = int(timestamp.timestamp())
                if filename not in latest_timestamps:
                    continue

                yield LogDataItem(os.path.join(dir, filename), line, latest_timestamps[filename])
