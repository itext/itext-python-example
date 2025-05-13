import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfDocument, PdfWriter
from iText.Svg.Converter import SvgConverter
from iText.Svg.Processors.Impl import SvgConverterProperties

SCRIPT_DIR = Path(__file__).parent.absolute()
SVG_RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources" / "svg"


def manipulate_pdf(pdf_dest):
    with disposing(PdfDocument(PdfWriter(pdf_dest))) as pdf_doc:
        # Create new page
        pdf_doc.AddNewPage(PageSize.A4)

        # SVG String
        contents = (
            '<svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">\n'
            '  <style media="(height: 900px)">\n'
            '    circle {\n'
            '      fill: green;\n'
            '    }\n'
            '  </style>\n'
            '\n'
            '  <circle cx="100" cy="100" r="50"/>\n'
            '</svg>'
        )

        # Convert and draw the string directly to the PDF.
        SvgConverter.DrawOnDocument(contents, pdf_doc, 1, SvgConverterProperties())


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "convert_svg_string_to_pdf.pdf"))
