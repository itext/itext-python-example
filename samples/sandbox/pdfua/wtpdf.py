import itextpy
itextpy.load()

import contextlib
from pathlib import Path

import clr

from System import Convert
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


# Inspired from https://github.com/pythonnet/pythonnet/issues/2213#issuecomment-1671252320
def try_cast(typ, obj):
    clr_type = clr.GetClrType(typ)
    if not clr_type.IsInstanceOfType(obj):
        return None
    return Convert.ChangeType(obj, clr_type)


@contextlib.contextmanager
def itext_closing(obj):
    try:
        yield obj
    finally:
        obj.Close()


@contextlib.contextmanager
def disposable(obj):
    try:
        yield obj
    finally:
        obj.Dispose()


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
        #        It just call this method again, causing infinite recursion.
        element_result = HTagWorker.GetElementResult(self)
        # Duck typing does not really work for .NET types...
        result = try_cast(Div, element_result)
        if result is not None:
            for child in result.GetChildren():
                paragraph = try_cast(Paragraph, child)
                if paragraph is not None:
                    paragraph.SetNeutralRole()
        return element_result


def manipulate_pdf(dest):
    icc_stream = FileStream(ICC_PATH, FileMode.Open, FileAccess.Read)
    intent = PdfOutputIntent("Custom", "", None, "sRGB IEC61966-2.1", icc_stream)
    writer_props = WriterProperties().SetPdfVersion(PdfVersion.PDF_2_0)
    with itext_closing(PdfADocument(PdfWriter(dest, writer_props), PdfAConformance.PDF_A_4, intent)) as pdf_doc:
        # Setup the general requirements for a wtpdf document
        with disposable(FileStream(XMP_PATH, FileMode.Open, FileAccess.Read)) as xmp_stream:
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

        with disposable(FileStream(HTML_PATH, FileMode.Open)) as html_stream:
            HtmlConverter.ConvertToPdf(html_stream, pdf_doc, converter_properties)


if __name__ == "__main__":
    manipulate_pdf("wtpdf.pdf")
