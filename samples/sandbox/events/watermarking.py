import itextpy
itextpy.load()

from itextpy.util import disposing

import csv
from pathlib import Path
from sys import stderr

from iText.IO.Exceptions import IOException
from iText.IO.Font.Constants import StandardFonts
from iText.Kernel.Colors import ColorConstants
from iText.Kernel.Font import PdfFontFactory
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Kernel.Pdf.Canvas import PdfCanvas
from iText.Kernel.Pdf.Event import PdfDocumentEvent, PyAbstractPdfDocumentEventHandler
from iText.Layout import Canvas, Document
from iText.Layout.Element import Cell, Paragraph, Table
from iText.Layout.Properties import TextAlignment, UnitValue, VerticalAlignment

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
DATA_CSV_PATH = str(RESOURCES_DIR / "data" / "united_states.csv")


class WatermarkingEventHandler(PyAbstractPdfDocumentEventHandler):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.Events"

    def _OnAcceptedEvent(self, event: PdfDocumentEvent) -> None:
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
        with disposing(Canvas(pdf_canvas, page.GetPageSize())) as canvas:
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

    with (disposing(PdfDocument(PdfWriter(dest))) as pdf_doc,
          disposing(Document(pdf_doc)) as doc):
        watermark_handler = WatermarkingEventHandler()
        pdf_doc.AddEventHandler(PdfDocumentEvent.END_PAGE, watermark_handler)
        doc.Add(table)


if __name__ == "__main__":
    manipulate_pdf("watermarking.pdf")
