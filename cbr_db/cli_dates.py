"""
Usage:
   cli_dates.py pass <form> (<timestamp1> [<timestamp2>] | --all-dates)

   Notes:
   (1) Format for monthly timestamps is YYYY-MM-DD (ISO), YYYY-MM, DD.MM.YYYY, MM.YYYY or YYYY
   (2) Format for quarterly timestamps is [1-4]q[YYYY], [1-4]Q[YYYY], [YYYY]q[1-4], [YYYY]Q[1-4]
"""

from datetime import datetime, date

from .docopt import docopt
from .date_engine import get_date_range, shift_month_ahead

def get_date_from_quarter_string(timestamp):
    """
    Returns day 1 of quarter following <timestamp> argument. 
    Example: for timestamp = '1q2015' returns date object with date '2015-04-01'
    <timestamp describes a date using a quarter-year  notation [1-4]q[YYYY], [1-4]Q[YYYY], [YYYY]q[1-4], [YYYY]Q[1-4]
    <timestamp> examples: 1Q2005, 2q2005, 2005Q3, 2005q4
    """
    # not todo: may use regex to catch year/quarter
    
    # break into (year, quarter) or (quarter, year)
    parts = timestamp.upper().split('Q')

    if len(parts) != 2:
        # not in a quarter format, break
        return None
    # make sure the order is (year, quater), swap to this format if otherwise
    if len(parts[0]) == 1:
        parts[0], parts[1] = parts[1], parts[0]

    # convert to integer checking the range
    year, quarter = int(parts[0]), int(parts[1])
    if quarter not in range(1, 5):
        raise ValueError("Quarter must be 1, 2, 3 or 4")

    # first quarter: month 4. last quarter: first month of next year
    month = quarter * 3
    dt = date(year=year, month=month, day=1)
    return shift_month_ahead(dt), "quarter"

# new formatters can be added by appending to DATE_FORMATS (text patterns) and
# to SPECIAL_FORMATS (functions that accepts one string argument)
DATE_FORMATS = ['%Y', '%d.%m.%Y', '%m.%Y', '%Y-%m', '%Y-%m-%d']
SPECIAL_FORMATS = [get_date_from_quarter_string]

def try_format(string, fmt):
    """
    Attempts to parse <string> with date <fmt> (format).
    """
    z = None
    try:
        z = datetime.strptime(string, fmt)
        z = z.date()
    except ValueError:
        pass

    return z, fmt

def get_date(string, formats=DATE_FORMATS, special_formats=SPECIAL_FORMATS):
    """
    Parses <string> as date using several predefined text <formats> and <special_formats> functions,
    returning the date and the its matching format.
    """

    # tries the pattern formats one by one up to the first that parses the date
    for fmt in formats:
        parse_output = try_format(string, fmt)
        if parse_output[0]: return parse_output

    # tries the special formats one by one, same as above. special_format is a function.
    for special_format in special_formats:
        parse_output = special_format(string)
        if parse_output[0]: return parse_output

def shift_month_to_quarter_start(month):
    """
    Shifts <month> to start of quarter. Function used to obtain valid quarter reporting date. 
    Always returns 1, 4, 7 or 10:
    month | result
    1 1
    2 1
    3 1
    4 4
    5 4
    6 4
    7 7
    8 7
    9 7
    10 10
    11 10 
    12 10 
    """
    # Note: former name 'get_last_quarter_month' contradicted function algorithm.
    #"""
    #Returns the last completed quarter from <month>. For example, if the
    #month is 1, 2 or 3, the last completed quarter was at month 1.
    #Note: always returns month 1, 4, 7 or 10.
    #"""
    quarter = (month - 1) // 3
    return quarter * 3 + 1

def get_next_quarter_end_date(dt):
    """
    Returns the date corresponding to the next quarter end from <dt>.
    For example, if the current month is 1, it is currently in a valid
    quarter end. Months 2 and 3 would be changed to 4.
    """
    while (dt.month - 1) % 3 != 0:
        dt = shift_month_ahead(dt)

    return dt

def get_last_date_in_year(dt, form):
    """
    Cap last month in year with current month. Returns a date with day 01.
    Example: In June 2015 will return 2015-06 for dt = 2015-12.
    In forms with quarter notation, returns the last valid quarter.
    """
    current_date_day_1 = datetime.today().replace(day=1).date()
    current_year_dec1_date = dt.replace(month=12)
    dt = min(current_date_day_1, current_year_dec1_date)

    if form == '102':  # use quarter notation
        if current_year_dec1_date == dt:
            # we can get the end of the 4 quarter that is in the next year
            dt = dt.replace(year=dt.year + 1, month=1)
        else:
            # go back to the last valid quarter reporting date
            dt = dt.replace(month=shift_month_to_quarter_start(dt.month))

    return dt

def get_date_range_from_command_line(args):
    """
    Returns date range specified in command line as a list of dates in iso format.
    """
    s, e = get_date_endpoints(args)
    step = 1

    if args['<form>'] == '102':
        step = 3

    if s and e:
        return [d.isoformat() for d in get_date_range(s, e, step)]

def get_date_endpoints(args):
    """
    Returns start and end of date range specified in command line.
    """
    s = None  # start date
    e = None  # end date
    form = args['<form>']

    if args['--all-dates']:
        # Risk: hard-coded constant
        s = date(2004, 2, 1)
        e = date.today().replace(day=1)

    # process first timestamp
    if args['<timestamp1>'] is not None:
        ts1, f1 = get_date(args['<timestamp1>'])
        s = ts1
        if f1 == "%Y":
            e = get_last_date_in_year(ts1, form)
        else:
            e = s

        if form == '102':
            # first quarter starts from month 4
            if f1 == "%Y":
                s = s.replace(month=4)

            # get current or next valid quarter
            s = get_next_quarter_end_date(s)

    # process second timestamp
    if args['<timestamp2>'] is not None:
        ts2, f2 = get_date(args['<timestamp2>'])
        if f2 == "%Y":
            e = get_last_date_in_year(ts2, form)
        else:
            e = ts2

    if s and e and (s.day != 1 or e.day != 1):
        print('Warning: must always use start of the month dates (day 1). Force setting day to 1 in argument dates.')
        s = s.replace(day=1)
        e = e.replace(day=1)

    return s, e

if __name__ == '__main__':
    args = docopt(__doc__)
    d_range = get_date_range_from_command_line(args)
    print("Start date:", d_range[0])
    print("End date:",   d_range[-1])
    print("Date list:",  d_range)
