import os
import platform

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
