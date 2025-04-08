import itextpy
itextpy.load()

import contextlib
from pathlib import Path

from iText.Kernel.Pdf import PdfName, PdfNumber, PdfWriter, PdfDocument
from iText.Kernel.Pdf.Event import AbstractPdfDocumentEventHandler, PdfDocumentEvent
from iText.Layout import Document
from iText.Layout.Element import AreaBreak, Cell, Paragraph

SCRIPT_DIR = Path(__file__).parent.absolute()


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


PORTRAIT = PdfNumber(0)
LANDSCAPE = PdfNumber(90)
INVERTEDPORTRAIT = PdfNumber(180)
SEASCAPE = PdfNumber(270)

HELLO_WORLD = Paragraph("Hello World!")


class PageRotationEventHandler(AbstractPdfDocumentEventHandler):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.Events"

    def __init__(self):
        super().__init__()
        self.rotation = PORTRAIT

    def OnAcceptedEvent(self, event: PdfDocumentEvent) -> None:
        event.GetPage().Put(PdfName.Rotate, self.rotation)


def handle_csv_line(table, line, font, is_header):
    for i in range(3):
        cell = Cell().Add(Paragraph(line[i]).SetFont(font))
        if is_header:
            table.AddHeaderCell(cell)
        else:
            table.AddCell(cell)


def manipulate_pdf(dest):
    with (itext_closing(PdfDocument(PdfWriter(dest))) as pdf_doc,
          itext_closing(Document(pdf_doc)) as doc):
        page_rotation_handler = PageRotationEventHandler()
        pdf_doc.AddEventHandler(PdfDocumentEvent.START_PAGE, page_rotation_handler)

        doc.Add(HELLO_WORLD)

        for rotation in (LANDSCAPE, INVERTEDPORTRAIT, SEASCAPE, PORTRAIT):
            page_rotation_handler.rotation = rotation
            doc.Add(AreaBreak())
            doc.Add(HELLO_WORLD)


if __name__ == "__main__":
    manipulate_pdf("page_rotation.pdf")
