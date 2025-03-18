import os
import sys
from pathlib import Path

# Add DLL directory to PATH
dll_path = Path(__file__).parent / "dlls"
os.environ["PATH"] += os.pathsep + str(dll_path)

# Initialize pythonnet runtime
import clr
clr.AddReference("System.IO")
from System.IO import Path as SysPath

# Load required iText assemblies
clr.AddReference(str(dll_path / "itext.kernel.dll"))
clr.AddReference(str(dll_path / "itext.layout.dll"))

# Expose iText namespaces directly
from iText.Kernel.Pdf import PdfWriter, PdfReader, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Paragraph

__all__ = ['PdfWriter', 'PdfReader', 'Document', 'Paragraph', 'PdfDocument']
