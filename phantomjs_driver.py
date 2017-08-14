import scandir
import sys
import urllib.request
import requests
from os import getlogin, system
from os.path import join
from sys import platform
import zipfile


class PhantomJS_driver(object):
    """
    Class that controls phanthom js driver

    Note:
        Do not include the 'self' parameter in the 'Args' section
    Attributes:
        curr_os (str): Current operating system
        driver (str): Format of driver depending on OS
    """

    def __init__(self):
        self.curr_os = platform
        if self.curr_os == 'win32':
            self.driver = 'phantomjs.exe'

        elif self.curr_os == 'linux':
            self.driver = 'phantomjs'

        elif self.curr_os == 'darwin':
            self.driver = 'phantomjs'

    def get_path(self):
        """
        Method that searches OS and finds phanthom js driver file then returns it if it exists

        :return: path of phanthom js driver on OS
        """

        # If operating system is Windows then begin search using scandir at User level
        if self.curr_os == 'win32':
            try:
                return self.driver_path

            except AttributeError:

                for root, dirs, files in scandir.walk("C:\\Users\\" + getlogin()):
                    print('Searching PC for PhantomJS driver:', root)
                    if self.driver in files:
                        self.driver_path = join(root, self.driver) # Joins current path and driver name to make path
                        print('Found PhantomJS driver:',self.driver_path)
                        return self.driver_path

        # If operating system is Linux then begin search using scandir at home level
        if self.curr_os == 'linux':
            for root, dirs, files in scandir.walk("/home"):
                print('searching:', root)
                if self.driver in files or self.driver in root:
                    self.driver_path = join(root, self.driver)  # Joins current path and driver name to make path
                    print('found:',self.driver_path)
                    return self.driver_path

        if self.curr_os == 'darwin':
            for root, dirs, files in scandir.walk("/Users/"):
                print('searching:', root)
                if self.driver in files or self.driver in root:
                    self.driver_path = join(root, self.driver)  # Joins current path and driver name to make path
                    print('found:', self.driver_path)
                    return self.driver_path

    def download_driver(self):
        """
        Downloads most recent phanthom js driver depending on OS

        :return: None
        """
        # If OS is Windows
        url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip" # Recent PhantomJS driver
        zip_target_path = 'C:\\Users\\' + getlogin() + '\\Downloads\\phantomjs-2.1.1-windows.zip' # Download path
        link = url
        file_name = "phantomjs-2.1.1-windows.zip"
        with open(file_name, "wb") as f:
            print
            "Downloading %s" % file_name
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        urllib.request.urlretrieve(url, zip_target_path)  # Downloads most recent phantom js driver to downloads directory
        zip_ref = zipfile.ZipFile(zip_target_path,'r')
        file_target_path = 'C:\\Users\\' + getlogin() + '\\Downloads\\'
        zip_ref.extractall(file_target_path)
        zip_ref.close()

        # If OS is Linux
        if self.curr_os == 'linux':
            system('wget -N https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip -P ~/Downloads')
            system('7z x ~/Downloads/phantomjs-2.1.1-windows.zip')
