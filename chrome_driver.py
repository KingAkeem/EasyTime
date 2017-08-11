import scandir
import getpass
from urllib import request
from os import getlogin, system
from os.path import join
from sys import platform
from shutil import copyfileobj


class Chrome_Driver:
    """
    Class that controls chromedriver

    Note:
        Do not include the 'self' parameter in the 'Args' section
    Attributes:
        curr_os (str): Current operating system
        driver (str): Format of driver depending on OS
    """

    def __init__(self):
        self.curr_os = platform
        if self.curr_os == 'win32':
            self.driver = 'chromedriver.exe'

        elif self.curr_os == 'linux':
            self.driver = 'chromedriver'

    def get_path(self):
        """
        Method that searches OS and finds chromedriver file then returns it if it exists

        :return: path of chromedriver on OS
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
        Downloads most recent chromedriver depending on OS

        :return: None
        """
        url = 'https://chromedriver.storage.googleapis.com/index.html?path=2.31/' # Url of recent chromedriver

        # If OS is Windows
        if self.curr_os == 'win32':
            file_name = 'C:\\Users\\' + getlogin()
            with request.urlopen(url) as response, open(file_name, 'wb') as out_file:
                copyfileobj(response, out_file)
        # If OS is Linux
        if self.curr_os == 'linux':
            system('wget -N http://chromedriver.storage.googleapis.com/2.31/chromedriver_linux64.zip -P ~/Downloads')
            system('7z x ~/Downloads/chromedriver_linux64.zip')
