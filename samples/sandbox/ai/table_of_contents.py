#
# This sample shows an example of generating table of contents for existing
# PDF documents with the help of an LLM with an OpenAI-compatible API.
#
# Before running the sample, make sure, that the `openai` package is installed
# and that the model you are running has a big enough context window to fit the
# whole input document.
#
# Default settings are set to use a Qwen 2.5 model on a local Ollama instance.
# The default Ollama context window is small, so make sure to change it using
# the instructions below.
#
import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from openai import OpenAI

from iText.Kernel.Geom import PageSize
from iText.Kernel.Pdf.Canvas.Parser import PdfTextExtractor
from iText.Kernel.Pdf.Canvas.Parser.Listener import LocationTextExtractionStrategy
from iText.Kernel.Pdf import PdfOutline, PdfReader, PdfWriter, PdfDocument
from iText.Kernel.Pdf.Action import PdfAction
from iText.Kernel.Pdf.Canvas.Draw import DottedLine
from iText.Kernel.Pdf.Navigation import PdfExplicitDestination
from iText.Layout import Canvas
from iText.Layout.Element import List, ListItem, Paragraph, Tab, TabStop
from iText.Layout.Properties import ListNumberingType, TabAlignment

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
INPUT_PDF_PATH = str(RESOURCES_DIR / "pdfs" / "nist.pdf")

#
# This block defines connection to the LLM you want to use. Default values
# will make the script connect to a local Ollama instance with a Qwen 2.5
# model available to it.
#
# If you are going to use Ollama, make sure that you increase the context
# windows size, as the default value is very small. With the default value
# there is a high chance, that the document won't fit into the context window,
# which will result in an incomplete or broken table.
#
# Easiest way to increase the context window is to set env var
# OLLAMA_CONTEXT_LENGTH to a big enough value (like 65536) before starting
# Ollama. Also make sure, that Ollama is version 0.5.13 or above. See this page
# for more info:
#   https://github.com/ollama/ollama/blob/main/docs/faq.md#how-can-i-specify-the-context-window-size
#
OPENAI_BASE_URL = "http://localhost:11434/v1"   # Default local Ollama URL
OPENAI_API_KEY = "EMPTY"                        # No API key needed for Ollama
OPENAI_MODEL = "qwen2.5"


# This is a tree-like structure for storing table of contents data. Root is a
# node without a caption.
class TableEntry:
    def __init__(self, caption: str | None = None):
        self.caption = caption
        self.children = []
        self.page_idx = None

    def __str__(self):
        return self.caption

    def __iter__(self):
        if self.caption is not None:
            yield self
        for child in self.children:
            for node in child:
                yield node


# This function converts pages of the PDF document to text.
def get_pages_as_text(doc: PdfDocument) -> list[str]:
    text_extractor = PdfTextExtractor()
    # This is the default strategy, which works relatively fine. But you might
    # get a better result with a custom one, which tries to preserve spacial
    # data with whitespace.
    strategy = LocationTextExtractionStrategy()
    pages = (doc.GetPage(i + 1) for i in range(doc.GetNumberOfPages()))
    return [text_extractor.GetTextFromPage(page, strategy) for page in pages]


# This function removes a <think>...</think> block at the start of the LLM
# response, if present
def strip_think(response_data: str) -> str:
    if response_data.startswith("<think>"):
        return response_data.partition('</think>')[2]
    return response_data


# This function parses the ToC LLM response into a tree-like structure.
def parse_response(response_lines: list[str]) -> TableEntry:
    result = TableEntry()
    for line in response_lines:
        # We expect strings like "1.2.3 Chapter" here
        stripped = line.strip()
        if not stripped:
            continue
        index_str, caption = stripped.split(" ", maxsplit=1)
        index_seq = [int(i) for i in index_str.split(".") if i]
        entry_list = result.children
        for index in index_seq[:-1]:
            entry_list = entry_list[index - 1].children
        pos = index_seq[-1] - 1
        if pos != len(entry_list):
            raise Exception("Unexpected index value")
        entry_list.append(TableEntry(caption))
    return result


# This function augments the table of contents with page numbers for each
# entry.
#
# Since LLM is not that reliable with giving a precise location for entries,
# we will assume, that we can find them in the original text and recover the
# page data that way. This is not ideal, but work relatively well in practice.
def add_page_data(toc_data: TableEntry, pages: list[str]) -> None:
    casefold_pages = [p.casefold() for p in pages]
    prev_page_idx = 0
    prev_str_idx = 0
    for node in toc_data:
        for page_offset, page in enumerate(casefold_pages[prev_page_idx:]):
            casefold_caption = node.caption.casefold()
            str_idx = page.find(casefold_caption, prev_str_idx if page_offset == 0 else 0)
            if str_idx != -1:
                prev_page_idx += page_offset
                prev_str_idx = str_idx + len(casefold_caption)
                break
        node.page_idx = prev_page_idx


# This function ask the LLM to generate the table of contents for the provided
# pages of text. The result gets parsed into a tree-like structure.
def generate_toc_data(pages: list[str]) -> TableEntry:
    openai_client = OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "You are about to read text of a PDF document:"},
        {"role": "user", "content": "\n\n".join(pages)},
        {"role": "user", "content": "Generate a numbered table of contents for the document. "
                                    "Write only the table entries."},
    ]
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.1,
    )
    response_content = response.choices[0].message.content
    toc_data = parse_response(strip_think(response_content).splitlines())
    add_page_data(toc_data, pages)
    return toc_data


# This function just recursively generates the Bookmarks tree for the
# resulting PDF document.
def fill_outline(doc: PdfDocument, outline_root: PdfOutline, toc_children: list[TableEntry]) -> None:
    for entry in toc_children:
        page_num = entry.page_idx + 1
        outline = outline_root.AddOutline(entry.caption)
        # +1 since we added the ToC page at the start
        outline.AddDestination(PdfExplicitDestination.CreateFit(doc.GetPage(page_num + 1)))
        if entry.children:
            fill_outline(doc, outline, entry.children)


# This function recursively generates a table of contents, using numbered list
# from the iText layout engine.
def generate_list(doc: PdfDocument, tab_stops: list[TabStop], toc_children: list[TableEntry]) -> List:
    l = List(ListNumberingType.DECIMAL)
    for entry in toc_children:
        page_num = entry.page_idx + 1
        # +1 since we added the ToC page at the start
        page_dest = PdfExplicitDestination.CreateFit(doc.GetPage(page_num + 1))
        p = (Paragraph()
             .SetMargin(2)
             .SetFontSize(12)
             .AddTabStops(tab_stops)
             .Add(entry.caption)
             .Add(Tab())
             .Add(str(page_num))
             .SetAction(PdfAction.CreateGoTo(page_dest)))
        item = ListItem()
        item.Add(p)
        if entry.children:
            item.Add(generate_list(doc, tab_stops, entry.children))
        l.Add(item)
    return l


# This function creates a page with the table of contents and prepends it to
# the PDF document. If there are no bookmarks present, then they will be added
# too.
#
# This function at the moment assumes, that everything will fit into one page.
def add_toc_to_doc(doc: PdfDocument, toc_data: TableEntry) -> None:
    page_size = PageSize(doc.GetPage(1).GetPageSize())
    toc_page = doc.AddNewPage(1, page_size)
    content_box = (toc_page.GetCropBox()
                   .ApplyMargins(36, 36, 36, 36, False))
    with disposing(Canvas(toc_page, content_box)) as toc_canvas:
        header = (Paragraph("Table of Contents")
                  .SetFontSize(24))
        toc_canvas.Add(header)
        page_num_tab_stop = TabStop(content_box.GetWidth(), TabAlignment.RIGHT, DottedLine())
        toc_canvas.Add(generate_list(doc, [page_num_tab_stop], toc_data.children))

    # Now adding bookmarks as well
    outline_root = doc.GetOutlines(True)
    # Do not ruin existing bookmarks...
    if len(outline_root.GetAllChildren()) == 0:
        fill_outline(doc, doc.GetOutlines(True), toc_data.children)


# The algorithm is pretty straightforward:
#   1. Convert PDF document pages to text.
#   2. Send pages to an LLM and ask it to generate the table of contents.
#   3. Parse the LLM response.
#   4. Generate and add the table of contents page, together with bookmarks.
def main(in_path: str, out_path: str) -> None:
    with disposing(PdfDocument(PdfReader(in_path), PdfWriter(out_path))) as doc:
        pages = get_pages_as_text(doc)
        if not pages:
            raise Exception("Document is empty!")
        toc_data = generate_toc_data(pages)
        if not toc_data.children:
            raise Exception("Table of Contents is empty!")
        add_toc_to_doc(doc, toc_data)


# Call the function to create a PDF
main(INPUT_PDF_PATH, "table_of_contents.pdf")
