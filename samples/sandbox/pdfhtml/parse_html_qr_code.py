import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.Html2pdf import ConverterProperties, HtmlConverter

from qr_code_tag import QRCodeTagCssApplierFactory, QRCodeTagWorkerFactory

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC_DIR = RESOURCES_DIR / "pdfhtml" / "qrcode"


def manipulate_pdf(html_source, pdf_dest, resource_loc):
    # Create custom tagworker factory
    # The tag <qr> is mapped on a QRCode tagworker. Every other tag is mapped to the default.
    # The tagworker processes a <qr> tag using iText Barcode functionality
    tag_worker_factory = QRCodeTagWorkerFactory()

    # Creates custom css applier factory
    # The tag <qr> is mapped on a BlockCssApplier. Every other tag is mapped to the default.
    css_applier_factory = QRCodeTagCssApplierFactory()

    converter_properties = (ConverterProperties()
                           # Base URI is required to resolve the path to source files
                           .SetBaseUri(resource_loc)
                           .SetTagWorkerFactory(tag_worker_factory)
                           .SetCssApplierFactory(css_applier_factory))

    with (disposing(FileStream(html_source, FileMode.Open)) as html_stream,
          disposing(FileStream(pdf_dest, FileMode.Create, FileAccess.Write)) as pdf_stream):
        HtmlConverter.ConvertToPdf(html_stream, pdf_stream, converter_properties)


if __name__ == "__main__":
    manipulate_pdf(
        html_source=str(SRC_DIR / "qrcode.html"),
        pdf_dest="parse_html_qr_code.pdf",
        resource_loc=str(SRC_DIR),
    )
