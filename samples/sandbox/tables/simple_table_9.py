import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Cell, Paragraph, Table
from iText.Layout.Properties import UnitValue

SCRIPT_DIR = Path(__file__).parent.absolute()


def manipulate_pdf(dest):
    with disposing(Document(PdfDocument(PdfWriter(dest)))) as doc:
        doc.Add(Paragraph("With 3 columns:"))
        table = Table(UnitValue.CreatePercentArray([10, 10, 80]))
        table.SetMarginTop(5)
        table.AddCell("Col a")
        table.AddCell("Col b")
        table.AddCell("Col c")
        table.AddCell("Value a")
        table.AddCell("Value b")
        table.AddCell("This is a long description for column c. "
                      "It needs much more space hence we made sure "
                      "that the third column is wider.")
        doc.Add(table)

        doc.Add(Paragraph("With 2 columns:"))

        table = Table(UnitValue.CreatePercentArray(2)).UseAllAvailableWidth()
        table.SetMarginTop(5)
        table.AddCell("Col a")
        table.AddCell("Col b")
        table.AddCell("Value a")
        table.AddCell("Value b")
        table.AddCell(Cell(1, 2).Add(Paragraph("Value b")))
        table.AddCell(Cell(1, 2).Add(Paragraph("This is a long description for column c. "
                                               "It needs much more space hence we made sure "
                                               "that the third column is wider.")))
        table.AddCell("Col a")
        table.AddCell("Col b")
        table.AddCell("Value a")
        table.AddCell("Value b")
        table.AddCell(Cell(1, 2).Add(Paragraph("Value b")))
        table.AddCell(Cell(1, 2).Add(Paragraph("This is a long description for column c. "
                                               "It needs much more space hence we made sure "
                                               "that the third column is wider.")))

        doc.Add(table)


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "simple_table_9.pdf"))
