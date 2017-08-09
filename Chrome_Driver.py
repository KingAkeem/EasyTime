import scandir
import os
from os.path import join
from sys import platform

class Chrome_Driver:

    def __init__(self):
        self.driver = 'chromedriver.exe'

    def find_path(self):
        if platform == 'win32':

            for root, dirs, files in scandir.walk("C:\\"):
                print('searching:', root)
                if self.driver in files:
                    driver_path = join(root, self.driver)
                    return driver_path

        if platform == 'linux':
            for root, dirs, files in os.walk("/home/atking1/Downloads/"):
                print('searching:', root)
                if self.driver in files:
                    driver_path = join(root, self.driver)
                    print('found:',driver_path)
                    return driver_path







