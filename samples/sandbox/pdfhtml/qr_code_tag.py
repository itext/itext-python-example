import itextpy
itextpy.load()

import System
from System.Collections.Generic import Dictionary
from iText.Barcodes import BarcodeQRCode
from iText.Barcodes.Qrcode import EncodeHintType, ErrorCorrectionLevel
from iText.Html2pdf.Attach import ITagWorker, ProcessorContext
from iText.Html2pdf.Attach.Impl import DefaultTagWorkerFactory
from iText.Html2pdf.Css.Apply.Impl import BlockCssApplier, DefaultCssApplierFactory
from iText.Layout import IPropertyContainer
from iText.Layout.Element import Image
from iText.StyledXmlParser.Node import IElementNode


class QRCodeTagWorker(ITagWorker):
    """
    Example of a custom tag worker implementation for pdfHTML.

    The tag worker processes a **>qr** tag using iText Barcode functionality.
    """
    __namespace__ = "Sandbox.PdfHtml"

    _ALLOWED_ERROR_CORRECTION = ("L", "M", "Q", "H",)
    _ALLOWED_CHARSET = ("Cp437", "Shift_JIS", "ISO-8859-1", "ISO-8859-16",)

    def __init__(self, element: IElementNode, context: ProcessorContext):
        # Retrieve all necessary properties to create the barcode
        # Conversion from Python dict didn't work
        hints = Dictionary[EncodeHintType, System.Object]()

        # Character set
        charset = element.GetAttribute("charset")
        if self._check_character_set(charset):
            hints[EncodeHintType.CHARACTER_SET] = charset

        # Error-correction level
        error_correction = element.GetAttribute("errorcorrection")
        if self._check_error_correction_allowed(error_correction):
            error_correction_level = self._get_error_correction_level(error_correction)
            hints[EncodeHintType.ERROR_CORRECTION] = error_correction_level

        # Create the QR-code
        self.qr_code = BarcodeQRCode("placeholder", hints)
        self.qr_code_as_image = None

    def GetElementResult(self) -> IPropertyContainer:
        return self.qr_code_as_image

    def ProcessContent(self, content: str, context: ProcessorContext) -> bool:
        self.qr_code.SetCode(content)
        return True

    def ProcessEnd(self, element: IElementNode, context: ProcessorContext) -> None:
        self.qr_code_as_image = Image(self.qr_code.CreateFormXObject(context.GetPdfDocument()))

    def ProcessTagChild(self, child_tag_worker: ITagWorker, context: ProcessorContext) -> bool:
        return False

    @staticmethod
    def _check_character_set(s: str) -> bool:
        return s in QRCodeTagWorker._ALLOWED_CHARSET

    @staticmethod
    def _check_error_correction_allowed(s: str) -> bool:
        return s.upper() in QRCodeTagWorker._ALLOWED_ERROR_CORRECTION

    @staticmethod
    def _get_error_correction_level(s: str) -> ErrorCorrectionLevel | None:
        if s == "L":
            return ErrorCorrectionLevel.L
        if s == "M":
            return ErrorCorrectionLevel.M
        if s == "Q":
            return ErrorCorrectionLevel.Q
        if s == "H":
            return ErrorCorrectionLevel.H
        return None


class QRCodeTagCssApplierFactory(DefaultCssApplierFactory):
    """
    Example of a custom CssApplier factory for pdfHTML.

    The tag **qr** is mapped on a BlockCssApplier. Every other tag is mapped
    to the default.
    """
    __namespace__ = "Sandbox.PdfHtml"

    def GetCustomCssApplier(self, tag):
        if tag.Name() == "qr":
            return BlockCssApplier()
        return None


class QRCodeTagWorkerFactory(DefaultTagWorkerFactory):
    """
    Example of a custom TagWorkerFactory for pdfHTML.

    The tag **qr** is mapped on a QRCode tag worker. Every other tag is mapped
    to the default.
    """
    __namespace__ = "Sandbox.PdfHtml"

    def GetCustomTagWorker(self, tag, context):
        if tag.Name() == "qr":
            return QRCodeTagWorker(tag, context)
        return None
