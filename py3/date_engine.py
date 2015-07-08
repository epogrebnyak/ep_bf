import datetime

def get_current_year(): 
    """
    Returns current year
    """   
    return (datetime.datetime.today().year) 

   
###########################################################
   
def date2iso(date):
    """
    Wrapper for date format conversion.
    Similar to .isoformat() method.
    """
    return datetime.date.strftime(date, "%Y-%m-%d")

def iso2date(iso_date):
    """
    Wrapper for date format conversion
    """
    return datetime.datetime.strptime(iso_date, "%Y-%m-%d").date()
        
###########################################################
    
def _verify_start_of_month(*args):
    """
    Checks if day of date is 01, raises error otherwise.
    Note: this is now a double check as cli_dates.get_date_endpoints() forces day to 1, occurrence of other day is unlikely.
    """
    for date in args:
        if date.day != 1:
            raise ValueError("All dates must be at the start of the month (day 1)")

def shift_month_ahead(date):
    """
    Returns date one month ahead of <date> arguement with day set to 1.
    """
    _verify_start_of_month(date)

    if date.month < 12:
        date = date.replace(month=date.month + 1)
    else:
        date = date.replace(month=1)
        date = date.replace(year=date.year + 1)

    return date
    
def shift_month_behind(date):
    """
    Returns date one month behind of <date> arguement with day set to 1.
    """
    _verify_start_of_month(date)

    if date.month > 1:
        date = date.replace(month=date.month - 1)
    else:
        date = date.replace(month=12)
        date = date.replace(year=date.year - 1)

    return date

def get_date_range(start_date, end_date, step=1):
    """
    Returns a list with dates between <start_date> and <end_date> including end point dates.
    """  
    date_range = []
    date = start_date

    while date <= end_date:
        date_range.append(date)
        
        for s in range(step):                
            date = shift_month_ahead(date)

    return date_range    

###########################################################
    
def isodate2timestamp(form, isodate):
    """
    Returns timestamp string used in <form> filenames based on <isodate> argument.
    """
    dt = iso2date(isodate)
    return date2timestamp(form, dt)

def date2timestamp(form, dt):
    """
    Returns timestamp string used in <form> filenames based on <dt> argument.    
    """
    form = str(form)    
    
    # Risk: must keet this hardcoded, different code will apply to different <form>
    if form == "101":
        # filename timestamp is one month behind
        if dt.month == 1:
            year = dt.year - 1
            month = 12
        else:
            year = dt.year
            month = dt.month - 1
        return zero_padded_month(month) + str(year)
    elif form == '102':
        # deals in quarters
        year, quarter = date2quarter(dt)
        return "{}{}".format(quarter, year)
    else:
        raise ValueError("Form not supported: " + form)

def zero_padded_month(month):
    """
    Returns 01, 02, ... 10, 11, 12.
    """    
    return "0" + str(month) if month < 10 else str(month)
        
def date2quarter(date):
    """
    Returns a (year, quarter) tuple from a <date> object.
    Note: the first quarter corresponds to month 4, not 1.
    """
    date = shift_month_behind(date)
    return date.year, date.month // 3

def quarter2date(year, quarter):
    """
    Returns a date from <year> and <quarter>.
    Note: the first quarter corresponds to month 4, not 1.
    """
    dt = datetime.date(year=year, month=quarter * 3, day=1)
    return shift_month_ahead(dt)