import re
import datetime

def str_to_datetime(string):
    time = None
    rfc3339 = re.match("(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d+)?(Z|[+-]\d{2}:\d{2})", string)
    if rfc3339:
        # TODO: include timezone
        (year, month, day, hour, minute, second, milisecond, timezone) = rfc3339.groups()
        if milisecond is None:
            milisecond = '0'
        time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(milisecond))
    return time
