import datetime
import sys

from .date_engine import iso2date, zero_padded_month
from .config_folders import get_public_data_folder
from .download import download, URLError


def download_form(isodate_input, form_input):
    """
    Download archive file for specific date and form type to a local folder
    """
    url = _get_url(isodate=isodate_input, form=form_input)
    dir_ = get_public_data_folder(form_input, 'rar')
    
    try:    
        download(url, dir_)
    except URLError as e:
        print('Skipping download of form {} data.\nReason: {}'.format(
            form_input, str(e)))
    
def _get_url(date=None, isodate=None, form=None):
    """
    Creates URL based on date for forms 101 and 102
    TODO: remove harcoded form check
    """
    form = str(form)    
    
    if form in ('101', '102'):
        return "http://www.cbr.ru/credit/forms/" + get_ziprar_filename(date, isodate, form)
    else:
        raise ValueError('Form {} not supported yet.'.format(form))

def get_ziprar_filename(date=None, isodate=None, form=None):
    if isodate is not None:
        date = iso2date(isodate)
    elif date is None:
        return None

    # date is now assumed to be defined in datetime, not ISO format
    month = zero_padded_month(date.month)
    year = date.year
    extension = _get_extension(date)
    
    form = str(form)

    if form in ('101', '102'):
        return "{}-{}{}01.{}".format(form, year, month, extension)
    else:
        raise ValueError('Form {} not supported yet.'.format(form))

def _get_extension(date):
    # dbf files are avaialble since Feb-2004. They are in zip format up to Dec-2008
    zip_start_date = datetime.date(2004, 2, 1)
    zip_end_date = datetime.date(2008, 12, 31)

    if zip_start_date <= date <= zip_end_date:
        return 'zip'

    # dbf files are in rar format stating Jan-2009
    rar_start_date = datetime.date(2009, 1, 1)

    # rar_end_date   = datetime.datetime.now().date().replace(day=1)
    if date >= rar_start_date:
        return 'rar'

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: make_url.py form date"
    form = sys.argv[1]
    date = sys.argv[2]
    print(_get_url(isodate=date, form=form))
