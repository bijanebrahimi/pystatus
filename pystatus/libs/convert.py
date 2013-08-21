import re
import datetime
from BeautifulSoup import BeautifulStoneSoup

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

def datetime_to_rfc3339(date, timezone=False):
    if isinstance(date, datetime):
        return '%.4d-%.2d-%.2dT%.2d:%.2d:%.2d.%.2d%s' % (date.year, date.month, date.day,
                                                       date.hour, date.minute, date.second, date.microsecond,
                                                       'Z')

def str_to_xml(string):
    return BeautifulStoneSoup(string, selfClosingTags=['thr:in-reply-to', 'category', 'followers', 'statusnet:profile_info', 'link'])
