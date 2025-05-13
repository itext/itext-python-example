import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.Forms.Form.Element import Button, InputField, Radio, TextArea
from iText.Kernel.Colors import ColorConstants
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Borders import SolidBorder
from iText.Layout.Element import Cell, Paragraph, Table

SCRIPT_DIR = Path(__file__).parent.absolute()


def manipulate_pdf(dest):
    with disposing(Document(PdfDocument(PdfWriter(dest)))) as document:
        input_field = InputField("input field")
        input_field.SetValue("John")
        input_field.SetInteractive(True)

        text_area = TextArea("text area")
        text_area.SetValue(
            "I'm a chess player.\n"
            "In future I want to compete in professional chess and be the world champion.\n"
            "My favorite opening is caro-kann.\n"
            "Also I play sicilian defense a lot."
        )
        text_area.SetInteractive(True)

        table = Table(2, False)
        table.AddCell("Name:")
        table.AddCell(Cell().Add(input_field))
        table.AddCell("Personal info:")
        table.AddCell(Cell().Add(text_area))

        male = Radio("male", "radioGroup")
        male.SetChecked(False)
        male.SetInteractive(True)
        male.SetBorder(SolidBorder(1))

        male_text = Paragraph("Male: ")
        male_text.Add(male)

        female = Radio("female", "radioGroup")
        female.SetChecked(True)
        female.SetInteractive(True)
        female.SetBorder(SolidBorder(1))

        female_text = Paragraph("Female: ")
        female_text.Add(female)

        button = Button("submit")
        button.SetValue("Submit")
        button.SetInteractive(True)
        button.SetBorder(SolidBorder(2))
        button.SetWidth(50)
        button.SetBackgroundColor(ColorConstants.LIGHT_GRAY)

        document.Add(table)
        document.Add(male_text)
        document.Add(female_text)
        document.Add(button)


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "create_form_field_through_layout.pdf"))
