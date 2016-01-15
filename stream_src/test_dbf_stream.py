# -*- coding: utf-8 -*-
"""
Testing of dbf_stream.py based on sample files 122012_B.DBF and 122012B1.DBF 

Created on Sat Aug 15 19:09:58 2015
"""
import os

import pytest

from .dbf_stream import yield_csv_subset, write_to_csv, get_field_list, NULL_CSV_MARKER


@pytest.yield_fixture(scope='module', autouse=True)
def cwd():
    old_cwd = os.getcwd()
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    yield path
    os.remove(os.path.join(path, '122012B1.csv'))
    os.chdir(old_cwd)


def test_yield_by_selection():
    c = "122012_B.csv"
    z = next(yield_csv_subset(c, ["NUM_SC", "SOME_EXTRA"]))
    assert z["SOME_EXTRA"] ==  NULL_CSV_MARKER 
  

fi = "122012_B.DBF"
fii = "122012B1.DBF"
    
def test_colnames():
    assert get_field_list(fi) == ['REGN', 'PLAN', 'NUM_SC', 'ITOGO', 'A_P', 'DT']
    assert get_field_list(fii) == ['REGN', 'PLAN', 'NUM_SC', 'A_P', 'VR', 'VV', 'VITG', 'ORA', 'OVA', 'OITGA', 
                                   'ORP', 'OVP', 'OITGP', 'IR', 'IV', 'IITG', 'DT', 'PRIZ']
    
def get_reference_value(f, field_names):
    сsv = write_to_csv(f)        
    gen = yield_csv_subset(сsv, field_names)
    return dict((k,v) for k,v in next(gen).items())    

def test_prep():
    field_names_i  = ['REGN', 'PLAN', 'NUM_SC', 'A_P', 'IR', 'IV', 'ITOGO', 'DT']
    field_names_ii = ['REGN', 'PLAN', 'NUM_SC', 'A_P', 'IR', 'IV',  'IITG', 'DT']
    assert get_reference_value(fi,  field_names_i)  == {'A_P': '2', 'IV': '0',   'PLAN': 'А', 'ITOGO': '1558500.0', 'REGN': '101', 'NUM_SC': '10207', 'IR': '0',      'DT': '2013-01-01'}
    assert get_reference_value(fii, field_names_ii) == {'A_P': '1', 'IV': '0.0', 'PLAN': 'А',  'IITG': '5970.0',    'REGN': '1.0', 'NUM_SC': '10605', 'IR': '5970.0', 'DT': '2013-01-01'}   