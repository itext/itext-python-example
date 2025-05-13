#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request

from glob import glob
from pathlib import Path
from zipfile import ZipFile

ROOT_DIR = Path(__file__).parent.parent.absolute()
# Directory for the .NET tools
TOOLS_DIR = ROOT_DIR / 'tools'
# Directory for the final stubs
FINAL_STUBS_DIR = ROOT_DIR / 'iText-stubs'
# Temporary directory to put intermediate stubs in
TEMP_STUBS_DIR = ROOT_DIR / 'stubs'
# Path to the output "itextpy" package directory
ITEXT_PY_PACKAGE_DIR = ROOT_DIR / 'itextpy'
# Path to the root directory for "itextpy" binaries
ITEXT_PY_BINARIES_DIR = ITEXT_PY_PACKAGE_DIR / 'binaries'

# Link for downloading PythonNetStubGenerator.Tool sources
# This is a commit-pinned link to our fork
PYTHONNET_STUB_GENERATOR_VERSION = '1.2.3'
PYTHONNET_STUB_GENERATOR_BASENAME_PREFIX = 'pythonnet-stub-generator-'
PYTHONNET_STUB_GENERATOR_BASENAME = PYTHONNET_STUB_GENERATOR_BASENAME_PREFIX + PYTHONNET_STUB_GENERATOR_VERSION
PYTHONNET_STUB_GENERATOR_SRC_LINK = 'https://codeload.github.com/Eswcvlad/pythonnet-stub-generator/zip/refs/tags/' + PYTHONNET_STUB_GENERATOR_VERSION


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


def rmtree_if_exists(f: str) -> None:
    try:
        shutil.rmtree(f)
    except FileNotFoundError:
        pass


def get_python_net_stub_generator_path() -> Path:
    """
    Returns the expected full path to the PythonNetStubGenerator.Tool binary.
    """
    if system() == 'Windows':
        exe_suffix = '.exe'
    else:
        exe_suffix = ''
    return TOOLS_DIR / 'bin' / ('PythonNetStubGenerator.Tool' + exe_suffix)


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
    try:
        with open(stubs_generated_file, 'rt') as generated:
            generator_version, time_str = generated.read().split('|', maxsplit=1)
        stubs_generated_time = int(time_str)
    except:
        return False
    if generator_version != PYTHONNET_STUB_GENERATOR_VERSION:
        return False
    itext_py_published_file = ITEXT_PY_BINARIES_DIR / '.published'
    try:
        with open(itext_py_published_file, 'rt') as published:
            itext_py_published_time = int(published.read())
    except:
        raise Exception('itextpy is not valid')
    return stubs_generated_time > itext_py_published_time


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


def is_tool_version_correct() -> bool:
    """
    Returns whether the installed PythonNetStubGenerator.Tool is of the
    expected version.
    """
    tool_path = get_python_net_stub_generator_path()
    if not tool_path.exists():
        return False

    version_run = subprocess.run(
        args=(tool_path, '--version'),
        stdout=subprocess.PIPE,
        text=True
    )
    strip = version_run.stdout.strip()
    return strip == PYTHONNET_STUB_GENERATOR_VERSION


def prepare_tools(dotnet_path: str) -> None:
    """
    Downloads and builds the PythonNetStubGenerator.Tool, if it doesn't exist.
    """
    eprint('Preparing PythonNetStubGenerator.Tool...')

    if is_tool_version_correct():
        eprint('--- PythonNetStubGenerator.Tool is already built.')
        return

    eprint('--- Cleaning old tools...')
    rmtree_if_exists(str(TOOLS_DIR / 'bin'))
    for f in TOOLS_DIR.glob(PYTHONNET_STUB_GENERATOR_BASENAME_PREFIX + '*'):
        if f.is_dir():
            rmtree_if_exists(str(f))
        else:
            f.unlink()

    eprint('--- Downloading PythonNetStubGenerator.Tool...')
    TOOLS_DIR.mkdir(exist_ok=True)
    with urllib.request.urlopen(PYTHONNET_STUB_GENERATOR_SRC_LINK) as tool_response:
        with open(str(TOOLS_DIR / f'{PYTHONNET_STUB_GENERATOR_BASENAME}.zip'), 'xb') as tool_file:
            tool_file.write(tool_response.read())

    eprint('--- Extracting PythonNetStubGenerator.Tool...')
    with ZipFile(str(TOOLS_DIR / f'{PYTHONNET_STUB_GENERATOR_BASENAME}.zip')) as tool_zip:
        tool_zip.extractall(str(TOOLS_DIR))

    eprint('--- Building PythonNetStubGenerator.Tool...')
    subprocess.run(
        args=(
            dotnet_path, 'publish',
            str(TOOLS_DIR / PYTHONNET_STUB_GENERATOR_BASENAME / 'csharp' / 'PythonNetStubTool'),
            '--nologo',
            '--use-current-runtime',
            '--configuration', 'Release',
            '--output', str(TOOLS_DIR / 'bin'),
        ),
        check=True,
    )

    eprint('--- PythonNetStubGenerator.Tool has been built.')


def clean_temp_stubs() -> None:
    """
    Cleans-up the temporary stubs directory.
    """
    eprint('Cleaning temporary stubs...')
    rmtree_if_exists(str(TEMP_STUBS_DIR))
    eprint('--- Temporary stubs cleaned.')


def generate_stubs() -> None:
    """
    Generates intermediate python typing stubs.
    """
    eprint('Generating intermediate stubs...')
    system_str = system()
    if system_str == 'Linux':
        os_id = 'linux'
    elif system_str == 'Darwin':
        os_id = 'osx'
    else:
        # Will use Windows as fallback as well
        os_id = 'win'
    dlls = list(glob('itext.*.dll', root_dir=ITEXT_PY_BINARIES_DIR))
    if not dlls:
        raise Exception('No iText dlls found.')
    subprocess.run(
        args=(
            get_python_net_stub_generator_path(),
            '--dest-path', TEMP_STUBS_DIR,
            '--search-paths', str(ITEXT_PY_BINARIES_DIR),
            '--search-paths', str(ITEXT_PY_BINARIES_DIR / os_id),
            '--target-dlls', ','.join(dlls),
            '--force-lf',
        ),
        cwd=str(ITEXT_PY_BINARIES_DIR),
        check=True,
    )
    eprint('--- Intermediate stubs have been generated.')


def clean_final_stubs() -> None:
    """
    Cleans-up the final stubs directory.
    """
    eprint('Cleaning final stubs...')
    rmtree_if_exists(str(FINAL_STUBS_DIR))
    eprint('--- Final stubs cleaned.')


def publish_stubs() -> None:
    """
    Publishes stubs to the final directory
    """
    eprint('Publishing stubs...')
    shutil.move(str(TEMP_STUBS_DIR / 'iText'), str(FINAL_STUBS_DIR))
    eprint('--- Adding .generated success mark file')
    with open(FINAL_STUBS_DIR / '.generated', 'x') as generated:
        generated.write(PYTHONNET_STUB_GENERATOR_VERSION)
        generated.write('|')
        generated.write(str(time.time_ns()))
    eprint('--- Stubs have been published.')


def run() -> int:
    if is_itext_py_missing():
        eprint('itextpy package not found. You should run '
               'init_itextpy_package.py before running this script.')
        return 1
    if are_stubs_up_to_date():
        eprint('Stubs are already up-to-date. Doing nothing.')
        return 0
    dotnet_path = require_dotnet()
    if dotnet_path is None:
        return 1
    prepare_tools(dotnet_path)
    clean_temp_stubs()
    generate_stubs()
    clean_final_stubs()
    publish_stubs()
    clean_temp_stubs()
    eprint('Stubs have been generated.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
