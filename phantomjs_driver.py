import scandir
import getpass
import urllib.request
from os import getlogin, system
from os.path import join
from sys import platform
import zipfile2


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

                for root, dirs, files in scandir.walk("C:\\Users\\"):
                    print('searching:', root)
                    if self.driver in files:
                        self.driver_path = join(root, self.driver) # Joins current path and driver name to make path
                        print('found:',self.driver_path)
                        return self.driver_path

        # If operating system is Linux then begin search using scandir at home level
        if self.curr_os == 'linux':
            for root, dirs, files in scandir.walk("/home"):
                print('searching:', root)
                if self.driver in files or self.driver in root:
                    self.driver_path = join(root, self.driver)  # Joins current path and driver name to make path
                    print('found:',self.driver_path)
                    return self.driver_path

    def download_driver(self):
        """
        Downloads most recent phanthom js driver depending on OS

        :return: None
        """
        # If OS is Windows
        url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip" # Recent PhantomJS driver
        zip_target_path = 'C:\\Users\\' + getlogin() + '\\Downloads\\phantomjs-2.1.1-windows.zip' # Download path
        urllib.request.urlretrieve(url, zip_target_path)  # Downloads most recent phantom js driver to downloads directory
        zip_ref = zipfile2.ZipFile(zip_target_path,'r')
        file_target_path = 'C:\\Users\\' + getlogin() + '\\Downloads\\'
        zip_ref.extractall(file_target_path)
        zip_ref.close()

        # If OS is Linux
        if self.curr_os == 'linux':
            system('wget -N https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip -P ~/Downloads')
            system('7z x ~/Downloads/phantomjs-2.1.1-windows.zip')
