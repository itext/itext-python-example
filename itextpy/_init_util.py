import os
import pathlib
import platform
import warnings

import pythonnet


def system() -> str:
    """
    Returns the system/OS name, e.g. 'Linux', 'Windows' or 'Darwin'.

    An empty string is returned if the value cannot be determined.
    """
    try:
        return os.uname().sysname
    except AttributeError:
        return platform.system()


def set_default_runtime(system_name: str) -> None:
    """
    Set up the default CLR runtime

    We don't want to use mono by default on non-Windows platforms, as it is
    done in the Python.NET project. Instead, we want to use .NET Core. So this
    function sets the default CLR runtime to .NET Core on non-Windows
    platforms, unless the runtime was already explicitly specified or if there
    is an env var override present.
    """
    if pythonnet.get_runtime_info() is not None:
        return
    if (system_name != 'Windows') and ('PYTHONNET_RUNTIME' not in os.environ):
        pythonnet.set_runtime('coreclr')
    else:
        pythonnet.set_runtime_from_env()


def add_reference(clr, path: pathlib.Path) -> None:
    """
    Loads the assembly, specified by path. If it couldn't be loaded, load the
    same base assembly from the normal location.

    :param clr: CLR module to add reference to.
    :param path: Path to assembly.
    """
    try:
        # This should work in 99% of cases
        clr.AddReference(str(path))
    except Exception as e:
        # We only case about FileLoadException, doing the import here so that
        # we don't need waste time on the fast path
        from System.IO import FileLoadException
        if not isinstance(e, FileLoadException):
            raise
        # And this the remaining 1%...
        #
        # Here is an example, when this could happen. You have .NET 8
        # installed, and you try to load, for example, System.Text.Encodings.Web
        # 9.0.4. It will fail to load, because .NET 8 bundles this library. But
        # the library version in the bundle is 8.0.0, so there is a conflict.
        # DLL hell is back again...
        #
        # Not quite sure, how to properly solve this in Python.NET, so, for
        # now, in such cases we will fall back on loading the bundled library
        # with a warning and hope for the best...
        assembly = clr.AddReference(str(path.stem))
        warnings.warn(f"{e.Message} "
                      f"This assembly was loaded instead: '{assembly.FullName}'. "
                      f"Updating .NET could resolve this issue.")
