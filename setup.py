import esky.bdist_esky
from esky.bdist_esky import Executable as Executable_Esky
from cx_Freeze import setup, Executable
setup(
    name = 'Time Entry',
    version = '1.0.1',
    options = {
        'build_exe': {
            'packages': ['os','sys','ctypes','win32con'],
            'excludes': ['tkinter','tcl','ttk'],
            'include_msvcr': True,
        },
        'bdist_esky': {
            'freezer_module': 'cx_freeze',
        }
    },
    scripts = [
        Executable_Esky(
            "AutoLogging.py",
            #icon = XPTO  # Use an icon if you want.
            ),
    ],
    executables = [Executable('AutoLogging.py',base=None)]
    )