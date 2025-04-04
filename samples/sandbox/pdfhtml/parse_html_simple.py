import itextpy
itextpy.load()

from pathlib import Path

from System.IO import FileAccess, FileMode, FileShare, FileStream
from iText.Html2pdf import ConverterProperties, HtmlConverter

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = (SCRIPT_DIR / ".." / ".." / "resources").absolute()
SRC_DIR = RESOURCES_DIR / "pdfhtml" / "rainbow"


def manipulate_pdf(html_source, pdf_dest, resource_loc):
    converter_properties = ConverterProperties().SetBaseUri(resource_loc)
    HtmlConverter.ConvertToPdf(
        FileStream(html_source, FileMode.Open, FileAccess.Read, FileShare.Read),
        FileStream(pdf_dest, FileMode.Create, FileAccess.Write),
        converter_properties
    )


if __name__ == "__main__":
    manipulate_pdf(
        html_source=str(SRC_DIR / "rainbow.html"),
        pdf_dest="parse_html_simple.pdf",
        resource_loc=str(SRC_DIR),
    )
