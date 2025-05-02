# Intro

This aims to create a pip package for iText 9 distribution

# Build 

.NET Core is required for build the package and `dotnet` tool should be
available in `PATH`.

To build the package, just run:

```
python -m build --wheel
```

which should create a file:

```
./dist/itextpy-9.1.0-py3-none-any.whl
```

that then you can install by using

```
pip install ./dist/itextpy-9.1.0-py3-none-any.whl --force-reinstall
```

This package includes both the binaries and the typing stubs for IDE
auto-completion.

# Usage

```python
# Uncomment this block, if you wish to force the .NET Core runtime
# import pythonnet
# pythonnet.load('coreclr')

# Load the .NET binaries
# Any .NET runtime configuration should be done before the load call
import itextpy
itextpy.load()

# Use as any regular Python package
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Paragraph

writer = PdfWriter("test.pdf")
pdf_doc = PdfDocument(writer)
document = Document(pdf_doc)
document.Add(Paragraph("Hello, World!"))
document.Close()
```

# Limitations

* .NET Core SDK is required for building.
* Typing information is auto-generated from binaries via the
  [pythonnet-stub-generator](https://github.com/MHDante/pythonnet-stub-generator).
  Ideally we would want to have docs transferred as well and be able to patch
  the tool output manually, if needed.
* As of Python.NET 3.0.5 you cannot override protected methods within Python.
  To overcome this limitation, we include a small `itext.python.compat`
  library. It includes subclasses, which wraps protected methods into
  overridable public ones.
* Dependencies are taken from NuGet and dependency resolution is handled by the
  .NET Core SDK. To control the library version, modify package versions within
  `Directory.Packages.props`.
* Only the following packages are included:
  * `itext`
  * `itext.bouncy-castle-adapter`
  * `itext.pdfhtml`
* Current 9.1.0 build contains a bug, which prevent running iText with .NET
  Core under Python.NET. For now we have a workaround here with a binary patch.
  Patch is done with the `scripts/patch_itext_binaries.py` script. So the 
  `itext.io.dll` binary is not the same, as the one from NuGet.
