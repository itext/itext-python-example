import itextpy
itextpy.load()

import contextlib
from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfDocument, PdfWriter
from iText.Svg.Converter import SvgConverter
from iText.Svg.Processors.Impl import SvgConverterProperties

SCRIPT_DIR = Path(__file__).parent.absolute()
SVG_RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources" / "svg"


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def manipulate_pdf(svg_source, pdf_dest):
    with itext_closing(PdfDocument(PdfWriter(pdf_dest))) as pdf_doc:
        # Create new page
        pdf_page = pdf_doc.AddNewPage(PageSize.A4)

        # SVG image
        svg_path = FileStream(svg_source, FileMode.Open, FileAccess.Read)

        # Create SVG converter properties object
        props = SvgConverterProperties()

        # Draw image on the page
        SvgConverter.DrawOnPage(svg_path, pdf_page, props)


if __name__ == "__main__":
    manipulate_pdf(
        svg_source=str(SVG_RESOURCES_DIR / "cauldron.svg"),
        pdf_dest="convert_svg_to_pdf_page.pdf",
    )
