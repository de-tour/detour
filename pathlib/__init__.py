import os.path
import sys

def abs_dir(file_attr):
    if getattr(sys, 'frozen', None):
        file_var = sys.executable
    else:
        file_var = file_attr

    return os.path.dirname(os.path.abspath(file_var))

exec_dir = None
