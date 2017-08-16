import os

from sys import platform
from cx_Freeze import setup, Executable

# Dependencies are automatically located but may need fine tuning
build_exe_options = {'packages':['os','numpy','pandas','sys','idna'],'include_msvcr': True}
bdist_msi_options =  {
    'upgrade_code': '{66620F3A-DC3A-11E2-B341-002219E9B01A}',
    'add_to_path': True
    }

base = None  # GUI applications require a different base on Windows

os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python36-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files\Python36-32\tcl\tk8.6'

if platform == 'win32':
    base = 'Win32GUI'

setup(
    name='Easy Time',
    options={'bdist_msi': bdist_msi_options, 'build_exe':build_exe_options},
    version='1.0.0',
    executables=[Executable('AutoLogging.py', base=base)]
)