"""
This file configures:
   1. data directories
   2. path to archive executables
   3. paths to mysql
   
   # variables imported to other modules from here:
   # PATH, MYSQL_PATH
   # variables with a '_' prefix should not be imported or used outside global_ini
"""
import configparser
import os
from os import path

from .date_engine import get_current_year


# This file is in subfolder of _PROJECT_ROOT_DIR, so do path.dirname() twice
_PROJECT_ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))

def get_absolute_path(user_path, root_path = _PROJECT_ROOT_DIR ):    
    """
    Adjusts <user_path> to project root directory <_PROJECT_ROOT_DIR> if <path> is relative.
    If <user_path> is absolute, returns itself.
    """
    if path.isabs(user_path):
        return user_path
    else:
        return path.join(root_path, user_path)

# Load user settings
config = configparser.ConfigParser()
config.read('../settings.cfg')

# Read the directories chosen by the user, adjusting them to the project root if necessary

_PUBLIC_DATA_FOLDER = get_absolute_path(
    config.get('data directories', 'public_data_folder', fallback='data.downloadable')
)

_PRIVATE_DATA_FOLDER = get_absolute_path(
    config.get('data directories', 'private_data_folder', fallback='data.private')
)

_OUTPUT_FOLDER = get_absolute_path(
    config.get('data directories', 'output_folder', fallback='output')
)

# Form directories
def _get_dir_structure(folder, form):
    return {
        'rar': path.join(folder, form, 'rarzip'),
        'dbf': path.join(folder, form, 'dbf' ),
        'csv': path.join(folder, form, 'csv'),
        'txt': path.join(folder, form, 'txt')
    }

def _get_public_dirs(form):
    return _get_dir_structure(_PUBLIC_DATA_FOLDER, form)

def _get_private_dirs(form):
    return _get_dir_structure(_PRIVATE_DATA_FOLDER, form)

def _get_global_dirs():
    return {
        'database': path.join(_PROJECT_ROOT_DIR, 'database', 'db_dump'),
        'alloc'   : path.join(_PROJECT_ROOT_DIR, 'database', 'alloc'  ),
        'tables'  : path.join(_PROJECT_ROOT_DIR, 'database', 'tables' ),
        'output'  : _OUTPUT_FOLDER
    }

def get_public_data_folder(form, subfolder_tag):
    """
    Return absolute path to public data folder.
    """
    dir_list = _get_public_dirs(form)
    return dir_list[subfolder_tag]

def get_private_data_folder(form, subfolder_tag):
    """
    Return absolute path to private data folder.
    """
    dir_list = _get_private_dirs(form)
    return dir_list[subfolder_tag]
    
def generate_private_data_annual_subfolders(form, subfolder_tag='txt'):
    """
    Will return paths 2015
        D:\git\cbr-data\data.private\101\txt\2004
        ...
        D:\git\cbr-data\data.private\101\txt\2015
    
    """
    for year in range(2004, get_current_year()+1):        
        main_folder = get_private_data_folder(form, subfolder_tag)
        dir_ = os.path.normpath(
                                os.path.join(main_folder,str(year))
                                )
        # print(dir_)
        if os.path.isdir(dir_):
            print("Exists:" + dir_)
            yield dir_, year    
            

def get_global_folder(folder_tag):
    """
    Return absolute path to global folder with database files.
    """
    dir_list = _get_global_dirs()
    return dir_list[folder_tag]

def get_output_folder():
    """
    Returns 'output' folder used to write final files.
    This function guarantees that folder exists and is writable.
    """   
    path = get_global_folder("output")
    if not os.path.isdir(path):
        os.makedirs(path)
    mode = os.stat(path).st_mode & 0o777
    new_mode = mode | 0o222  # must be writable by all
    if new_mode != mode:
        os.chmod(path, new_mode)
    return path

def generate_all_folder_names():
    """
    Generator that yields names of the folders that shall be created by the
    program, such as the location of the downloaded files.
    See create_default_directories() for more information.
    """
    for frm in  ('101', '102'):
        for dir_ in _get_public_dirs(frm).values():
            yield dir_
            
        for dir_ in _get_private_dirs(frm).values():
            yield dir_
        
    for dir_ in _get_global_dirs().values():
            yield dir_

def create_default_directories(verbose=False):
    """
    Creates the default directories required by the application. 
    Some directories can be configured by the user in <settings.cfg> 
    in the project root directory.
    """
    if verbose:
        print("Directories used:")
    
    for dir_ in generate_all_folder_names():
        os.makedirs(dir_, exist_ok=True) 
       
        if verbose:
            print(dir_)


############################## Executables directories [zip/rar path]

# default paths depends on the operating system
if os.name == 'posix':
    # on GNU / Linux, the executables will be already the path. If not, the
    # user can specify it in the configuration.
    _DEFAULT_PATH = {
        'unrar': 'unrar',
        'z7': '7z'
    }
else:
    _DEFAULT_PATH = {
        'unrar': path.join(_PROJECT_ROOT_DIR, 'bin', 'unrar.exe'),
        'z7': path.join(_PROJECT_ROOT_DIR, 'bin', '7za')
    }

# user can override the paths by specifying them in settings.cfg
PATH = _DEFAULT_PATH

for key in ('unrar', 'z7'):
    op = config.get('zip/rar path', key, fallback=_DEFAULT_PATH[key])
    for path_option in [op, get_absolute_path(op)]:
        if os.path.isfile(path_option):
            PATH.update({key:path_option})


############################## Executables directories [mysql]

_DEFAULT_MYSQL_PATH_STRING = r'C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin, C:\MySQL\bin'

# reads a path list from the configuration, using ',' as the separator
path_string = config.get('mysql', 'path', fallback=_DEFAULT_MYSQL_PATH_STRING)
MYSQL_PATH = list(map(lambda s: s.strip(), path_string.split(',')))