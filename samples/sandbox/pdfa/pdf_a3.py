import itextpy
itextpy.load()

import contextlib
import csv
from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.IO.Font import PdfEncodings
from iText.Kernel.Font import PdfFontFactory
from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfAConformance, PdfDate, PdfDictionary, PdfName, PdfOutputIntent, PdfWriter
from iText.Kernel.Pdf.Filespec import PdfFileSpec
from iText.Layout import Document
from iText.Layout.Element import Cell, Paragraph, Table
from iText.Layout.Properties import UnitValue
from iText.Pdfa import PdfADocument

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
ICC_PATH = str(RESOURCES_DIR / "data" / "sRGB_CS_profile.icm")
DATA_CSV_PATH = str(RESOURCES_DIR / "data" / "united_states.csv")
FONT_REGULAR = str(RESOURCES_DIR / "font" / "OpenSans-Regular.ttf")
FONT_BOLD = str(RESOURCES_DIR / "font" / "OpenSans-Bold.ttf")


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def handle_csv_line(table, line, font, font_size, is_header):
    for token in line:
        cell = Cell().Add(Paragraph(token).SetFont(font).SetFontSize(font_size))
        if is_header:
            table.AddHeaderCell(cell)
        else:
            table.AddCell(cell)


def manipulate_pdf(dest):
    font = PdfFontFactory.CreateFont(FONT_REGULAR, PdfEncodings.IDENTITY_H)
    bold = PdfFontFactory.CreateFont(FONT_BOLD, PdfEncodings.IDENTITY_H)

    icc_stream = FileStream(ICC_PATH, FileMode.Open, FileAccess.Read)
    intent = PdfOutputIntent("Custom", "", None, "sRGB IEC61966-2.1", icc_stream)
    with (itext_closing(PdfADocument(PdfWriter(dest), PdfAConformance.PDF_A_3B, intent)) as pdf_doc,
          itext_closing(Document(pdf_doc, PageSize.A4.Rotate())) as document):
        parameters = PdfDictionary()
        parameters.Put(PdfName.ModDate, PdfDate().GetPdfObject())

        # Embeds file to the document
        file_spec = PdfFileSpec.CreateEmbeddedFileSpec(
            pdf_doc,
            Path(DATA_CSV_PATH).read_bytes(),
            "united_states.csv",
            "united_states.csv",
            PdfName("text/csv"),
            parameters,
            PdfName.Data
        )
        pdf_doc.AddAssociatedFile("united_states.csv", file_spec)

        table = Table(UnitValue.CreatePercentArray([4, 1, 3, 4, 3, 3, 3, 3, 1])).UseAllAvailableWidth()

        with open(DATA_CSV_PATH, "rt", newline="") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            line = next(csv_reader)
            handle_csv_line(table, line, bold, 10, True)
            for line in csv_reader:
                handle_csv_line(table, line, font, 10, False)

        document.Add(table)


if __name__ == "__main__":
    manipulate_pdf("pdf_a3.pdf")
