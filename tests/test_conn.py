import collections
from cbr_db import conn


def test_select():
    resp = conn.execute_sql('SELECT 5')
    assert len(resp) == 1
    assert len(resp[0]) == 1
    assert resp[0][0] == 5


def test_return():
    # should return at least 1 result
    resp = conn.execute_sql('SHOW DATABASES')
    assert isinstance(resp, collections.Iterable)
    assert len(resp) > 0
            
    # empty set
    resp = conn.execute_sql('SHOW DATABASES WHERE "Database" = "xASFghd9"');
    assert isinstance(resp, collections.Iterable)
    assert len(resp) == 0
