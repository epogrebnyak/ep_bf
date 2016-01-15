import os

import pytest

from cbr_db import bankform
from cbr_db import conn


@pytest.yield_fixture
def cwd(scope='module', autouse=True):
    old_cwd = os.getcwd()
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    yield path
    os.chdir(old_cwd)


def get_regns():
    # TODO: we are using working database for tests. This is bad!
    return sorted([
        t[0] for t in 
        conn.execute_sql("SELECT regn FROM cfg_regn_in_focus",
                         database="dbf_db")
    ])


def test_regn_list_one():
    bankform.main("make dataset 101 2015 --regn=964".split(' '))
    assert get_regns() == [964]


def test_regn_list_many():
    bankform.main("make dataset 101 2015 --regn=2,5,3,1".split(' '))
    assert get_regns() == [1, 2, 3, 5]


def test_regn_all():
    """warning: this tests depends on the current database contents, that
    must be populated."""
    bankform.main("make dataset 101 2015".split(' '))
    regns1 = get_regns()

    bankform.main("make dataset 101 2015 --regn-all".split(' '))
    regns2 = get_regns()

    assert regns1 == regns2


def test_regn_list_file(cwd):
    regn_file = os.path.join(cwd, 'regn.txt')
    bankform.main(['make', 'dataset', '101', '2015', '--regn-file={}'.format(regn_file)])
    assert get_regns() == [10, 11, 12, 13, 14, 15]
