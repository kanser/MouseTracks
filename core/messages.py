from __future__ import division, absolute_import
from datetime import datetime


def print_override(text):
    """Send everything here to print, so that it can easily be edited.
    Defaults to Python 3 version as it'll refuse to even run the script otherwise.
    """
    print(text.encode('utf-8').strip())
    

def time_format(t):
    return '[{}]'.format(datetime.fromtimestamp(t).strftime("%H:%M:%S"))


def date_format(t):
    dt = datetime.fromtimestamp(t)
    hour = dt.hour
    minute = dt.minute
    if 0 <= hour < 12:
        suffix = 'AM'
    else:
        suffix = 'PM'
        hour %= 12
    if not hour:
        hour += 12
    output_time = '{h}:{m}{s}'.format(h=hour, m=minute, s=suffix)
    
    day = str(dt.day)
    if day.endswith('1'):
        day += 'st'
    elif day.endswith('2'):
        day += 'nd'
    elif day.endswith('3'):
        day += 'rd'
    else:
        day += 'th'
    month = dt.strftime("%B")
    year = dt.year
    output_date = '{d} {m} {y}'.format(d=day, m=month, y=year)

    return '{}, {}'.format(output_time, output_date)
    

_LENGTH = (
    #name, seconds, highest amount, number of decimals
    ('second', 1, 60, 2),
    ('minute', 60, 60, None),
    ('hour', 60 * 60, 24, None),
    ('day', 60 * 60 * 24, 7, None),
    ('week', 60 * 60 * 24 * 7, 52, None),
    ('year', 60 * 60 * 24 * 365, None, None)
)


def ticks_to_seconds(amount, tick_rate, output_length=2, allow_decimals=True):  
    """Simple function to convert ticks to a readable time for use in sentences."""

    output = []
    time_elapsed = amount / tick_rate
    for name, length, limit, decimals in _LENGTH[::-1]:
        if decimals is None or not allow_decimals:
            current = int(time_elapsed // length)
        else:
            current = round(time_elapsed / length, decimals)
        if limit is not None:
            current %= limit

        if current:
            output.append('{} {}{}'.format(current, name, '' if current == 1 else 's'))
            if len(output) == output_length:
                break
    
    if not output:
        output.append('{} {}s'.format(current, name))
    
    if len(output) > 1:
        result = ' and '.join((', '.join(output[:-1]), output[-1]))
    else:
        result = output[-1]

    return result
