#!/usr/bin/env python3
import os
import platform
import subprocess
import shutil
import sys

from glob import glob
from os.path import getmtime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
# Directory for the .NET tools
TOOLS_DIR = SCRIPT_DIR / 'tools'
# Directory for the final stubs
FINAL_STUBS_DIR = SCRIPT_DIR / 'iText-stubs'
# Temporary directory to put intermediate stubs in
TEMP_STUBS_DIR = SCRIPT_DIR / 'stubs'
# Path to the output "itextpy" package directory
ITEXT_PY_PACKAGE_DIR = SCRIPT_DIR / 'itextpy'
# Path to the root directory for "itextpy" binaries
ITEXT_PY_BINARIES_DIR = ITEXT_PY_PACKAGE_DIR / 'binaries'


def eprint(*args, **kwargs) -> None:
    """
    Print to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)


def system() -> str:
    """
    Returns the current system ID.
    """
    try:
        return os.uname().sysname
    except AttributeError:
        return platform.system()


def get_python_net_stub_generator_path() -> Path:
    """
    Returns the expected full path to the PythonNetStubGenerator.Tool binary.
    """
    if system() == 'Windows':
        exe_suffix = '.exe'
    else:
        exe_suffix = ''
    return TOOLS_DIR / ('GeneratePythonNetStubs' + exe_suffix)


def is_itext_py_missing() -> bool:
    """
    Returns True, if the ".generated" marker in not present in the "itextpy"
    package.
    """
    return not (ITEXT_PY_PACKAGE_DIR / '.generated').exists()


def are_stubs_up_to_date() -> bool:
    """
    Returns false, if the ".generated" marker for stubs is older, than the
    ".published" marker for the itextpy binaries.
    """
    stubs_generated_file = FINAL_STUBS_DIR / '.generated'
    if not stubs_generated_file.exists():
        return False
    itext_py_published_file = ITEXT_PY_BINARIES_DIR / '.published'
    if not itext_py_published_file.exists():
        raise Exception('itextpy is not present')
    return getmtime(stubs_generated_file) >= getmtime(itext_py_published_file)


def require_dotnet() -> str | None:
    """
    Returns path to the dotnet tool.
    """
    eprint('Searching for .NET...')
    dotnet_path = shutil.which('dotnet')
    if dotnet_path is None:
        eprint('--- .NET was not not found. If .NET is installed, make sure it '
               'is available in PATH. If .NET is not installed, go to '
               'https://dotnet.microsoft.com/en-us/download for installation '
               'instructions.')
        return None
    eprint(f'--- .NET found at "{dotnet_path}".')
    return dotnet_path


#
def install_tools(dotnet_path: str) -> None:
    """
    Installs the PythonNetStubGenerator.Tool, if it doesn't exist.
    """
    tool_path = get_python_net_stub_generator_path()
    if tool_path.exists():
        eprint('PythonNetStubGenerator.Tool is already installed.')
        return
    eprint('Installing PythonNetStubGenerator.Tool...')
    subprocess.run(
        args=(
            dotnet_path, 'tool', 'install',
            'PythonNetStubGenerator.Tool',
            '--version', '1.2.1',
            '--tool-path', str(TOOLS_DIR),
        )
    )
    eprint('--- PythonNetStubGenerator.Tool has been installed.')


def clean_temp_stubs() -> None:
    """
    Cleans-up the temporary stubs directory.
    """
    eprint('Cleaning temporary stubs...')
    try:
        shutil.rmtree(str(TEMP_STUBS_DIR))
    except FileNotFoundError:
        pass
    eprint('--- Temporary stubs cleaned.')


def generate_stubs() -> None:
    """
    Generates intermediate python typing stubs.
    """
    eprint('Generating intermediate stubs...')
    system_str = system()
    if system_str == 'Linux':
        os_id = 'win'
    elif system_str == 'Darwin':
        os_id = 'osx'
    else:
        # Will use Windows as fallback as well
        os_id = 'win'
    dlls = list(glob('itext.*.dll', root_dir=ITEXT_PY_BINARIES_DIR))
    if not dlls:
        raise Exception('No iText dlls found.')
    result = subprocess.run(
        args=(
            get_python_net_stub_generator_path(),
            '--dest-path', TEMP_STUBS_DIR,
            '--search-paths', str(ITEXT_PY_BINARIES_DIR),
            '--search-paths', str(ITEXT_PY_BINARIES_DIR / os_id),
            '--target-dlls', ','.join(dlls)
        ),
        cwd=str(ITEXT_PY_BINARIES_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    eprint(result.stdout)
    # For some reason it doesn't change the exit code...
    if 'error' in result.stdout.lower():
        raise Exception('Stub generation failed')
    eprint('--- Intermediate stubs have been generated.')


def clean_final_stubs() -> None:
    """
    Cleans-up the final stubs directory.
    """
    try:
        shutil.rmtree(str(FINAL_STUBS_DIR))
    except FileNotFoundError:
        pass
    eprint('--- Final stubs cleaned.')


def publish_stubs() -> None:
    """
    Publishes stubs to the final directory
    """
    eprint('Publishing stubs...')
    shutil.move(str(TEMP_STUBS_DIR / 'iText'), str(FINAL_STUBS_DIR))
    eprint('--- Adding .generated success mark file')
    open(FINAL_STUBS_DIR / '.generated', 'x').close()
    eprint('--- Stubs have been published.')


def run() -> int:
    if is_itext_py_missing():
        eprint('itextpy package not found. You should run '
               'init_itextpy_package.py before running this script.')
        return 1
    if are_stubs_up_to_date():
        eprint('Stubs are already up-to-date. Doing nothing.')
        return 1
    dotnet_path = require_dotnet()
    if dotnet_path is None:
        return 1
    install_tools(dotnet_path)
    clean_temp_stubs()
    generate_stubs()
    clean_final_stubs()
    publish_stubs()
    clean_temp_stubs()
    eprint('Stubs have been generated.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
