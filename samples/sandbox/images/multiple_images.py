import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from iText.IO.Image import ImageDataFactory
from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf import PdfWriter, PdfDocument
from iText.Layout import Document
from iText.Layout.Element import Image

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
IMAGES = (
    str(RESOURCES_DIR / "img" / "berlin2013.jpg"),
    str(RESOURCES_DIR / "img" / "javaone2013.jpg"),
    str(RESOURCES_DIR / "img" / "map_cic.png"),
)


def manipulate_pdf(dest):
    image = Image(ImageDataFactory.Create(IMAGES[0]))
    page_size = PageSize(image.GetImageWidth(), image.GetImageHeight())
    with (disposing(PdfDocument(PdfWriter(dest))) as pdf_doc,
          disposing(Document(pdf_doc, page_size)) as doc):
        for i, image_path in enumerate(IMAGES):
            image = Image(ImageDataFactory.Create(image_path))
            pdf_doc.AddNewPage(PageSize(image.GetImageWidth(), image.GetImageHeight()))
            image.SetFixedPosition(i + 1, 0, 0)
            doc.Add(image)


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "multiple_images.pdf"))
