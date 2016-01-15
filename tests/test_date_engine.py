from datetime import date

import pytest

from cbr_db import date_engine


def test_shift_month_ahead():
    assert date_engine.shift_month_ahead(date(2015, 5, 1)) == date(2015, 6, 1)

    assert date_engine.shift_month_ahead(date(2012, 12, 1)) == date(2013, 1, 1)

    with pytest.raises(ValueError):
        date_engine.shift_month_ahead(date(2013, 3, 31))


def test_shift_month_behind():
    assert date_engine.shift_month_behind(date(2015, 12, 1)) == date(2015, 11, 1)
    
    assert date_engine.shift_month_behind(date(1988, 7, 1)) == date(1988, 6, 1)

    assert date_engine.shift_month_behind(date(2012, 1, 1)) == date(2011, 12, 1)

    with pytest.raises(ValueError):
        date_engine.shift_month_behind(date(2013, 3, 31))


def test_get_date_range():
    assert (date_engine.get_date_range(date(2012, 3, 1), date(2012, 5, 1)) ==
            [date(2012, 3, 1), date(2012, 4, 1), date(2012, 5, 1)])

    assert (date_engine.get_date_range(date(1988, 11, 1), date(1989, 1, 1)) ==
            [date(1988, 11, 1), date(1988, 12, 1), date(1989, 1, 1)])


def test_zero_padded_month():
    assert date_engine.zero_padded_month(5) == "05"
    assert date_engine.zero_padded_month(11) == "11"


def test_datetime2iso():
    assert date_engine.date2iso(date(1988, 1, 1)) == '1988-01-01'
    assert date_engine.date2iso(date(2015, 5, 23)) == '2015-05-23'


def test_iso2date():
    assert date_engine.iso2date('1988-01-01') == date(1988, 1, 1)
    assert date_engine.iso2date('2015-05-23') == date(2015, 5, 23)


def test_date2timestamp():
    assert date_engine.date2timestamp(101, date(2014, 5, 3)) == '042014'
    assert date_engine.date2timestamp('101', date(2014, 1, 5)) == '122013'


def test_isodate2timestamp():
    assert date_engine.isodate2timestamp(101, '2014-05-03') == '042014'

    assert date_engine.isodate2timestamp('101', '2014-01-05') == '122013'


def test_quarter2date():
    assert date_engine.quarter2date(2000, 1) == date(2000, 4, 1)
    assert date_engine.quarter2date(2000, 2) == date(2000, 7, 1)
    assert date_engine.quarter2date(2000, 3) == date(2000, 10, 1)
    assert date_engine.quarter2date(2000, 4) == date(2001, 1, 1)


def test_date2quarter():
    assert date_engine.date2quarter(date(2000, 4, 1)) == (2000, 1)
    assert date_engine.date2quarter(date(2000, 7, 1)) == (2000, 2)
    assert date_engine.date2quarter(date(2000, 10, 1)) == (2000, 3)
    assert date_engine.date2quarter(date(2001, 1, 1)) == (2000, 4)
