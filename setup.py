from sys import platform
from cx_Freeze import setup, Executable

# Dependencies are automatically located but may need fine tuning
build_exe_options = {'packages':['os','numpy','pandas','sys'],'include_msvcr': True}
base = None  # Setting base to none, for terminal use until I figure out win32Gui usage

setup(
    name='Time Logger',
    options={'build_exe':build_exe_options},
    version='1.0.0',
    executables=[Executable('AutoLogging.py', base=base)]
)