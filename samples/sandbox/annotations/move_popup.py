import itextpy
itextpy.load()

import contextlib
from pathlib import Path

from iText.Kernel.Pdf import PdfArray, PdfName, PdfReader, PdfWriter, PdfDocument

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC = str(RESOURCES_DIR / "pdfs" / "hello_sticky_note.pdf")


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def manipulate_pdf(dest):
    with itext_closing(PdfDocument(PdfReader(SRC), PdfWriter(dest))) as pdf_doc:
        page = pdf_doc.GetFirstPage().GetPdfObject()
        annots = page.GetAsArray(PdfName.Annots)

        # Get sticky notes annotation and change the rectangle of that annotation
        sticky = annots.GetAsDictionary(0)
        sticky_rect = sticky.GetAsArray(PdfName.Rect)

        sticky_rectangle = PdfArray([
            sticky_rect.GetAsNumber(0).FloatValue() - 120, sticky_rect.GetAsNumber(1).FloatValue() - 70,
            sticky_rect.GetAsNumber(2).FloatValue(), sticky_rect.GetAsNumber(3).FloatValue() - 30
        ])
        sticky.Put(PdfName.Rect, sticky_rectangle)

        # Get pop-up window annotation and change the rectangle of that annotation
        popup = annots.GetAsDictionary(1)
        popup_rect = popup.GetAsArray(PdfName.Rect)

        popup_rectangle = PdfArray([
            popup_rect.GetAsNumber(0).FloatValue() - 250, popup_rect.GetAsNumber(1).FloatValue(),
            popup_rect.GetAsNumber(2).FloatValue(), popup_rect.GetAsNumber(3).FloatValue() - 250
        ])
        popup.Put(PdfName.Rect, popup_rectangle)


if __name__ == "__main__":
    manipulate_pdf("move_popup.pdf")
