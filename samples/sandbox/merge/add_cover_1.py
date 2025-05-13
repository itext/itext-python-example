import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.Kernel.Pdf import PdfReader, PdfWriter, PdfDocument
from iText.Kernel.Utils import PdfMerger

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
COVER_PATH = str(RESOURCES_DIR / "pdfs" / "hero.pdf")
RESOURCE_PATH = str(RESOURCES_DIR / "pdfs" / "pages.pdf")


def manipulate_pdf(dest):
    with (disposing(PdfDocument(PdfReader(COVER_PATH))) as cover,
          disposing(PdfDocument(PdfReader(RESOURCE_PATH))) as resource,
          disposing(PdfDocument(PdfWriter(dest))) as pdf_doc):
        merger = PdfMerger(pdf_doc)
        merger.Merge(cover, 1, 1)
        merger.Merge(resource, 1, resource.GetNumberOfPages())


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "add_cover_1.pdf"))
