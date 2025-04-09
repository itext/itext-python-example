import itextpy
itextpy.load()

import contextlib
from pathlib import Path
from sys import stderr

from iText.IO.Font.Constants import StandardFonts
from iText.IO.Exceptions import IOException
from iText.Kernel.Font import PdfFontFactory
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Kernel.Pdf.Event import PdfDocumentEvent, PyAbstractPdfDocumentEventHandler
from iText.Layout import Canvas, Document
from iText.Layout.Element import AreaBreak, Cell, Paragraph
from iText.Layout.Properties import TextAlignment

SCRIPT_DIR = Path(__file__).parent.absolute()


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


class TextFooterEventHandler(PyAbstractPdfDocumentEventHandler):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.Events"

    def __init__(self, doc: Document):
        super().__init__()
        self.doc = doc

    def _OnAcceptedEvent(self, event: PdfDocumentEvent) -> None:
        page_size = event.GetPage().GetPageSize()
        font = None
        try:
            font = PdfFontFactory.CreateFont(StandardFonts.HELVETICA_OBLIQUE)
        except IOException as e:
            # Such an exception isn't expected to occur,
            # because helvetica is one of standard fonts
            print(e.Message, file=stderr)

        coord_x = ((page_size.GetLeft() + self.doc.GetLeftMargin())
                   + (page_size.GetRight() - self.doc.GetRightMargin())) / 2
        header_y = page_size.GetTop() - self.doc.GetTopMargin() + 10
        footer_y = self.doc.GetBottomMargin()
        with itext_closing(Canvas(event.GetPage(), page_size)) as canvas:
            (canvas
             # If the exception has been thrown, the font variable is not initialized.
             # Therefore, null will be set and iText will use the default font - Helvetica
             .SetFont(font)
             .SetFontSize(5)
             .ShowTextAligned("this is a header", coord_x, header_y, TextAlignment.CENTER)
             .ShowTextAligned("this is a footer", coord_x, footer_y, TextAlignment.CENTER))


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
        text_footer_event_handler = TextFooterEventHandler(doc)
        pdf_doc.AddEventHandler(PdfDocumentEvent.END_PAGE, text_footer_event_handler)

        for i in range(1, 4):
            doc.Add(Paragraph(f"Test {i}"))
            if i < 3:
                doc.Add(AreaBreak())


if __name__ == "__main__":
    manipulate_pdf("text_footer.pdf")
