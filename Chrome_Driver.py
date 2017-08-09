import scandir
from urllib import request
from os import getlogin
from os.path import join
from sys import platform
from shutil import copyfileobj


class Chrome_Driver:

    def __init__(self):
        self.curr_os = platform
        if self.curr_os == 'win32':
            self.driver = 'chromedriver.exe'

        elif self.curr_os == 'linux':
            self.driver = 'chromedriver'

    def find_path(self):
        if self.curr_os == 'win32':

            for root, dirs, files in scandir.walk("C:\\Users\\Honors Student\\"):
                # print('searching:', root)
                if self.driver in files:
                    driver_path = join(root, self.driver)
                    print('found:',driver_path)
                    return driver_path

        if self.curr_os == 'linux':
            for root, dirs, files in scandir.walk("/home"):
                print('searching:', root)
                if self.driver in files or self.driver in root:
                    driver_path = join(root, self.driver)
                    print('found:',driver_path)
                    return driver_path
"""
    def download_driver(self):
        url = 'https://chromedriver.storage.googleapis.com/index.html?path=2.31/'
        if self.curr_os == 'win32':
            file_name = 'C:\\Users\\' + getlogin()
            with request.urlopen(url) as response, open(file_name, 'wb') as out_file:
                copyfileobj(response, out_file)
"""