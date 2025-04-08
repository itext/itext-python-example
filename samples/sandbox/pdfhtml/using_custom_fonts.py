import itextpy
itextpy.load()

import contextlib
from pathlib import Path

from System.IO import FileMode, FileStream
from iText.Html2pdf import ConverterProperties, HtmlConverter
from iText.Kernel.Pdf import PdfDocument, PdfWriter
from iText.StyledXmlParser.Resolver.Font import BasicFontProvider

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC_DIR = RESOURCES_DIR / "pdfhtml" / "FontExample"
FONT_DIR = str(SRC_DIR / "font")
FONT_1_PATH = str(RESOURCES_DIR / "font" / "New Walt Disney.ttf")
FONT_2_PATH = str(RESOURCES_DIR / "font" / "Greifswalder Tengwar.ttf")


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def manipulate_pdf(html_source, pdf_dest):
    with itext_closing(PdfDocument(PdfWriter(pdf_dest))) as pdf_doc:
        # Default provider will register standard fonts and free fonts shipped with iText, but not system fonts
        provider = BasicFontProvider()

        # 1. Register all fonts in a directory
        provider.AddDirectory(FONT_DIR)

        # 2. Register a single font by specifying path
        provider.AddFont(FONT_1_PATH)

        # 3. Use the raw bytes of the font file
        with open(FONT_2_PATH, 'rb') as font:
            font_bytes = font.read()
        provider.AddFont(font_bytes)

        # Make sure the provider is used
        converter_properties = (ConverterProperties()
                                # Base URI is required to resolve the path to source files
                                .SetBaseUri(str(SRC_DIR))
                                .SetFontProvider(provider))

        HtmlConverter.ConvertToPdf(
            FileStream(html_source, FileMode.Open),
            pdf_doc,
            converter_properties,
        )


if __name__ == "__main__":
    manipulate_pdf(
        html_source=str(SRC_DIR / "FontExample.html"),
        pdf_dest="using_custom_fonts.pdf",
    )
