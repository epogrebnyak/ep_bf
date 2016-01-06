"""Converts CSV to Excel files (xlsx)

Usage:
  make_xlsx.py <csv_file> <xlsx_file> [--delimiter=<delim>] 
  make_xlsx.py batch [--delimiter=<delim>]  
  
"""
import csv
from datetime import datetime
import os

import xlsxwriter

from .docopt import docopt


def get_cell_format(workbook):
    """
    Cell format dictionary. 
    """   
    format_ = workbook.add_format()
    format_.set_font_name('Arial')
    format_.set_font_size(8)
    return format_
    
def get_date_format(workbook):
    """
    Number format dictionary. 
    """ 
    format_ = get_cell_format(workbook)
    format_.set_num_format('dd.mm.yyyy')
    return format_

def simple_write_csv_to_new_xlsx_sheet(workbook, sheet_name, csv_path):
    """
    Basic functionality to write csv to xlsx workbook sheet.
    """
    cell_format = get_cell_format(workbook)

    with open(csv_path) as f:
        reader = csv.reader(f, delimiter=delimiter)
        sheet = workbook.add_worksheet(sheet_name)
        for i, row in enumerate(reader):
            for j, val in enumerate(row):
                sheet.write(i, j, val, cell_format)

def _write_csv_to_new_xlsx_sheet(workbook, sheet_name, csv_path, delim = '\t'):
    """
    Writes data from csv file to a xlsx workbook sheet.
    Assumes some pre-formatting (e.g. first row is dates).
    """

    COL_WIDTH  = 9.5 
    ROW_HEIGHT = 11.25   
    
    with open(csv_path) as f:
        reader = csv.reader(f, delimiter = delim)
        sheet = workbook.add_worksheet(sheet_name)                
        for i, row in enumerate(reader):
            # cell formatting - adjust row height and apply font size and family            
            sheet.set_row(i, ROW_HEIGHT)
            cell_format = get_cell_format(workbook)            
            for j, val in enumerate(row):
                if i == 0: 
                    # cell formatting  - adjust column width                
                    sheet.set_column(j, j, COL_WIDTH)                     
                    if j > 2:
                        date_time = datetime.strptime(val, '%Y-%m-%d')
                        val = date_time
                        cell_format = get_date_format(workbook)                      
                if i > 0 and j > 0: 
                    val = int(val)
                sheet.write(i, j, val, cell_format)      

def getwd():    
    """
    Returns current dicrectory.
    """   
    return os.path.dirname(os.path.abspath(__file__))
    
def make_xlsx(directory = getwd()):
    """
    Creates XLXS file based on CSV files. All files are in <directory>.    
    """   
    xlsx_filename = "output.xlsx" 
    csv_filenames = ["tmp_output_ir.txt", "tmp_output_iv.txt", "tmp_output_itogo.txt"]
    sheet_names = ["csv_ir", "csv_iv", "csv_itogo"]
    
    xlsx_path = os.path.join(directory, xlsx_filename)     
    csv_paths = [os.path.join(directory, f) for f in csv_filenames ]
    
    workbook = xlsxwriter.Workbook(xlsx_path)
    for csv_path, sheet_name in zip(csv_paths, sheet_names):
        _write_csv_to_new_xlsx_sheet(workbook, sheet_name, csv_path)
    workbook.close()
        
if __name__ == '__main__':              
    args = docopt(__doc__)
    delimiter = args['--delimiter'] or '\t'
    
    if args['batch']:
         make_xlsx()
    
    else:
        csv_path  = args['<csv_file>']
        xlsx_path = args['<xlsx_file>']
        
        workbook = xlsxwriter.Workbook(xlsx_path)
        _write_csv_to_new_xlsx_sheet(workbook, "Sheet1", csv_path)
        workbook.close()
        
                
