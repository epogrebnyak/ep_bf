"""
   Converts text form files into csv (form 101, 102).
   
   Main converter functions:
       convert_f101_txt2csv(txt_file, csv_file, isodate)
       convert_f102_txt2csv(txt_file, csv_file, isodate)
       wrapper:
       convert_txt2csv(txt_path, form)
    
    Entry point:
       convert_txt_directory_to_csv(form)
       
    Role of other functions:
        make target csv filename
          get_target_csv_path(txt_path, form)
        
        walk througn all txt files for  a given form
          generate_filepaths(form)
"""

import csv
import datetime
import os

from .config_folders import get_private_data_folder, generate_private_data_annual_subfolders
from .date_engine import shift_month_ahead, date2iso, quarter2date, conv_date2quarter
from .global_ini import get_private_data_db_table

def convert_txt2csv(txt_path, form):
    """
    Calls functions to define 'isodate' and 'csv_path' depending on 'txt_path' 
    Selects and calls file converter depending on <form>. 
    """
    isodate = _decompose_private_txt_filename (txt_path, form)
    csv_path = _get_target_csv_path(txt_path, form)
    
    CONVERTERS = {
                  '101': convert_f101_txt2csv,
                  '102': convert_f102_txt2csv
                }
    
    converter_func = CONVERTERS[form] 
    converter_func(txt_path, csv_path, isodate)
    
def _get_parent_dirname(path):
    """
    Returns parent folder stand-alone name.
    E.g. returns '2013' for path = r"D:\git\cbr-data\data.private\101\txt\2013\f101_12.txt"
    """
    parent = os.path.dirname(path)    
    return os.path.split(parent)[1]
 
def _decompose_private_txt_filename (path, form):
    """
    Returns reporting date of file in <path> in ISO format. 
    """
    basename = os.path.basename(path)    
    year = int(_get_parent_dirname(path))
    if form == '101':
        # not-todo: this may be handled using regex 
        # reads from f101_01.txt, f101_12.txt         
        month = int(basename[5:7]) 
        isodate = date2iso(shift_month_ahead(datetime.date(year, month, 1)))        
    if form == '102':  
        # reads from f102_1.txt, f102_4.txt
        quarter = int(basename[5])
        isodate = date2iso(quarter2date(year, quarter))    
    return isodate
    
    
def _get_target_csv_path(txt_path, form):
    """
    Returns csv file path (target file) corresponding to <txt_path> (source file).
    """
    isodate = _decompose_private_txt_filename(txt_path, form)
    csv_dir = get_private_data_folder(form, 'csv')    
    filename = get_private_data_db_table(form) +  "." + isodate 
    return os.path.join(csv_dir, filename)

def get_regn(txt_file):
    """
    Parses the regn code from <txt_file>, returning it.
    """
    MAX_LINES_TO_READ = 20
    lines_read = 0
    
    with open(txt_file) as input_file:
        for line in input_file:
            # limits the parsing to the header section
            if lines_read > MAX_LINES_TO_READ:
                break
            
            # look for a line that contains a series of number
            fields = line.split('|')[1:-1]  # ignore first and last
            
            if len(fields) == 5:
                try:
                    numbers = list(map(int, fields))
                    return numbers[3] # regn column
                except ValueError:
                    # not the line we are after, skip                
                    lines_read += 1
    
    raise ValueError("{} deviates from the expected format".format(txt_file))    
    
def convert_f101_txt2csv(txt_file, csv_file, isodate):

    regn = get_regn(txt_file)

    with open(csv_file, 'w') as targetfile:
        writer = csv.writer(targetfile, delimiter='\t', lineterminator = '\n')

        with open(txt_file, 'r') as sourcefile:
            reader = csv.reader(sourcefile, delimiter=' ', skipinitialspace = True)
            is_in_section_a = False
            is_in_section_b = False
            a_p = 0
            
            for row in reader:
                if len(row) > 0:
                    if is_in_section_a == False and row[0] == u"А.": is_in_section_a = True
                    if is_in_section_b == False and row[0] == u"Б.": is_in_section_b = True
                    if is_in_section_a == True and row[0] == u"Актив": a_p = 1
                    if is_in_section_a == True and row[0] == u"Пассив": a_p = 2
                    if is_in_section_b == True: a_p = 0
                    #  print(a_p)
                    
                if len(row) > 0:
                    flag = "|" == row[0][0] and len(row[0]) > 1 and len(row) == 13
                    
                if flag:
                    row[0] = row[0][1:]
                    row[-1] = row[-1][:-1]
                    row.append(isodate)
                    row.append(str(a_p))
                    row.append(regn)
                    writer.writerow(row)
                    
def convert_f102_txt2csv(txt_file, csv_file, isodate):
    """
    Special converter of form 102 text files to csv files.
    Note: skips rows with missing ('X') values.    
    """    
    SKIP_ROWS = 45
    regn = get_regn(txt_file)
    
    year, quarter = conv_date2quarter(isodate)
    
    with open(csv_file, 'w') as targetfile:
        writer = csv.writer(targetfile, delimiter='\t', lineterminator = '\n')

        with open(txt_file, 'r') as sourcefile:
            reader = csv.reader(sourcefile, delimiter='|', skipinitialspace=True)

            for _ in range(SKIP_ROWS):
                next(reader)
            
            for row in reader:
                if len(row) == 8:
                    try:
                        _ = int(row[1]) # just try to parse, should be int
                        fields = list(map(int, row[3:7]))
                        fields.insert(0, isodate)
                        fields.insert(0, regn)                        
                        fields.insert(0, quarter)
                        fields.insert(0, year)
                        writer.writerow(fields)
                    except ValueError:
                        pass


            # print(fields)
            
def generate_filepaths(form):
    """
    Yeilds paths to all available private files of form <form>.
    """
    for dir_, year in generate_private_data_annual_subfolders(form):
        for filename in os.listdir(dir_):
            path = os.path.join(dir_, filename)            
            yield path           
        
def convert_txt_directory_to_csv(form):
    """
    Converts all available private text files of form <form> to csv files.
    """

    print('Converting available private text files to csv...')    
    num_converted = 0
    
    for path in generate_filepaths(form):
        try:
            print("Converting {} to csv...".format(path))
            convert_txt2csv(path, form)
            num_converted += 1
            print("Done.")
        except FileNotFoundError:
            print("File {} (not found)".format(path))
    
    print("-> Converted a total of {} files".format(num_converted))
