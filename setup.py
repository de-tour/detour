# Build script for freezing modules into an executable file

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = dict(
    packages = [],
    excludes = [],
    includes = ['idna.idnadata'],
    include_files = ['config/', 'public/'],
    optimize = 2,
)

# import sys
# base = 'Win32GUI' if sys.platform=='win32' else None
base = None

executables = [
    Executable('start.py', base=base)
]

setup(
    name='Detour',
    version = '0.1.0',
    description = 'Detour',
    options = dict(build_exe = build_options),
    executables = executables
)
