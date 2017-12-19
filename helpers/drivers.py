#! /usr/bin/env python3

try:
    from scandir import walk

except ImportError:
    from os import walk

import requests
import shutil
import stat
import sys
import wget
import urllib.request
import zipfile
import os
from sys import platform

PHANTOMJS_VERSION = '2.1.1'
CHROME_VERSION = '2.34'
LINUX_HOME = os.path.join('/home', os.getlogin())


class PhantomJSDriver:

    def _get_path(self):
        """
        Function that searches OS and finds phantom js driver file then returns
        it if it exists

        :return: path of phanthom js driver on OS
        """

        # If operating system is Windows then begin search using scandir at User
        # level
        if platform == 'win32':
            for root, dirs, files in walk('C:\\Users\\'):
                print('Searching: {root}'.format(root=root))
                if exe in files or exe in root:
                    path = os.path.join(root, exe)
                    print('Foud: {path}'.format(path=path))
                    return path
            else:
                _download_driver()

        elif platform == 'linux':
            for root, dirs, files in walk(LINUX_HOME):

                print('Searching: {root}'.format(root=root))
                if exe in files or exe in root:
                    path = os.path.join(root, exe)
                    print('Found: {path}'.format(path=path))
                    return path
            else:
                _download_driver()

        elif platform == 'darwin':
            for root, dirs, files in walk('/Users/'):
                print('Searching: {root}'.format(root=root))
                if exe in files or exe in root:
                    path = os.path.join(root, exe)
                    print('Found: {path}'.format(path=path))
                    return path
            else:
                self_download_driver()

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
                'phantomjs-{version}-windows.zip'.format(version=VERSION)
            )
        )  # Recent PhantomJS driver

        # If OS is Windows
        if platform == 'win32':
            file_name = 'phantomjs-version-windows.zip'.format(version=VERSION)
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

            file_name = wget.download(url)
            cache_dir = os.path.join(LINUX_HOME, '.phantomjs')
            os.mkdir(cache_dir)

            with zipfile.ZipFile(file_name) as zip_ref:
                zip_ref.extractall(cache_dir)

            exec_perm = stat.S_IXUSR
            file_name_no_ext = file_name.replace('.zip', '')
            os.chmod(os.path.join(cache_dir, file_name_no_ext), exec_perm)

            os.remove(file_name)
