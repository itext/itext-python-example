import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.IO.Font import PdfEncodings
from iText.IO.Image import ImageDataFactory
from iText.Kernel.Font import PdfFontFactory
from iText.Kernel.Pdf import PdfAConformance, PdfOutputIntent, PdfWriter
from iText.Layout import Document
from iText.Layout.Element import Image, Paragraph
from iText.Pdfa import PdfADocument

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
ICC_PATH = str(RESOURCES_DIR / "data" / "sRGB_CS_profile.icm")
FONT_PATH = str(RESOURCES_DIR / "font" / "OpenSans-Regular.ttf")
IMG_PATH = str(RESOURCES_DIR / "img" / "hero.jpg")


def manipulate_pdf(dest):
    with disposing(FileStream(ICC_PATH, FileMode.Open, FileAccess.Read)) as icc_stream:
        intent = PdfOutputIntent("Custom", "", None, "sRGB IEC61966-2.1", icc_stream)
    with (disposing(PdfADocument(PdfWriter(dest), PdfAConformance.PDF_A_4, intent)) as pdf_doc,
          disposing(Document(pdf_doc)) as document):
        logo_image = Image(ImageDataFactory.Create(IMG_PATH))
        document.Add(logo_image)

        # PDF/A spec requires font to be embedded, iText will warn you if you do something against the PDF/A4 spec
        font = PdfFontFactory.CreateFont(FONT_PATH, PdfEncodings.IDENTITY_H)
        element = (Paragraph("Hello World")
                   .SetFont(font)
                   .SetFontSize(10))
        document.Add(element)


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "pdf_a4.pdf"))
