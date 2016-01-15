from cbr_db import database


def test_sqldump_table_and_filename():
    assert (database.get_sqldump_table_and_filename('101') ==
            ('f101', 'f101.sql'))

    assert (database.get_sqldump_table_and_filename('102') ==
            ('f102', 'f102.sql'))
