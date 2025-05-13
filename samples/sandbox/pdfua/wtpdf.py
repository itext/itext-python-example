import itextpy
itextpy.load()

from itextpy.util import clr_try_cast, disposing

from pathlib import Path

from System.IO import FileAccess, FileMode, FileStream
from iText.Html2pdf import ConverterProperties, HtmlConverter
from iText.Html2pdf.Attach import ITagWorker, ProcessorContext
from iText.Html2pdf.Attach.Impl import DefaultTagWorkerFactory
from iText.Html2pdf.Attach.Impl.Tags import HTagWorker
from iText.Kernel.Pdf import PdfAConformance, PdfOutputIntent, PdfString, \
    PdfVersion, PdfViewerPreferences, PdfWriter, WriterProperties
from iText.Kernel.XMP import XMPMetaFactory
from iText.Layout import IPropertyContainer
from iText.Layout.Element import Div, Paragraph
from iText.Pdfa import PdfADocument
from iText.StyledXmlParser.Node import IElementNode
from iText.StyledXmlParser.Resolver.Font import BasicFontProvider

SCRIPT_DIR = Path(__file__).parent.absolute()
WTPDF_RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources" / "wtpdf"
HTML_PATH = str(WTPDF_RESOURCES_DIR / "article.html")
ICC_PATH = str(WTPDF_RESOURCES_DIR / "sRGB Color Space Profile.icm")
XMP_PATH = str(WTPDF_RESOURCES_DIR / "simplePdfUA2.xmp")


class CustomTagWorkerFactory(DefaultTagWorkerFactory):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.PdfUa"

    _H_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def GetCustomTagWorker(self, tag: IElementNode, context: ProcessorContext) -> ITagWorker:
        if tag.Name() in self._H_TAGS:
            return CustomHTagWorker(tag, context)
        return super().GetCustomTagWorker(tag, context)


class CustomHTagWorker(HTagWorker):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.PdfUa"

    def __init__(self, element: IElementNode, context: ProcessorContext):
        super().__init__(element, context)

    def GetElementResult(self) -> IPropertyContainer:
        # FIXME: For some reason super().GetElementResult() doesn't work.
        #        It just calls this method again, causing infinite recursion.
        element_result = HTagWorker.GetElementResult(self)
        # Duck typing does not really work for .NET types...
        result = clr_try_cast(element_result, Div)
        if result is not None:
            for child in result.GetChildren():
                paragraph = clr_try_cast(child, Paragraph)
                if paragraph is not None:
                    paragraph.SetNeutralRole()
        return element_result


def manipulate_pdf(dest):
    with disposing(FileStream(ICC_PATH, FileMode.Open, FileAccess.Read)) as icc_stream:
        intent = PdfOutputIntent("Custom", "", None, "sRGB IEC61966-2.1", icc_stream)
    writer_props = WriterProperties().SetPdfVersion(PdfVersion.PDF_2_0)
    with disposing(PdfADocument(PdfWriter(dest, writer_props), PdfAConformance.PDF_A_4, intent)) as pdf_doc:
        # Setup the general requirements for a wtpdf document
        with disposing(FileStream(XMP_PATH, FileMode.Open, FileAccess.Read)) as xmp_stream:
            xmp_meta = XMPMetaFactory.Parse(xmp_stream)
        pdf_doc.SetXmpMetadata(xmp_meta)
        pdf_doc.SetTagged()
        pdf_doc.GetCatalog().SetViewerPreferences(PdfViewerPreferences().SetDisplayDocTitle(True))
        pdf_doc.GetCatalog().SetLang(PdfString("en-US"))
        info = pdf_doc.GetDocumentInfo()
        info.SetTitle("Well tagged PDF document")

        # Use custom font provider as we only want embedded fonts
        font_provider = BasicFontProvider(False, False, False)
        font_provider.AddFont(str(WTPDF_RESOURCES_DIR / "NotoSans-Regular.ttf"))
        font_provider.AddFont(str(WTPDF_RESOURCES_DIR / "NotoEmoji-Regular.ttf"))

        converter_properties = (
            ConverterProperties()
            .SetBaseUri(str(WTPDF_RESOURCES_DIR))
            # We need the custom factory to set role of children to null
            # instead of P because P as in element of Hn is not allowed
            # by PDF2.0 spec
            .SetTagWorkerFactory(CustomTagWorkerFactory())
            .SetFontProvider(font_provider)
        )

        with disposing(FileStream(HTML_PATH, FileMode.Open)) as html_stream:
            HtmlConverter.ConvertToPdf(html_stream, pdf_doc, converter_properties)


if __name__ == "__main__":
    manipulate_pdf(str(SCRIPT_DIR / "wtpdf.pdf"))
