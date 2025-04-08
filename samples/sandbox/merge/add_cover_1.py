import itextpy
itextpy.load()

import contextlib
from pathlib import Path

from iText.Kernel.Pdf import PdfReader, PdfWriter, PdfDocument
from iText.Kernel.Utils import PdfMerger

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
COVER_PATH = str(RESOURCES_DIR / "pdfs" / "hero.pdf")
RESOURCE_PATH = str(RESOURCES_DIR / "pdfs" / "pages.pdf")


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def manipulate_pdf(dest):
    with (itext_closing(PdfDocument(PdfWriter(dest))) as pdf_doc,
          itext_closing(PdfDocument(PdfReader(COVER_PATH))) as cover,
          itext_closing(PdfDocument(PdfReader(RESOURCE_PATH))) as resource,
          itext_closing(PdfMerger(pdf_doc)) as merger):
        merger.Merge(cover, 1, 1)
        merger.Merge(resource, 1, resource.GetNumberOfPages())


if __name__ == "__main__":
    manipulate_pdf("add_cover_1.pdf")
