#!/usr/bin/env python3
import subprocess
import shutil
import sys

from collections import defaultdict
from os.path import getmtime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
# Name of the .NET stub project
STUB_PROJ_NAME = 'csharp-dependency-stub'
# Path to the .NET stub project directory
STUB_PROJ_DIR = SCRIPT_DIR / 'csharp' / STUB_PROJ_NAME
# Path to the Python compat .NET library project directory
COMPAT_PROJ_DIR = SCRIPT_DIR / 'csharp' / 'itext.python.compat'
# Path to the output "itextpy" package directory
PACKAGE_DIR = SCRIPT_DIR / 'itextpy'
# Path to the root directory for "itextpy" binaries
ANY_PUBLISH_DIR = PACKAGE_DIR / 'binaries'

# Configuration to build the stub .NET project in. Not sure, if it even
# matters in this case, as dependencies will be build in Release mode anyway,
# but just in case...
CONFIGURATION = 'Release'
# Target framework to use for the stub project. For now, using "netstandard2.0"
# as the lowest common denominator.
FRAMEWORK = 'netstandard2.0'
# "Default" OS to reference, when merging binaries between OSes. Makes sense
# for .NET to have Windows as the default. Though it shouldn't matter for
# deduplication anyway...
REFERENCE_OS = 'win'
# Target runtimes to publish for. This, pretty much, defines platforms, for
# which the itextpy package is guaranteed to work
RUNTIMES = {
    'win': ('x64', 'x86', 'arm64',),
    'linux': ('x64', 'musl-x64', 'musl-arm64', 'arm', 'arm64', 'bionic-arm64', 'loongarch64',),
    'osx': ('arm64', 'x64',),
}


def eprint(*args, **kwargs) -> None:
    """
    Print to stderr.
    """
    print(*args, file=sys.stderr, **kwargs)


def escape_quote(s: str) -> str:
    """
    Escapes single quotes for literal single quote string content.
    """
    return s.replace("'", "\\'")


def to_runtime(os: str, arch: str) -> str:
    """
    Constructs a runtime identifier from OS and architecture.
    """
    return '-'.join((os, arch))


def get_publish_dir(runtime: str) -> Path:
    """
    Returns path to the publish directory of the .NET stub project for the
    specified runtime.
    """
    return STUB_PROJ_DIR / 'bin' / CONFIGURATION / FRAMEWORK / runtime / 'publish'


def are_relevant_binaries_published() -> bool:
    """
    Returns True, if there is a ".published" marker in the binaries directory,
    and that the marker was created after all the stub project changes.
    """
    published_file = (ANY_PUBLISH_DIR / '.published')
    if not published_file.exists():
        return False
    for proj_dir in (STUB_PROJ_DIR, COMPAT_PROJ_DIR):
        for ext in ('cs', 'csproj'):
            for f in proj_dir.glob(f'**/*.{ext}'):
                if getmtime(f) > getmtime(published_file):
                    return False
    return True


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


def clean_stub() -> None:
    """
    Cleans-up the csharp-dependency-stub .NET project.
    """
    eprint('Cleaning stub project...')
    for subdir in ('obj', 'bin'):
        eprint(f'--- Cleaning {subdir}...')
        try:
            shutil.rmtree(str(STUB_PROJ_DIR / subdir))
        except FileNotFoundError:
            pass
    eprint('--- Stub project cleaned.')


def publish_stub(dotnet_path: str) -> None:
    """
    Runs "dotnet publish" on the csharp-dependency-stub project for all
    pre-defined runtimes.
    """
    eprint('Publishing stub project...')
    for os, architectures in RUNTIMES.items():
        for arch in architectures:
            runtime = '-'.join((os, arch))
            eprint(f'--- Publishing for {runtime}...')
            subprocess.run(
                args=(
                    dotnet_path, 'publish',
                    str(STUB_PROJ_DIR),
                    '--nologo',
                    '--no-self-contained',
                    '--configuration', CONFIGURATION,
                    '--framework', FRAMEWORK,
                    '--runtime', runtime,
                ),
                check=True,
            )
    eprint('--- Stub project has been published for all runtimes')


def index_stub_binaries() -> defaultdict[str, set[str]]:
    """
    Goes through the published .NET project and creates an index of library
    binaries. Binaries, which are the same within a wider parent runtime
    classifier, are "deduplicated" and will no longer be present in the child
    runtime. The hierarchy of runtime ids is: any -> {os} -> {os}-{arch}.
    For example, if Newtonsoft.Json.dll is the same in osx-arm64 and osx-x64,
    it will no longer be present under those keys, but under osx. And if the
    same library is the same in linux, osx and win, then it will be moved to
    any.
    """
    eprint('Indexing stub binaries...')

    eprint('--- Listing libraries per runtime...')
    binaries = defaultdict(set)
    for os, architectures in RUNTIMES.items():
        for arch in architectures:
            runtime = to_runtime(os, arch)
            for dll in get_publish_dir(runtime).glob('[!_]*.dll'):
                binaries[runtime].add(str(dll.name))

    for os in RUNTIMES:
        eprint(f'--- Deduplicating libraries within {os}...')
        shared_binaries = set.intersection(*(binaries[to_runtime(os, arch)] for arch in RUNTIMES[os]))
        for dll in sorted(shared_binaries):
            if is_same_within_os(os, dll):
                deduplicate_within_os(binaries, os, dll)
                eprint(f'------ Deduplicated: {dll}.')
            else:
                eprint(f'------ Left as-is:   {dll}.')

    eprint(f'--- Deduplicating libraries between OSes...')
    shared_binaries = set.intersection(*(binaries[os] for os in RUNTIMES))
    for dll in sorted(shared_binaries):
        if is_same_between_oses(dll):
            deduplicate_between_oses(binaries, dll)
            eprint(f'------ Deduplicated: {dll}.')
        else:
            eprint(f'------ Left as-is:   {dll}.')

    eprint('--- Indexing finished.')
    return binaries


def is_same_within_os(os: str, dll: str) -> bool:
    """
    Returns whether the specified DLL is the same for each architecture
    within the specified OS.
    """
    architectures = RUNTIMES[os]
    if len(architectures) == 1:
        return True
    comp_bytes = (get_publish_dir(runtime=to_runtime(os, architectures[0])) / dll).read_bytes()
    for arch in architectures[1:]:
        dll_bytes = (get_publish_dir(runtime=to_runtime(os, arch)) / dll).read_bytes()
        if dll_bytes != comp_bytes:
            return False
    return True


def deduplicate_within_os(binaries: defaultdict[str, set[str]], os: str, dll: str) -> None:
    """
    Manipulates the index. Removes the DLL from the leaf {os}-{arch} keys and
    puts it under the {os} key.
    """
    for arch in RUNTIMES[os]:
        binaries[to_runtime(os, arch)].remove(dll)
    binaries[os].add(dll)


def is_same_between_oses(dll: str) -> bool:
    """
    Returns whether the specified DLL is the same for each OS. Assumes, that
    deduplication already happened per OS.
    """
    oses = tuple(RUNTIMES.keys())
    if len(oses) == 1:
        return True
    comp_bytes = (get_publish_dir(runtime=to_runtime(oses[0], RUNTIMES[oses[0]][0])) / dll).read_bytes()
    for os in oses[1:]:
        dll_bytes = (get_publish_dir(runtime=to_runtime(os, RUNTIMES[os][0])) / dll).read_bytes()
        if dll_bytes != comp_bytes:
            return False
    return True


def deduplicate_between_oses(binaries: defaultdict[str, set[str]], dll: str) -> None:
    """
    Manipulates the index. Removes the DLL from the {os} keys and puts it under
    the 'any' key. Assumes, that deduplication already happened per OS.
    """
    for os in RUNTIMES:
        binaries[os].remove(dll)
    binaries['any'].add(dll)


def clean_package() -> None:
    """
    Cleans the "itextpy" package directory.
    """
    eprint('Cleaning package...')
    (PACKAGE_DIR / '.generated').unlink(missing_ok=True)
    (PACKAGE_DIR / '__init__.py').unlink(missing_ok=True)
    if not are_relevant_binaries_published():
        try:
            shutil.rmtree(str(ANY_PUBLISH_DIR))
        except FileNotFoundError:
            pass
    eprint('--- Package cleaned.')


def publish_binaries(binaries: defaultdict[str, set[str]]) -> None:
    """
    Publishes the .NET binaries for the itextpy package. I.E. it populates
    the "itextpy/binaries" directory.
    """
    eprint('Publishing binaries...')

    eprint('--- Publishing any binaries...')
    ANY_PUBLISH_DIR.mkdir(parents=True)
    reference_runtime = to_runtime(REFERENCE_OS, RUNTIMES[REFERENCE_OS][0])
    for dll in sorted(binaries['any']):
        shutil.move(str(get_publish_dir(reference_runtime) / dll), str(ANY_PUBLISH_DIR / dll))
        eprint(f'--- Moved {dll}.')
    for os, architectures in RUNTIMES.items():
        reference_os_runtime = to_runtime(os, RUNTIMES[os][0])
        os_publish_dir = ANY_PUBLISH_DIR / os
        if binaries[os]:
            eprint(f'--- Publishing {os} binaries...')
            os_publish_dir.mkdir()
            for dll in sorted(binaries[os]):
                shutil.move(str(get_publish_dir(reference_os_runtime) / dll), str(os_publish_dir / dll))
                eprint(f'--- Moved {dll}.')
        for arch in architectures:
            runtime = to_runtime(os, arch)
            runtime_publish_dir = os_publish_dir / arch
            if binaries[runtime]:
                eprint(f'--- Publishing {runtime} binaries...')
                runtime_publish_dir.mkdir(parents=True)
                for dll in sorted(binaries[runtime]):
                    shutil.move(str(get_publish_dir(runtime) / dll), str(runtime_publish_dir / dll))
                    eprint(f'--- Moved {dll}.')

    eprint('--- Adding .published success mark file')
    open(ANY_PUBLISH_DIR / '.published', 'x').close()

    eprint('--- All binaries have been published')


def index_package_binaries() -> defaultdict[str, set[str]]:
    """
    Builds the package index based on the "itextpy/binaries" contents.
    """
    eprint('Indexing package binaries...')

    binaries = defaultdict(set)
    for dll in ANY_PUBLISH_DIR.glob('[!_]*.dll'):
        binaries['any'].add(str(dll.name))
    for os, architectures in RUNTIMES.items():
        for dll in (ANY_PUBLISH_DIR / os).glob('[!_]*.dll'):
            binaries[os].add(str(dll.name))
        for arch in architectures:
            runtime = to_runtime(os, arch)
            for dll in (ANY_PUBLISH_DIR / os / arch).glob('[!_]*.dll'):
                binaries[runtime].add(str(dll.name))

    eprint('--- Indexing finished.')
    return binaries


def generate_init_file(binaries: defaultdict[str, set[str]]) -> bool:
    """
    Generates the __init__.py file for the "itextpy" package.
    """
    eprint('Generating __init__.py file...')

    # At the moment we don't have architecture-specific binaries, so not
    # implementing it for now. Will just check, that it is still the case in
    # the future
    supported_binaries = {'any', 'win', 'linux', 'osx'}
    current_binaries = set()
    if binaries['any']:
        current_binaries.add('any')
    for os, architectures in RUNTIMES.items():
        if binaries[os]:
            current_binaries.add(os)
        for arch in architectures:
            runtime = to_runtime(os, arch)
            if binaries[runtime]:
                current_binaries.add(runtime)
    unsupported_binaries = current_binaries - supported_binaries
    if unsupported_binaries:
        eprint(f'--- Found exclusive binaries for {unsupported_binaries}. Not implemented. Aborting.')
        return False

    lines = [
        "# !!! THIS FILE IS AUTO-GENERATED, DO NOT EDIT !!!",
        "import pathlib as _pathlib",
        "from . import _util",
        "",
        "_BINARIES = _pathlib.Path(__file__).parent / 'binaries'",
        "",
        "",
        "def load() -> None:",
        '    """',
        "    Loads the .NET libraries required for itextpy to function.",
        "",
        "    This function imports clr, so if you wish to customise your .NET runtime",
        "    configuration, it should be done before calling this function.",
        '    """',
        "    system_name = _util.system()",
        "    _util.set_default_runtime(system_name)",
        "    import clr",
    ]
    for dll in sorted(binaries['any']):
        lines.append(f"    clr.AddReference(str(_BINARIES / '{escape_quote(dll)}'))")
    for os, system in (('win', 'Windows'), ('linux', 'Linux'), ('osx', 'Darwin')):
        if binaries[os]:
            lines.append(f"    if system_name == '{escape_quote(system)}':")
            for dll in sorted(binaries[os]):
                lines.append(f"        clr.AddReference(str(_BINARIES / '{escape_quote(os)}' / '{escape_quote(dll)}'))")
    lines.extend((
        "",
        "",
        "__all__ = ('load',)",
    ))
    with open(PACKAGE_DIR / '__init__.py', 'xt', encoding='utf-8', newline='\n') as init_py:
        for line in lines:
            init_py.write(line)
            init_py.write('\n')

    eprint('--- Adding .generated success mark file')
    open(PACKAGE_DIR / '.generated', 'x').close()

    eprint('--- __init__.py generated.')
    return True


def run() -> int:
    dotnet_path = require_dotnet()
    if dotnet_path is None:
        return 1
    clean_package()
    if not are_relevant_binaries_published():
        clean_stub()
        publish_stub(dotnet_path)
        binaries = index_stub_binaries()
        publish_binaries(binaries)
        clean_stub()
    if not generate_init_file(index_package_binaries()):
        eprint('Package generation failed.')
        return 1
    eprint('Package has been generated.')
    return 0


if __name__ == '__main__':
    sys.exit(run())
