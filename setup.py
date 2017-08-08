from sys import platform
from cx_Freeze import setup, Executable

# Dependencies are automatically located but may need fine tuning
build_exe_options = {'packages':['os','numpy','pandas'], 'excludes':['tkinter']}
base = None  # GUI applications require a different base on Windows

if platform == 'win32':
    base = 'Win32GUI'

setup(
    name='Time Logger',
    options={'build_exe':build_exe_options},
    version='1.0.0',
    executables=[Executable('CCU_AutomateLogging.py', base=base)]
)