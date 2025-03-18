import os
from pathlib import Path

# Add DLL directory to PATH
dll_path = Path(__file__).parent / "dlls"
os.environ["PATH"] += os.pathsep + str(dll_path)

# Initialize pythonnet runtime
import clr
clr.AddReference("System.IO")

# Load required iText assemblies
clr.AddReference(str(dll_path / "itext.kernel.dll"))
clr.AddReference(str(dll_path / "itext.layout.dll"))

# Expose iText namespaces directly
from iText.Kernel.Pdf import *
from iText.Layout import *
from iText.Layout.Element import *

__all__ = [name for name in dir() if not name.startswith("_")]

