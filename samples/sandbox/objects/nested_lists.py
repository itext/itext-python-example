import itextpy
itextpy.load()

from itextpy.util import disposing

from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import List, ListItem, Paragraph


def manipulate_pdf(dest):
    with disposing(Document(PdfDocument(PdfWriter(dest)))) as document:
        top_level = List()
        top_level_item = ListItem()
        top_level_item.Add(Paragraph().Add("Item 1"))
        top_level.Add(top_level_item)

        second_level = List()
        second_level.Add("Sub Item 1")
        second_level_item = ListItem()
        second_level_item.Add(Paragraph("Sub Item 2"))
        second_level.Add(second_level_item)
        top_level_item.Add(second_level)

        third_level = List()
        third_level.Add("Sub Sub Item 1")
        third_level.Add("Sub Sub Item 2")
        second_level_item.Add(third_level)

        document.Add(top_level)


if __name__ == "__main__":
    manipulate_pdf("nested_lists.pdf")
