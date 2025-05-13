import itextpy
itextpy.load()

from iText.Html2pdf.Attach import ITagWorker, ProcessorContext
from iText.Html2pdf.Css import CssConstants
from iText.Html2pdf.Css.Apply import ICssApplier
from iText.Html2pdf.Css.Apply.Impl import BlockCssApplier, DefaultCssApplierFactory, SpanTagCssApplier
from iText.Html2pdf.Html import TagConstants
from iText.Kernel.Colors import WebColors
from iText.StyledXmlParser.Node import IElementNode, IStylesContainer


def _scale_color_float_array(colors):
    res = [255.0 * c for c in colors[:3]]
    res.append(float(colors[3]))
    return res


def _transform_color(color_blindness: str, original_color: str) -> str:
    # Get RGB colors values
    rgba_color = list(WebColors.GetRGBAColor(original_color))
    rgb_color = rgba_color[:3]

    # Change RGB colors values to corresponding colour blindness RGB values
    new_colour_rgb = ColorBlindnessTransforms.simulate_color_blindness(color_blindness, rgb_color)
    new_colour_rgba = new_colour_rgb[0:3] + [rgba_color[3]]

    # Scale and return changed color values
    new_color_array = _scale_color_float_array(new_colour_rgba)
    new_color_string = "rgba(" + ','.join(str(int(c)) for c in new_color_array) + ")"

    return new_color_string


class ColorBlindnessTransforms:
    PROTANOPIA = "Protanopia"
    PROTANOPIA_TRANSFORM = [
        [0.5667, 0.43333, 0.0],
        [0.55833, 0.44167, 0.0],
        [0.0, 0.24167, 0.75833],
    ]

    DEUTERANOMALY = "Deuteranomaly"
    DEUTERANOMALY_TRANSFORM = [
        [0.8, 0.2, 0.0],
        [0.25833, 0.74167, 0.0],
        [0.0, 0.14167, 0.85833],
    ]

    @staticmethod
    def simulate_color_blindness(code: str, original_rgb: list[float]) -> list[float]:
        if code == ColorBlindnessTransforms.PROTANOPIA:
            return ColorBlindnessTransforms._simulate(original_rgb, ColorBlindnessTransforms.PROTANOPIA_TRANSFORM)
        if code == ColorBlindnessTransforms.DEUTERANOMALY:
            return ColorBlindnessTransforms._simulate(original_rgb, ColorBlindnessTransforms.DEUTERANOMALY_TRANSFORM)
        return original_rgb

    @staticmethod
    def _simulate(original_rgb: list[float], transform_values: list[list[float]]) -> list[float]:
        # Number of RGB colors
        nr_of_channels = 3
        result = [0.0] * 3

        for i in range(nr_of_channels):
            for j in range(nr_of_channels):
                result[i] += original_rgb[j] * transform_values[i][j]

        return result


class ColorBlindBlockCssApplier(BlockCssApplier):
    """
    Css applier extending from a blockcssapplier that transforms standard
    colors into the ones colorblind people see.
    """
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.PdfHtml"

    def __init__(self):
        super().__init__()
        self.color_blindness = ColorBlindnessTransforms.PROTANOPIA

    def set_color_blindness(self, color_blindness: str):
        """Set the from of color blindness to simulate."""
        self.color_blindness = color_blindness

    def Apply(self, context: ProcessorContext, styles_container: IStylesContainer, tag_worker: ITagWorker):
        css_styles = styles_container.GetStyles()
        if css_styles.ContainsKey(CssConstants.COLOR):
            new_color = _transform_color(self.color_blindness, css_styles[CssConstants.COLOR])
            css_styles[CssConstants.COLOR] = new_color
            styles_container.SetStyles(css_styles)

        if css_styles.ContainsKey(CssConstants.BACKGROUND_COLOR):
            new_color = _transform_color(self.color_blindness, css_styles[CssConstants.BACKGROUND_COLOR])
            css_styles[CssConstants.BACKGROUND_COLOR] = new_color
            styles_container.SetStyles(css_styles)

        super().Apply(context, styles_container, tag_worker)


class ColorBlindSpanTagCssApplier(SpanTagCssApplier):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.PdfHtml"

    def __init__(self):
        super().__init__()
        self.color_blindness = ColorBlindnessTransforms.PROTANOPIA

    def set_color_blindness(self, color_blindness: str):
        """Set the from of color blindness to simulate."""
        self.color_blindness = color_blindness

    def Apply(self, context: ProcessorContext, styles_container: IStylesContainer, tag_worker: ITagWorker):
        css_styles = styles_container.GetStyles()
        if css_styles.ContainsKey(CssConstants.COLOR):
            new_color = _transform_color(self.color_blindness, css_styles[CssConstants.COLOR])
            css_styles[CssConstants.COLOR] = new_color
            styles_container.SetStyles(css_styles)

        if css_styles.ContainsKey(CssConstants.BACKGROUND_COLOR):
            new_color = _transform_color(self.color_blindness, css_styles[CssConstants.BACKGROUND_COLOR])
            css_styles[CssConstants.BACKGROUND_COLOR] = new_color
            styles_container.SetStyles(css_styles)

        super().Apply(context, styles_container, tag_worker)


class ColorBlindnessCssApplierFactory(DefaultCssApplierFactory):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.PdfHtml"

    def __init__(self, color_type: str):
        super().__init__()
        self.color_type = color_type

    def GetCustomCssApplier(self, tag: IElementNode) -> ICssApplier | None:
        if tag.Name() == TagConstants.DIV:
            applier = ColorBlindBlockCssApplier()
            applier.set_color_blindness(self.color_type)
            return applier

        if tag.Name() == TagConstants.SPAN:
            applier = ColorBlindSpanTagCssApplier()
            applier.set_color_blindness(self.color_type)
            return applier

        return None
