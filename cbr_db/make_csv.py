from collections import defaultdict
import csv
from datetime import datetime
from functools import reduce
import os

from dbfread import DBF

from .global_ini import FORM_DATA, CODEPAGE
from .config_folders import get_public_data_folder
from .date_engine import isodate2timestamp, iso2date, date2quarter, date2iso


class CustomDBF(DBF):
    """
    Original DBF reader is quite slow (as for 2.0.4).
    We override `_iter_records` for better reading speed.
    It's about 2 times faster on `11 2015-12-01` dataset.
    """

    def __init__(self, filename, encoding=None, selected_fields=None):
        """
        Custom constructor contains additional argument `selected_fields`.
        It is used to narrow set of fields at the lowest level possible.
        """
        super(CustomDBF, self).__init__(filename, encoding=encoding)
        self.__selected_fields = set(selected_fields)

    def _iter_records(self, record_type=b' '):
        """
        WARNING: we re-use the same dict for yielding.
        It means that caller MUST NOT store yielded results as objects.
        Yielded records must be consumed (to CSV, to DB) and discarded.
        """
        with open(self.filename, 'rb') as infile, self._open_memofile() as memofile:
            # Skip to first record.
            infile.seek(self.header.headerlen, 0)
            field_parser = self.parserclass(self, memofile)
            # We know that our data are mostly numbers, strings and dates,
            # so we can keep local dict for parsing functions.
            parse = defaultdict(lambda x: field_parser.parse)
            parse.update({
                'N': field_parser.parseN,
                'C': field_parser.parseC,
                'D': field_parser.parseD,
            })
            # Shortcuts for speed
            skip_record = self._skip_record
            read = infile.read
            seek = infile.seek
            fields = self.fields
            for field in fields:
                field._sel = (field.name in self.__selected_fields)
            # Squash fields: combine N consecutive unused fields into one.
            # This allows efficient skipping of unused fields by seek().
            fields = self.__squash(fields)
            # Reuse the same dict for speed.
            items = {}
            while True:
                sep = read(1)
                if sep == record_type:
                    for field in fields:
                        if field._sel:
                            items[field.name] = parse[field.type](field, read(field.length))
                        else:
                            seek(field.length, 1)
                    yield items
                elif sep in (b'\x1a', b''):
                    # End of records.
                    break
                else:
                    skip_record(infile)

    @staticmethod
    def __squash(fields):
        """
        Combines N consecutive unused (_sel == False) fields into one fake long field.
        Returns squashed list of fields.
        """
        def squash(fields, field):
            if fields and not fields[-1]._sel and not field._sel:
                fields[-1].length += field.length
            else:
                fields.append(field)
            return fields
        return list(reduce(squash, [[]] + fields))


def get_records(dbf_filename, field_name_selection):
    """
    WARNING: we re-use the same dict for yielding.
    It means that caller MUST NOT store yielded results as objects.
    Yielded records must be consumed (to CSV, to DB) and discarded.
    """
    # Use CustomDBF for speed
    table = CustomDBF(dbf_filename, encoding=CODEPAGE,
                      selected_fields=field_name_selection)
    # Don't iterate and yield, return an iterator directly - it's much faster
    return iter(table.records)


def make_csv_filename(dbf_filename, db_table_name):
    if db_table_name is None:
        #  rename if db_table_name not supplied
        csv_filename = dbf_filename[:-4] + ".csv"
    else:
        # make dbf filename same as table name, put date information in extension
        csv_filename = db_table_name + "." + dbf_filename[:-4]

    return csv_filename

def make_dbf_filename(isodate, postfix, form):
    ts = isodate2timestamp(form, isodate)
    dbf_filename = ts + postfix + ".DBF"
    return dbf_filename

def _write_csv_by_path(dbf_path, csv_path, field_name_selection, form, dt):
    # not todo - make time wrapper
    startTime = datetime.now()
    # ----------------------
    with open(csv_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter='\t', lineterminator='\n',  fieldnames=field_name_selection)
        writer.writeheader()
        
        n_skipped = 0

        for rec_dict in get_records(dbf_path, field_name_selection):
            skip = False
            
            if form == "101":
                if "NUM_SC" in field_name_selection and rec_dict["NUM_SC"] != "ITGAP":
                    for c in ("IITG", "ITOGO"):
                        if c in field_name_selection:
                            rec_dict[c] = int(rec_dict[c])
                else:
                    skip = True
            
            if form == "102":
                # fix (fill with zeros) SIM_R and SIM_V
                for c in ("SIM_R", "SIM_V"):
                    if c in field_name_selection and rec_dict[c] is None:
                        rec_dict[c] = 0
                
                # add date, year and quarter
                rec_dict["DT"] = date2iso(dt)
                
                qt_year, qt_month = date2quarter(dt)                
                rec_dict["YEAR"] = qt_year
                rec_dict["QUART"] = qt_month
                    
            if skip:
                n_skipped += 1
            else:
                writer.writerow(rec_dict)
    # ----------------------
    msg = "Time elapsed: {0}".format(datetime.now() - startTime)

    # not todo: may also write skipped rows to separate file
    if n_skipped > 0:
        msg = msg + "\nSkipped writing {0} records to file.".format(n_skipped)

    print(msg)

def _write_csv(dbf_filename, field_name_selection, db_table_name, dbf_dir, csv_dir, form,
               dt):
    csv_filename = make_csv_filename(dbf_filename, db_table_name)
    csv_path = os.path.join(csv_dir, csv_filename)
    dbf_path = os.path.join(dbf_dir, dbf_filename)

    if os.path.isfile(dbf_path):
        print("Converting {0} to csv file {1}".format(dbf_filename, csv_filename))
        _write_csv_by_path(dbf_path, csv_path, field_name_selection, form, dt)
    else:
        print("File {0} not found".format(dbf_filename))

def dbf2csv(isodate, form):
    """
    Converts DBF files to CSV files with SQL table name as basename and date as extension.
    This filename format allows using fast mysqlimport to read CSV files to database.
    Function will iterate over subforms in each form.
    """
    for subform, info in FORM_DATA[form].items():
        _write_csv(dbf_filename=make_dbf_filename(isodate, info['postfix'], form),
                   field_name_selection=info['dbf_fields'],
                   db_table_name=info['db_table'],
                   dbf_dir=get_public_data_folder(form, 'dbf'),
                   csv_dir=get_public_data_folder(form, 'csv'),
                   form=form,
                   dt=iso2date(isodate))

def list_csv_filepaths_by_date(isodate, form):
    for subform, info in FORM_DATA[form].items():
        dbf_filename = make_dbf_filename(isodate, info['postfix'], form)
        csv_filename = make_csv_filename(dbf_filename, info['db_table'])
        csv_dir = get_public_data_folder(form, 'csv')
        csv_path = os.path.join(csv_dir, csv_filename)
        yield csv_path