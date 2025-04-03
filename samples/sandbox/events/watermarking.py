import itextpy

itextpy.load()

import contextlib
import csv
from pathlib import Path
from sys import stderr

from iText.IO.Exceptions import IOException
from iText.IO.Font.Constants import StandardFonts
from iText.Kernel.Colors import ColorConstants
from iText.Kernel.Font import PdfFontFactory
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Kernel.Pdf.Canvas import PdfCanvas
from iText.Kernel.Pdf.Event import PdfDocumentEvent
from iText.Layout import Canvas, Document
from iText.Layout.Element import Cell, Paragraph, Table
from iText.Layout.Properties import TextAlignment, UnitValue, VerticalAlignment

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = (SCRIPT_DIR / ".." / ".." / "resources").absolute()
DATA_CSV_PATH = str(RESOURCES_DIR / "data" / "united_states.csv")


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


# TODO: Does not yet work in Python.NET: https://github.com/pythonnet/pythonnet/issues/2571
# class WatermarkingEventHandler(AbstractPdfDocumentEventHandler):
class WatermarkingEventHandler:
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.Events"

    def OnAcceptedEvent(self, event: PdfDocumentEvent) -> None:
        pdf_doc = event.GetDocument()
        page = event.GetPage()
        font = None
        try:
            font = PdfFontFactory.CreateFont(StandardFonts.HELVETICA_BOLD)
        except IOException as e:
            # Such an exception isn't expected to occur,
            # because helvetica is one of standard fonts
            print(e.Message, file=stderr)
        pdf_canvas = PdfCanvas(page.NewContentStreamBefore(), page.GetResources(), pdf_doc)
        with itext_closing(Canvas(pdf_canvas, page.GetPageSize())) as canvas:
            (canvas
             .SetFontColor(ColorConstants.LIGHT_GRAY)
             .SetFontSize(60)
             # If the exception has been thrown, the font variable is not initialized.
             # Therefore, None will be set and iText will use the default font - Helvetica
             .SetFont(font)
             .ShowTextAligned(Paragraph("WATERMARK"),
                              298, 421,
                              pdf_doc.GetPageNumber(page),
                              TextAlignment.CENTER, VerticalAlignment.MIDDLE,
                              45))


def handle_csv_line(table, line, font, is_header):
    for i in range(3):
        cell = Cell().Add(Paragraph(line[i]).SetFont(font))
        if is_header:
            table.AddHeaderCell(cell)
        else:
            table.AddCell(cell)


def manipulate_pdf(dest):
    font = PdfFontFactory.CreateFont(StandardFonts.HELVETICA)
    bold = PdfFontFactory.CreateFont(StandardFonts.HELVETICA_BOLD)

    table = Table(UnitValue.CreatePercentArray([4, 1, 3])).UseAllAvailableWidth()

    with open(DATA_CSV_PATH, "rt", newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        line = next(csv_reader)
        handle_csv_line(table, line, bold, True)
        for line in csv_reader:
            handle_csv_line(table, line, font, False)

    with (itext_closing(PdfDocument(PdfWriter(dest))) as pdf_doc,
          itext_closing(Document(pdf_doc)) as doc):
        # TODO: Does not yet work in Python.NET: https://github.com/pythonnet/pythonnet/issues/2571
        # pdf_doc.AddEventHandler(PdfDocumentEvent.END_PAGE, WatermarkingEventHandler())
        doc.Add(table)
        # TODO: Remove this block, when handler variant is working
        watermark_handler = WatermarkingEventHandler()
        for page_index in range(pdf_doc.GetNumberOfPages()):
            page = pdf_doc.GetPage(page_index + 1)
            event = PdfDocumentEvent(PdfDocumentEvent.END_PAGE, page)
            event.SetDocument(pdf_doc)
            watermark_handler.OnAcceptedEvent(event)


if __name__ == "__main__":
    manipulate_pdf("watermarking.pdf")
