from urllib import request, parse
from urllib.error import URLError
from os import path, makedirs
import shutil
import arrow

def get_date(url):
    """
    Returns the modification date of the file pointed by *url* without
    downloading it.
    """
    url = request.urlopen(url)
    date = url.info().get('Last-Modified')
    return arrow.get(date, 'ddd D MMM YYYY HH:mm:ss')

def get_filename(url, dir_=""):
    """
    Returns the name of the file pointed by url, when put in directory *dir*
    """
    return path.join(dir_, path.basename(parse.urlsplit(url).path))

def download(url, dir_, force=False, verbose=True):
    """
    Downloads the file pointed by *url* into directory *dir*. Unless *force* is True,
    the file will not be downloaded if there is a local up-to-date file in *dir_*.
    """
    filename = get_filename(url, dir_)
    local_url = r"file://" + filename
    mod_remote = get_date(url)

    try:
        mod_local = get_date(local_url)
    except URLError:
        # local file does not exists
        force = True

    if force or mod_remote > mod_local:
        if verbose:
            print("-> Downloading {}".format(url))
        
        makedirs(dir_, exist_ok=True)
        with request.urlopen(url) as response, open(filename, 'wb') as out:
            shutil.copyfileobj(response, out)  # downloads in chunks
    else:
        if verbose:
            print("-> Skipping {} (already downloaded)".format(url))