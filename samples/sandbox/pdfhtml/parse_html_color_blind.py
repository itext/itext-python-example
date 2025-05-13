import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from System.IO import FileAccess, FileMode, FileShare, FileStream
from iText.Html2pdf import ConverterProperties, HtmlConverter

from _colorblindness import ColorBlindnessCssApplierFactory, ColorBlindnessTransforms

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC_DIR = RESOURCES_DIR / "pdfhtml" / "rainbow"


def manipulate_pdf(html_source, pdf_dest, resource_loc):
    # Base URI is required to resolve the path to source files
    converter_properties = ConverterProperties().SetBaseUri(resource_loc)

    # Create custom css applier factory.
    # Current custom css applier factory handle <div> and <span> tags of html and returns corresponding css applier.
    # All of that css appliers change value of RGB colors
    # to simulate color blindness of people (like Tritanopia, Achromatopsia, etc.)
    css_applier_factory = ColorBlindnessCssApplierFactory(ColorBlindnessTransforms.DEUTERANOMALY)
    converter_properties.SetCssApplierFactory(css_applier_factory)

    with (disposing(FileStream(html_source, FileMode.Open, FileAccess.Read, FileShare.Read)) as html_stream,
          disposing(FileStream(pdf_dest, FileMode.Create, FileAccess.Write)) as pdf_stream):
        HtmlConverter.ConvertToPdf(html_stream, pdf_stream, converter_properties)


if __name__ == "__main__":
    manipulate_pdf(
        html_source=str(SRC_DIR / "rainbow.html"),
        pdf_dest=str(SCRIPT_DIR / "parse_html_color_blind.pdf"),
        resource_loc=str(SRC_DIR),
    )
