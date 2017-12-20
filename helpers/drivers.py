#! /usr/bin/env python3

try:
    from scandir import walk

except ImportError:
    from os import walk

import requests
import sys
import wget
import urllib.request
import zipfile
import os
from sys import platform

CHROME_VERSION = '2.34'
PHANTOMJS_VERSION = '2.1.1'

def _give_exe_permissions(path):
    """
    Gives execution permissions to this path, while keeping other permissions

    :param path: Path to give permission
    """

    os.chmod(path, 0o777)

class PhantomJSDriver:

    def __init__(self):

        self._driver_file = '-'.join(('phantomjs', PHANTOMJS_VERSION, 'windows.zip'))

        if platform == 'win32' or platform == 'linux':
            self.__exe = 'phantomjs.exe'
            self._LINUX_HOME = os.path.join('/home', os.getlogin())
            self._cache_dir = os.path.join(self._LINUX_HOME, '.phantomjs')
            self._cache_file = os.path.join(self._cache_dir, self._driver_file.replace('.zip', ''), 'bin', 'phantomjs.exe')

        elif platform == 'darwin':
            self.__exe = 'phantomjsdiver'

        if os.path.isdir(self._cache_dir) and 'bin' in os.listdir(self._cache_dir):

            self._path = self._cache_file

        else:
            self._find_path()

    def get_path(self):

        return self._path

    def _find_path(self):
        """
        Function that searches OS and finds phantom js driver file then returns

        it if it exists

        :return: path of phanthom js driver on OS
        """

        found = False

        # If operating system is Windows then begin search using scandir at User
        # level
        if platform == 'win32':
            for root, dirs, files in walk('C:\\Users\\'):
                print('Searching: {root}'.format(root=root))
                if self.__exe in files or self.__exe in root:
                    self._path = os.path.join(root, self.__exe)
                    print('Found: {path}'.format(path=self._path))

        elif platform == 'linux':
            for root, dirs, files in walk(self._LINUX_HOME):
                print('Searching: {root}'.format(root=root))
                if self.__exe in files or self.__exe in root:
                    self._path = os.path.join(root, self.__exe)
                    print('Found: {path}'.format(path=self._path))

        elif platform == 'darwin':
            for root, dirs, files in walk('/Users/'):
                print('Searching: {root}'.format(root=root))
                if self.__exe in files or self.__exe in root:
                    self._path = os.path.join(root, self.__exe)
                    print('Found: {path}'.format(path=self._path))

        if not found:
            self._download_driver()

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
            file_name = 'phantomjs-version-windows.zip'.format(version=PHANTOMJS_VERSION)
            zip_target_path = 'C:\\Users\\{login}\\Downloads\\{f}'.format(
                login=os.getlogin(), f=file_name)  # Download path
            link = url
            with open(file_name, 'wb') as f:
                print('Downloading {f}'.format(f=file_name))
                response = requests.get(link, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None:  # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=1024):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        sys.stdout.write(
                            '\r[%s%s]' % ('=' * done, ' ' * (50 - done))
                        )
                    sys.stdout.flush()
                    urllib.request.urlretrieve(url, zip_target_path)
                    zip_ref = zipfile.ZipFile(zip_target_path, 'r')
                    file_target_path = 'C:\\Users\\{login}\\Downloads\\'.format(
                        login=os.getlogin())
                    zip_ref.extractall(file_target_path)


        # If OS is Linux
        if platform == 'linux':

            if not os.path.isdir(self._cache_dir):
                os.mkdir(self._cache_dir)

            file_locations = os.listdir(self._cache_dir) + os.listdir()
            if self._driver_file not in file_locations:
                wget.download(url)

            with zipfile.ZipFile(self._driver_file) as zip_ref:
                zip_ref.extractall(self._cache_dir)

            _give_exe_permissions(self._cache_file)
            os.remove(self._driver_file)
            self._path = os.path.join(self._cache_file)
