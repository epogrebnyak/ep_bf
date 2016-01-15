"""Access DBF files as stream and write to CSV."""

from .common import change_extension, dump_iter_to_csv, yield_csv_rows
from dbfread import DBF
from collections import OrderedDict
from datetime import datetime

#______________________________________________________________________________
#
#  Access DBF files
#______________________________________________________________________________

# encoding of the dbf files
CODEPAGE = "cp866"

def open_dbf(f):
    return DBF(f, encoding=CODEPAGE)

def get_field_list(f):
    return [d.name for d in open_dbf(f).fields]
                
def dbf_stream(f):
    table = open_dbf(f)
    yield table.field_names
    for record in table:
        yield(list(record.values()))

def kill_itgap_row(gen):
    for row in gen:  
        if row[2] != "ITGAP":
            yield row
            
def write_to_csv(f, filter_func = kill_itgap_row):
    gen1 = dbf_stream(f)
    gen2 = filter_func(gen1)
    c = change_extension(f, "csv")
    dump_iter_to_csv(gen2, c)
    return c

#______________________________________________________________________________
#
#  Modify DBF data streams - OrderedDict and truncating
#______________________________________________________________________________

def yield_csv_as_ordered_dict(f):
    gen = yield_csv_rows(f)
    field_names = next(gen)
    for row in gen:
        yield OrderedDict(zip(field_names, row)) 
    
NULL_CSV_MARKER = '0'
    
def select_fields_from_row(incoming_row_dict, field_names):     
    """Return OD with *field_names* as keys and *incoming_dict* as values, where matched."""
    result_row_dict = OrderedDict.fromkeys(field_names, NULL_CSV_MARKER)
    for k,v in incoming_row_dict.items():
        if k in field_names:
            result_row_dict[k] = v
    return result_row_dict

def yield_csv_subset(f, field_names):
    gen = yield_csv_as_ordered_dict(f)
    for row in gen:
         yield select_fields_from_row(row, field_names)

#______________________________________________________________________________
#
#  Modify DBF data streams - Yeild flat stream from DBF file from 
#______________________________________________________________________________


def get_csv_stream(f, field_names):
    сsv = write_to_csv(f)        
    return yield_csv_subset(сsv, field_names)
    

def yield_by_ts(ts, postfix= None, field_names = None):
        f = ts + postfix + ".dbf"
        return get_csv_stream(f, field_names)  
        

FIELDS_BY_FILETYPE = [
    # short table specification
      { 'postfix' : "_B", 
    'field_names' : ['REGN', 'PLAN', 'NUM_SC', 'A_P', 'IR', 'IV', 'ITOGO', 'DT']}
   
    # long table specification
    ,  {'postfix' : "B1",
    'field_names' : ['REGN', 'PLAN', 'NUM_SC', 'A_P', 'IR', 'IV',  'IITG', 'DT']}
        ]

def yield_flat_stream(ts):
    for definition in FIELDS_BY_FILETYPE:
        gen = yield_by_ts(ts, **definition)
        for row in gen:
            yield row 
            
#______________________________________________________________________________
#
#  Modify DBF data streams - Return dictionaries
#______________________________________________________________________________        


def get_date(isodate):
    return datetime.strptime(isodate, "%Y-%m-%d").date() 

def to_int(x):
    return int(float(x))     

def yield_dicts(ts):
    gen = yield_flat_stream(ts)
    for row in gen:
        row = [x for x in row.values()]
        yield {'regn': to_int(row[0]),
               'plan': row[1],
              'conto': to_int(row[2]),
                'a_p': to_int(row[3]),           
                 'ir': to_int(row[4]),
                 'iv': to_int(row[5]),
              'itogo': to_int(row[6]),
                 'dt': get_date(row[7])
               }        

if __name__ == "__main__":
    
   for i, x in enumerate(yield_dicts('122012')):
        print (x)
