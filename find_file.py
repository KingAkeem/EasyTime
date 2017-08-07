import os
from os.path import join


def find_file(file):
    look_for = file
    for root, dirs, files in os.walk("C:\\Users\\Honors Student\\Desktop\\"):
        if look_for in files:
            driver_path = join(root, look_for)
            return driver_path

