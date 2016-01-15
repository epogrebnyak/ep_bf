from cbr_db.make_url import get_extension, get_url, get_ziprar_filename
from datetime import date

    
def test_get_extension():
    assert get_extension(date(2004, 1, 30)) is None
    assert 'zip' == get_extension(date(2004, 2, 10))
    assert 'zip' == get_extension(date(2008, 12, 30))
    assert 'rar' == get_extension(date(2009, 1, 1))


def test_get_ziprar_filename():
    assert (get_ziprar_filename(isodate='2004-03-05', form=101) ==
            "101-20040301.zip")
    assert (get_ziprar_filename(isodate='2013-05-01', form=101) ==
            "101-20130501.rar")
    assert (get_ziprar_filename(date=date(2004, 3, 5), form=101) ==
            "101-20040301.zip")
    assert (get_ziprar_filename(date=date(2013, 5, 1), form=101) ==
            "101-20130501.rar")


def test_get_url():
    assert (get_url(isodate='2004-03-05', form=101) ==
            "http://www.cbr.ru/credit/forms/101-20040301.zip")
    assert (get_url(isodate='2013-05-01', form='101') ==
            "http://www.cbr.ru/credit/forms/101-20130501.rar")
