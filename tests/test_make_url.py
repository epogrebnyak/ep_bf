import unittest
from cbr_db import make_url
from datetime import date

class MakeURLTest(unittest.TestCase):
    
    def test_get_extension(self):
        self.assertEqual(None, make_url._get_extension(date(2004, 1, 30)))
        self.assertEqual('zip', make_url._get_extension(date(2004, 2, 10)))
        self.assertEqual('zip', make_url._get_extension(date(2008, 12, 30)))
        self.assertEqual('rar', make_url._get_extension(date(2009, 1, 1)))
    
    def test_get_ziprar_filename(self):
        self.assertEqual(
            make_url.get_ziprar_filename(isodate='2004-03-05', form=101),
            "101-20040301.zip"
        )
        
        self.assertEqual(
            make_url.get_ziprar_filename(isodate='2013-05-01', form=101),
            "101-20130501.rar"
        )
        
        self.assertEqual(
            make_url.get_ziprar_filename(date=date(2004, 3, 5), form=101),
            "101-20040301.zip"
        )
        
        self.assertEqual(
            make_url.get_ziprar_filename(date=date(2013, 5, 1), form=101),
            "101-20130501.rar"
        )
    
    def test_get_url(self):
        self.assertEqual(
            make_url._get_url(isodate='2004-03-05', form=101),
            "http://www.cbr.ru/credit/forms/101-20040301.zip"
        )
        
        self.assertEqual(
            make_url._get_url(isodate='2013-05-01', form='101'),
            "http://www.cbr.ru/credit/forms/101-20130501.rar"
        )
    
if __name__ == '__main__':
    unittest.main()