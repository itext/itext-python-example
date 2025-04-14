import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.Kernel.Pdf.Action import PdfAction
from iText.Kernel.Pdf.Annot import PdfAnnotation
from iText.Kernel.Pdf.Navigation import PdfExplicitDestination
from iText.Kernel.Pdf import PdfReader, PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Link, Paragraph
from iText.Layout.Properties import TextAlignment, VerticalAlignment

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC = str(RESOURCES_DIR / "pdfs" / "primes.pdf")


def manipulate_pdf(dest):
    with (disposing(PdfDocument(PdfReader(SRC), PdfWriter(dest))) as pdf_doc,
          disposing(Document(pdf_doc)) as doc):
        # Make the link destination page fit to the display
        destination = PdfExplicitDestination.CreateFit(pdf_doc.GetPage(3))
        link = Link(
            "This is a link. Click it and you'll be forwarded to another page in this document.",
            # Add link to the 3rd page
            PdfAction.CreateGoTo(destination)
        )

        # Set highlighting type which is enabled after a click on the annotation
        link.GetLinkAnnotation().SetHighlightMode(PdfAnnotation.HIGHLIGHT_INVERT)
        p = Paragraph(link).SetWidth(240)
        doc.ShowTextAligned(p, 320, 695, 1, TextAlignment.LEFT, VerticalAlignment.TOP, 0)


if __name__ == "__main__":
    manipulate_pdf("add_link_annotation_5.pdf")
