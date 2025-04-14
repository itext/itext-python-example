import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.Kernel.Geom import PageSize, Rectangle
from iText.Kernel.Pdf import PdfDocument, PdfWriter
from iText.Kernel.Pdf.Canvas import PdfCanvas
from iText.Svg.Converter import SvgConverter

SCRIPT_DIR = Path(__file__).parent.absolute()
SVG_RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources" / "svg"


def manipulate_pdf(svg_source, pdf_dest):
    with disposing(PdfDocument(PdfWriter(pdf_dest))) as pdf_doc:
        # Create new page
        pdf_page = pdf_doc.AddNewPage(PageSize.A4)

        with disposing(FileStream(svg_source, FileMode.Open, FileAccess.Read)) as svg_path:
            # Convert directly to an XObject
            x_obj = SvgConverter.ConvertToXObject(svg_path, pdf_doc)

        # Add the XObject to the page
        PdfCanvas(pdf_page).AddXObjectFittedIntoRectangle(
            x_obj,
            Rectangle(100, 180, PageSize.A4.GetWidth() / 2, PageSize.A4.GetHeight() / 2)
        )


if __name__ == "__main__":
    manipulate_pdf(
        svg_source=str(SVG_RESOURCES_DIR / "cauldron.svg"),
        pdf_dest="convert_svg_to_x_object.pdf",
    )
