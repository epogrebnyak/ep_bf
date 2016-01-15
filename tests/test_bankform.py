import collections

from cbr_db import bankform


def test_get_db_name_single():
    for key in ('raw', 'final'):
        arg = {'raw': True, 'final': False}
        names = bankform.get_db_name(arg)
        assert isinstance(names, collections.Iterable)
        assert isinstance(names[0], str)
        assert len(names) == 1


def test_get_db_name_all():
    arg = {'raw': False, 'final': False}
    names = bankform.get_db_name(arg)
    assert isinstance(names, collections.Iterable)
    assert isinstance(names[0], str)
    assert len(names) == 2
