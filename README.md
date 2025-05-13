# Intro

This aims to create a pip package for iText 9 distribution

# Installation

.NET Core is required for building the package and the `dotnet` tool should be
available in `PATH`.

To install the experimental `itextpy` package in your Python environment,
execute this command at the root of the repository:

```shell
pip install .
```

This will include all the necessary .NET binaries, together with the typing
stubs for IDE auto-completion.

If you just want to build the `itextpy` wheel without installing it, you can
do that with the [build](https://pypi.org/project/build/) package:

```shell
pip install build
python -m build --wheel
```

This will create the `itextpy` wheel in the `dist` directory.

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

More source code examples are available in the [samples](./samples) directory.

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
  .NET Core SDK. To control the versions of the dependencies, modify them in
  `Directory.Packages.props`.
* Only the following packages are included:
  * `itext`
  * `itext.bouncy-castle-adapter`
  * `itext.pdfhtml`
* Current 9.1.0 build contains a bug, which prevents running iText with .NET
  Core under Python.NET. For now, we have a workaround here with a binary 
  patch. Patching is done with the `scripts/patch_itext_binaries.py` script.
  So don't worry, if the `itext.io.dll` binary differs from the one from NuGet.
