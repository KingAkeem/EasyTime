from cx_Freeze import setup, Executable
import os

# Dependencies are automatically located but may need fine tuning
build_exe_options = {'packages':['os','numpy','pandas','sys'],'include_msvcr': True}
base = None  # Setting base to none, for terminal use until I figure out win32Gui usage

# Setting paths for execution
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


setup(
    name='Automated Time Entry',
    options={'build_exe':build_exe_options},
    version='1.0.0',
    executables=[Executable('AutoLogging.py', base=base)]
)