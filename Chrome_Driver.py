import scandir
from glob import glob
from os.path import join
from sys import platform

class Chrome_Driver:

    def __init__(self):
        if platform == 'win32':
            self.driver = 'chromedriver.exe'

        elif platform == 'linux':
            self.driver = 'chromedriver'

    def find_path(self):
        if platform == 'win32':

            for root, dirs, files in scandir.walk("C:\\"):
                print('searching:', root)
                if self.driver in files:
                    driver_path = join(root, self.driver)
                    print('found:',driver_path)
                    return driver_path

        if platform == 'linux':
            for root, dirs, files in scandir.walk("/home"):
                print('searching:', root)
                if self.driver in files or self.driver in root:
                    driver_path = join(root, self.driver)
                    print('found:',driver_path)
                    return driver_path

