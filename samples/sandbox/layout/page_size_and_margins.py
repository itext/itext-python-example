import itextpy
itextpy.load()

import contextlib

from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import AreaBreak, Paragraph


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


def manipulate_pdf(dest):
    page_size = PageSize(200, 200)
    with itext_closing(Document(PdfDocument(PdfWriter(dest)), page_size)) as doc:
        margins_text = ", ".join(map(str, (doc.GetTopMargin(),
                                           doc.GetRightMargin(),
                                           doc.GetBottomMargin(),
                                           doc.GetLeftMargin())))
        p = Paragraph(f"Margins: [{margins_text}]\nPage size: 200*200")
        doc.Add(p)

        # The margins will be applied on the pages,
        # which have been added after the call of this method.
        doc.SetMargins(10, 10, 10, 10)

        doc.Add(AreaBreak())
        p = Paragraph("Margins: [10.0, 10.0, 10.0, 10.0]\nPage size: 200*200")
        doc.Add(p)

        # Add a new A4 page.
        doc.Add(AreaBreak(PageSize.A4))
        p = Paragraph("Margins: [10.0, 10.0, 10.0, 10.0]\nPage size: A4")
        doc.Add(p)

        # Add a new page.
        # The page size will be the same as it is set in the Document.
        doc.Add(AreaBreak())
        p = Paragraph("Margins: [10.0, 10.0, 10.0, 10.0]\nPage size: 200*200")
        doc.Add(p)


if __name__ == "__main__":
    manipulate_pdf("page_size_and_margins.pdf")
