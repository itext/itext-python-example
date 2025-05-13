import itextpy
itextpy.load()

from pathlib import Path

from System.IO import FileInfo
from iText.Svg.Converter import SvgConverter

SCRIPT_DIR = Path(__file__).parent.absolute()
SVG_RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources" / "svg"


def manipulate_pdf(svg_source, pdf_dest):
    # Directly convert the SVG file to a PDF.
    SvgConverter.CreatePdf(FileInfo(svg_source), FileInfo(pdf_dest))


if __name__ == "__main__":
    manipulate_pdf(
        svg_source=str(SVG_RESOURCES_DIR / "cauldron.svg"),
        pdf_dest=str(SCRIPT_DIR / "convert_svg_to_pdf.pdf"),
    )
