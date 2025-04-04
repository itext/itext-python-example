import itextpy
itextpy.load()

import contextlib

from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Cell, Paragraph, Table
from iText.Layout.Properties import UnitValue


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def manipulate_pdf(dest):
    with itext_closing(Document(PdfDocument(PdfWriter(dest)))) as doc:
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
    manipulate_pdf("simple_table_9.pdf")
