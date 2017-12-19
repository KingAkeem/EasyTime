#! /usr/bin/env python3

try:
    from scandir import walk
except ImportError:
    from os import walk

import getpass
import requests
import sys
import urllib.request
import zipfile
from os import getlogin, system
from os.path import join
from sys import exit, platform

VERSION = '2.1.1'


def confirm():

            answer = input(
                "Would you like to download version {version} of PhantomJS"
                "driver? ".format(version=VERSION))
            valid_answers = ["Y", "y", "yes", "Yes", "YES"]
            if answer in valid_answers:
                return 'YES'
            else:
                print("You cannot continue program without driver.")
                exit()


def get_path(exe):
    """
    Function that searches OS and finds phanthom js driver file then returns
    it if it exists

    :return: path of phanthom js driver on OS
    """

    # If operating system is Windows then begin search using scandir at User
    # level
    if platform == 'win32':
        for root, dirs, files in walk('C:\\Users\\'):
            print('Searching: {root}'.format(root=root))
            if exe in files or exe in root:
                path = join(root, exe)
                print('Found: {path}'.format(path=path))
                return path
        else:
            if confirm() == 'YES':
                download_driver()

    if platform == 'linux':
        for root, dirs, files in walk('/home/{user}/'.format(
            user=getpass.getuser()
        )):
            print('Searching: {root}'.format(root=root))
            if exe in files or exe in root:
                path = join(root, exe)
                print('Found: {path}'.format(path=path))
                return path
        else:
            if confirm() == 'YES':
                download_driver()

    if platform == 'darwin':
        for root, dirs, files in walk('/Users/'):
            print('Searching: {root}'.format(root=root))
            if exe in files or exe in root:
                path = join(root, exe)
                print('Found: {path}'.format(path=path))
                return path
        else:
            if confirm() == 'YES':
                download_driver()


def download_driver():
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
            login=getlogin(), f=file_name)  # Download path
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
                    login=getlogin())
                zip_ref.extractall(file_target_path)
                zip_ref.close()
            print('You now have Phantom JS version {version} driver in '
                  '{f_t}'.format(version=VERSION, f_t=file_target_path))

    # If OS is Linux
    if platform == 'linux':
        system('wget -N {url} -P .'.format(url=url))
        system('unzip phantomjs-2.1.1-windows.zip')
        system('chmod u+x phantomjs-2.1.1-windows/bin/phantomjs.exe')
        print('You now have Phantom JS version 2.1.1 driver in your current'
              ' directory.')
