# Uncomment this block, if you wish to force the .NET Core runtime
# import pythonnet
# pythonnet.load('coreclr')

import itextpy
itextpy.load()

# Import necessary namespaces
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Paragraph


# Example: Create a simple PDF document
def create_pdf(output_path):
    writer = PdfWriter(output_path)
    pdf_doc = PdfDocument(writer)
    document = Document(pdf_doc)

    # Add content to the PDF
    document.Add(Paragraph("Hello, World!"))
    document.Add(Paragraph("I was created using iText 9.1.0 in a Python environment"))

    # Close the document
    document.Close()


# Call the function to create a PDF
create_pdf("output.pdf")
