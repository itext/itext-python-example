import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.Forms.Form.Element import InputField
from iText.IO.Font import PdfEncodings
from iText.IO.Image import ImageDataFactory
from iText.Kernel.Colors import ColorConstants
from iText.Kernel.Font import PdfFontFactory
from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfArray, PdfName, PdfString, PdfUAConformance, PdfWriter
from iText.Kernel.Pdf.Tagging import PdfStructureAttributes, StandardRoles
from iText.Layout import Document
from iText.Layout.Element import AreaBreak, Cell, Image, List, ListItem, Paragraph, Table
from iText.Layout.Properties import AreaBreakType
from iText.Pdfua import PdfUAConfig, PdfUADocument

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
FONT_PATH = str(RESOURCES_DIR / "font" / "FreeSans.ttf")
DOG_PATH = str(RESOURCES_DIR / "img" / "dog.bmp")
FOX_PATH = str(RESOURCES_DIR / "img" / "fox.bmp")


def add_form_fields(document: Document) -> None:
    # Formfields are also possible
    field = InputField("name")
    field.GetAccessibilityProperties().SetAlternateDescription("Name")
    field.SetValue("John Doe")
    field.SetBackgroundColor(ColorConstants.CYAN)
    document.Add(field)

    field_2 = InputField("email")
    field_2.GetAccessibilityProperties().SetAlternateDescription("Email")
    field_2.SetValue("sales@apryse.com")
    field_2.SetInteractive(True)
    field_2.SetBackgroundColor(ColorConstants.YELLOW)
    document.Add(field_2)


def add_tables(document: Document) -> None:
    # Add a table with the automatic column scope
    table = Table(2)
    header_cell_1 = Cell().Add(Paragraph("Header 1"))
    header_cell_1.GetAccessibilityProperties().SetRole(StandardRoles.TH)
    header_cell_2 = Cell().Add(Paragraph("Header 2"))
    header_cell_2.GetAccessibilityProperties().SetRole(StandardRoles.TH)

    table.AddHeaderCell(header_cell_1)
    table.AddHeaderCell(header_cell_2)

    table.AddCell(Cell().Add(Paragraph("data 1")))
    table.AddCell(Cell().Add(Paragraph("data 2")))

    document.Add(table)
    document.Add(Paragraph("\n\n"))
    # Add a table with row scope
    table_2 = Table(2)
    header_cell_3 = Cell().Add(Paragraph("Header 1"))
    attributes = PdfStructureAttributes("Table")
    attributes.AddEnumAttribute("Scope", "Row")
    header_cell_3.GetAccessibilityProperties().AddAttributes(attributes)
    header_cell_3.GetAccessibilityProperties().SetRole(StandardRoles.TH)

    header_cell_4 = Cell().Add(Paragraph("Header 2"))
    header_cell_4.GetAccessibilityProperties().SetRole(StandardRoles.TH)
    attributes2 = PdfStructureAttributes("Table")
    attributes2.AddEnumAttribute("Scope", "Row")
    header_cell_4.GetAccessibilityProperties().AddAttributes(attributes2)

    table_2.AddCell(header_cell_3)
    table_2.AddCell(Cell().Add(Paragraph("data 1")))
    table_2.AddCell(header_cell_4)
    table_2.AddCell(Cell().Add(Paragraph("data 2")))
    document.Add(table_2)

    # For complex tables you can also make use of Id's
    table_3 = Table(2)
    for i in range(4):
        cell = Cell().Add(Paragraph(f"data {i}"))
        cell_attributes = PdfStructureAttributes("Table")
        headers = PdfArray()
        headers.Add(PdfString("header_id_1"))
        cell_attributes.GetPdfObject().Put(PdfName.Headers, headers)
        cell.GetAccessibilityProperties().AddAttributes(cell_attributes)
        table_3.AddCell(cell)

    header_cell_5 = Cell(1, 2).Add(Paragraph("Header 1"))
    header_cell_5.GetAccessibilityProperties().SetRole(StandardRoles.TH)
    header_cell_5.GetAccessibilityProperties().SetStructureElementIdString("header_id_1")
    header_attributes = PdfStructureAttributes("Table")
    header_attributes.AddEnumAttribute("Scope", "None")
    header_cell_5.GetAccessibilityProperties().AddAttributes(header_attributes)
    table_3.AddCell(header_cell_5)
    document.Add(table_3)

    document.Add(AreaBreak(AreaBreakType.NEXT_PAGE))
    # Let's add some headings
    h1 = Paragraph("Heading 1").SetFontSize(20)
    h1.GetAccessibilityProperties().SetRole(StandardRoles.H1)
    document.Add(h1)
    h2 = Paragraph("Heading 2").SetFontSize(18)
    h2.GetAccessibilityProperties().SetRole(StandardRoles.H2)
    document.Add(h2)
    h3 = Paragraph("Heading 3").SetFontSize(16)
    h3.GetAccessibilityProperties().SetRole(StandardRoles.H3)
    document.Add(h3)


def manipulate_pdf(dest):
    ua_config = PdfUAConfig(PdfUAConformance.PDF_UA_1, "Some title", "en-US")
    with (disposing(PdfUADocument(PdfWriter(dest), ua_config)) as pdf_doc,
          disposing(Document(pdf_doc, PageSize.A4.Rotate())) as document):
        # PDF UA requires font to be embedded, this is the way we want to do it
        font = PdfFontFactory.CreateFont(
            FONT_PATH,
            PdfEncodings.WINANSI,
            PdfFontFactory.EmbeddingStrategy.PREFER_EMBEDDED
        )
        document.SetFont(font)

        p = Paragraph()
        # You can also set it on individual elements if you want to
        p.SetFont(font)
        p.Add("The quick brown ")
        document.Add(p)

        # Images require to have an alternative description
        img = Image(ImageDataFactory.Create(FOX_PATH))
        img.GetAccessibilityProperties().SetAlternateDescription("Fox")
        document.Add(img)

        p = Paragraph(" jumps over the lazy ")
        document.Add(p)

        img = Image(ImageDataFactory.Create(DOG_PATH))
        img.GetAccessibilityProperties().SetAlternateDescription("Dog")
        document.Add(img)

        p = Paragraph("\n\n\n\n\n\n\n\n\n\n\n\n").SetFontSize(20)
        document.Add(p)

        # Let's add a list
        list = List().SetFontSize(20)
        list.Add(ListItem("quick"))
        list.Add(ListItem("brown"))
        list.Add(ListItem("fox"))
        list.Add(ListItem("jumps"))
        list.Add(ListItem("over"))
        list.Add(ListItem("the"))
        list.Add(ListItem("lazy"))
        list.Add(ListItem("dog"))
        document.Add(list)

        document.Add(AreaBreak(AreaBreakType.NEXT_PAGE))
        add_tables(document)
        document.Add(AreaBreak(AreaBreakType.NEXT_PAGE))

        add_form_fields(document)


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "pdf_ua.pdf"))
