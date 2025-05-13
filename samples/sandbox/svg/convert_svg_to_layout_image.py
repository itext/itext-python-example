import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfDocument, PdfWriter
from iText.Layout import Document
from iText.Layout.Element import Paragraph
from iText.Svg.Converter import SvgConverter

SCRIPT_DIR = Path(__file__).parent.absolute()
SVG_RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources" / "svg"


def manipulate_pdf(svg_source, pdf_dest):
    with (disposing(PdfDocument(PdfWriter(pdf_dest))) as pdf_doc,
          disposing(Document(pdf_doc)) as doc):
        # Create new page
        pdf_doc.AddNewPage(PageSize.A4)

        doc.Add(Paragraph("This is some text added before the SVG image."))

        with disposing(FileStream(svg_source, FileMode.Open, FileAccess.Read)) as svg_path:
            # Convert to image
            image = SvgConverter.ConvertToImage(svg_path, pdf_doc)

        # Set scale
        image.ScaleToFit(PageSize.A4.GetWidth() / 2, PageSize.A4.GetHeight() / 2)

        # Add to the document
        doc.Add(image)

        doc.Add(Paragraph("This is some text added after the SVG image."))


if __name__ == "__main__":
    manipulate_pdf(
        svg_source=str(SVG_RESOURCES_DIR / "cauldron.svg"),
        pdf_dest=str(SCRIPT_DIR / "convert_svg_to_layout_image.pdf"),
    )
