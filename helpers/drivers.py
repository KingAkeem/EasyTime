#! /usr/bin/env python3



import os
import shutil
import wget
import zipfile

from sys import platform

CHROME_VERSION = '2.34'
PHANTOMJS_VERSION = '2.1.1'
_LINUX_HOME = os.path.join('/home', os.getlogin())
_WINDOWS_HOME = os.path.join('C:', 'Users', os.getlogin())


def _find_path(driver):
    """
    Function that searches OS and finds phantom js driver file then returns

    it if it exists

    :return: path of phanthom js driver on OS
    """

    try:
        from scandir import walk

    except ImportError:
        from os import walk

    # If operating system is Windows then begin search using scandir at User
    # level
    if platform == 'win32':
        for root, dirs, files in walk(_WINDOWS_HOME):
            print('Searching: {root}'.format(root=root))
            if driver in files or driver in root:
                path = os.path.join(root, driver)
                print('Found: {path}'.format(path=path))
                return path

    elif platform == 'linux':
        for root, dirs, files in walk(_LINUX_HOME):
            print('Searching: {root}'.format(root=root))
            if driver in files or driver in root:
                path = os.path.join(root, driver)
                print('Found: {path}'.format(path=path))
                return path

    elif platform == 'darwin':
        for root, dirs, files in walk('/Users/'):
            print('Searching: {root}'.format(root=root))
            if driver in files or driver in root:
                path = os.path.join(root, driver)
                print('Found: {path}'.format(path=path))
                return path

    return False

class PhantomJSDriver:

    def __init__(self):

        self._driver_file = '-'.join(('phantomjs', PHANTOMJS_VERSION, 'windows.zip'))

        if platform == 'linux':
            self._cache_dir = os.path.join(_LINUX_HOME, '.phantomjs')
            self._cache_file = os.path.join(self._cache_dir, self._driver_file.replace('.zip', ''), 'bin',
                                            'phantomjs.exe')

        elif platform == 'win32':
            self._exe = 'phantomjs.exe'
            self._cache_dir = os.path.join(_WINDOWS_HOME, '.phantomjs')
            self._cache_file = os.path.join(self._cache_dir, self._driver_file.replace('.zip', ''), 'bin', 'phantomjs.exe')

        elif platform == 'darwin':
            self._exe = 'phantomjsdriver'

        if os.path.isdir(self._cache_dir) and 'bin' in os.listdir(self._cache_dir):
            self._path = self._cache_file
        else:
            self._path = _find_path('phantomjs.exe')


    def get_path(self):

        if os.path.isfile(self._path):
            return self._path
        else:
            self._download_driver()
            return self._path

    def _download_driver(self):
        """
    Downloads most recent phanthom js driver depending on OS

    :return: None
        """

        url = '/'.join(
            (
                'https://bitbucket.org',
                'ariya',
                'phantomjs',
                'downloads',
                self._driver_file
            )
        )  # Recent PhantomJS driver

        # If OS is Windows
        if platform == 'win32':
            pass

        # If OS is Linux
        if platform == 'linux':

            if not os.path.isdir(self._cache_dir):
                os.mkdir(self._cache_dir)

            file_locations = os.listdir(self._cache_dir) + os.listdir()
            if self._driver_file not in file_locations:
                wget.download(url)

            with zipfile.ZipFile(self._driver_file) as zip_ref:
                zip_ref.extractall(self._cache_dir)

            os.chmod(self._cache_file, 0o777)
            os.remove(self._driver_file)

            if 'ghostdriver.log' in os.listdir():
                shutil.move('ghostdriver.log', self._cache_dir)
                os.remove('ghostdriver.log')

            self._path = os.path.join(self._cache_file)


class ChromeDriver:

    def __init__(self):

        if platform == 'linux':
            self._driver_file = 'chromedriver_linux64.zip'
            self._exe = 'chromedriver'
            self._LINUX_HOME = os.path.join('/home', os.getlogin())
            self._cache_dir = os.path.join(_LINUX_HOME, '.chrome')
            self._cache_file = os.path.join(self._cache_dir, self._exe)

        if platform == 'win32':
            self._exe = 'chromedriver.exe'
            self._WINDOWS_HOME = os.path.join('C:', 'Users', os.getlogin())
            self._cache_dir = os.path.join(self._WINDOWS_HOME_HOME, '.chrome')
            self._cache_file = os.path.join(self._cache_dir, self._exe)

        elif platform == 'darwin':
            self._exe = 'chromedriver'

        if os.path.isdir(self._cache_dir) and 'bin' in os.listdir(self._cache_dir):

            self._path = self._cache_file

        else:
           self._path = _find_path(self._exe)

    def get_path(self):

        if os.path.isfile(self._path):
            return self._path
        else:
            self._download_driver()
            return self._path

    def _download_driver(self):
        """
    Downloads most recent phanthom js driver depending on OS

    :return: None
        """

        url = '/'.join(
            (
                'https://chromedriver.storage.googleapis.com',
                '{version}'.format(version=CHROME_VERSION),
                self._driver_file
            )
        )  # Recent PhantomJS driver

        # If OS is Windows
        if platform == 'win32':
            pass

        # If OS is Linux
        if platform == 'linux':

            if not os.path.isdir(self._cache_dir):
                os.mkdir(self._cache_dir)

            file_locations = os.listdir(self._cache_dir) + os.listdir()
            if self._driver_file not in file_locations:
                wget.download(url)

            with zipfile.ZipFile(self._driver_file) as zip_ref:
                zip_ref.extractall(self._cache_dir)

            os.chmod(self._cache_file, 0o777)
            os.remove(self._driver_file)
            self._path = os.path.join(self._cache_file)