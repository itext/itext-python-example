#!/usr/bin/env python3

#
# This is a simple script, which patches the iText 9.1.0 binaries to work
# better under Python.NET.
#

import shutil
import sys
from collections import namedtuple
from pathlib import Path

Patch = namedtuple('Patch', ('name', 'marker', 'replacement'))
PatchSet = namedtuple('PatchSet', ('binary_path', 'patches'))


SCRIPT_DIR = Path(__file__).parent.absolute()
# Path to the .NET binaries we want to patch
ITEXT_BINARIES_DIR = SCRIPT_DIR / 'itextpy' / 'binaries'
# Path to the iText.IO binary
ITEXT_IO_PATH = ITEXT_BINARIES_DIR / 'itext.io.dll'
# Path to the iText.Kernel binary
ITEXT_KERNEL_PATH = ITEXT_BINARIES_DIR / 'itext.kernel.dll'
# Path to the iText.Signature binary
ITEXT_SIGN_PATH = ITEXT_BINARIES_DIR / 'itext.sign.dll'
# Path to the iText.Html2Pdf binary
ITEXT_HTML2PDF_PATH = ITEXT_BINARIES_DIR / 'itext.html2pdf.dll'

PATCH_SETS = (
    PatchSet(
        binary_path=ITEXT_IO_PATH,
        patches=[
            # This patch is fix an exception, which happens, when you are
            # running under .NET Core.
            #
            # What the patch does is that it modifies this check:
            # https://github.com/itext/itext-dotnet/blob/74700467506d83c6c5c9031cdb31181072f79ba0/itext/itext.io/itext/io/util/ResourceUtil.cs#L227
            #
            # It replaces this line:
            #     if (FileUtil.GetBaseDirectory() != null) {
            # With this:
            #     return; {
            #
            # So now unconditionally skips the last if block. Since we don't bundle the
            # font libraries, it shouldn't have any negative effects. Binary is, also, not
            # signed, so we can safely do this.
            #
            # This should not be required in the next iText version.
            Patch(
                name="ResourceUtil",
                marker=bytes([
                    # // [174 7 - 174 47]
                    # IL_002e: call         string [itext.commons]iText.Commons.Utils.FileUtil::GetBaseDirectory()
                    0x28, 0xA7, 0x00, 0x00, 0x0A,
                    # IL_0033: brfalse      IL_00b8
                    0x39, 0x80, 0x00, 0x00, 0x00,
                    # // [176 31 - 176 87]
                    # IL_0038: call         string [itext.commons]iText.Commons.Utils.FileUtil::GetBaseDirectory()
                    0x28, 0xA7, 0x00, 0x00, 0x0A,
                    # IL_003d: ldstr        "*.dll"
                    0x72, 0xA7, 0x14, 0x00, 0x70,
                    # IL_0042: call         string[] [netstandard]System.IO.Directory::GetFiles(string, string)
                    0x28, 0xA8, 0x00, 0x00, 0x0A,
                    # IL_0047: stloc.2      // V_2
                    0x0C,
                ]),
                replacement=bytes([
                    # IL_002e: ret nop nop nop nop
                    #          ^ return from function (i.e. skip the if block entirely)
                    0x2A, 0x00, 0x00, 0x00, 0x00,
                    # IL_002f: nop nop nop nop nop
                    0x00, 0x00, 0x00, 0x00, 0x00,
                    # Everything else remains as-is
                ]),
            ),
        ],
    ),
    PatchSet(
        binary_path=ITEXT_KERNEL_PATH,
        patches=[
            # As of writing this patch, it is impossible to override protected
            # methods in Python.NET. This is an annoying problem for using
            # AbstractPdfDocumentEventHandler, which has an abstract protected
            # method OnAcceptedEvent.
            #
            # Relevant issues in Python.NET:
            # - https://github.com/pythonnet/pythonnet/issues/2213
            # - https://github.com/pythonnet/pythonnet/issues/2571
            #
            # This and later patches update the method table to replace
            # "protected internal" with "public", so that we could override it
            # in Python.NET.
            #
            # But the problem is that this change should be propagated to all
            # other handler subclasses, as you cannot override a "public"
            # method with "protected".
            #
            # Public AbstractPdfDocumentEventHandler::OnAcceptedEvent.
            Patch(
                name="Public AbstractPdfDocumentEventHandler::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0x00, 0x00, 0x00, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC5, 0x05,
                    # Name
                    0x06, 0xDB, 0x01, 0x00,
                    # Signature
                    0x5C, 0x54, 0x01, 0x00,
                    # ParamList
                    0xEF, 0x0E,
                ]),
                replacement=bytes([
                    # RVA
                    0x00, 0x00, 0x00, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace FamORAssem with Public)
                    0xC6, 0x05,
                    # Everything else remains as-is
                ]),
            ),
            # Public StandaloneMacContainerEmbedder::OnAcceptedEvent.
            Patch(
                name="Public StandaloneMacContainerEmbedder::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0xEC, 0x8D, 0x06, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC5, 0x00,
                    # Name
                    0x06, 0xDB, 0x01, 0x00,
                    # Signature
                    0x5C, 0x54, 0x01, 0x00,
                    # ParamList
                    0x4A, 0x1C,
                ]),
                replacement=bytes([
                    # RVA
                    0xEC, 0x8D, 0x06, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace FamORAssem with Public)
                    0xC6, 0x00,
                    # Everything else remains as-is
                ]),
            ),
            # Public StandaloneMacPdfObjectAdder::OnAcceptedEvent.
            Patch(
                name="Public StandaloneMacPdfObjectAdder::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0x88, 0x8D, 0x06, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC5, 0x00,
                    # Name
                    0x06, 0xDB, 0x01, 0x00,
                    # Signature
                    0x5C, 0x54, 0x01, 0x00,
                    # ParamList
                    0x48, 0x1C,
                ]),
                replacement=bytes([
                    # RVA
                    0x88, 0x8D, 0x06, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace FamORAssem with Public)
                    0xC6, 0x00,
                    # Everything else remains as-is
                ]),
            ),
        ],
    ),
    PatchSet(
        binary_path=ITEXT_SIGN_PATH,
        patches=[
            # Public SignatureMacContainerEmbedder::OnAcceptedEvent.
            Patch(
                name="Public SignatureMacContainerEmbedder::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0xF4, 0xA0, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC4, 0x00,
                    # Name
                    0xB2, 0xA6,
                    # Signature
                    0x09, 0x11,
                    # ParamList
                    0xD4, 0x05,
                ]),
                replacement=bytes([
                    # RVA
                    0xF4, 0xA0, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace Family with Public)
                    0xC6, 0x00,
                    # Everything else remains as-is
                ]),
            ),
            # Public SignatureMacPdfObjectAdder::OnAcceptedEvent.
            Patch(
                name="Public SignatureMacPdfObjectAdder::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0x84, 0xA0, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC4, 0x00,
                    # Name
                    0xB2, 0xA6,
                    # Signature
                    0x09, 0x11,
                    # ParamList
                    0xD2, 0x05,
                ]),
                replacement=bytes([
                    # RVA
                    0x84, 0xA0, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace Family with Public)
                    0xC6, 0x00,
                    # Everything else remains as-is
                ]),
            ),
        ],
    ),
    PatchSet(
        binary_path=ITEXT_HTML2PDF_PATH,
        patches=[
            # Public HtmlBodyStylesApplierHandler::OnAcceptedEvent.
            Patch(
                name="Public HtmlBodyStylesApplierHandler::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0xD8, 0x5D, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC4, 0x00,
                    # Name
                    0x75, 0x9A,
                    # Signature
                    0x00, 0x62,
                    # ParamList
                    0x39, 0x05,
                ]),
                replacement=bytes([
                    # RVA
                    0xD8, 0x5D, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace Family with Public)
                    0xC6, 0x00,
                    # Everything else remains as-is
                ]),
            ),
            # Public PageMarginBoxesDrawingHandler::OnAcceptedEvent.
            Patch(
                name="Public PageMarginBoxesDrawingHandler::OnAcceptedEvent",
                marker=bytes([
                    # RVA
                    0x44, 0xB5, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags
                    0xC4, 0x00,
                    # Name
                    0x75, 0x9A,
                    # Signature
                    0x00, 0x62,
                    # ParamList
                    0x85, 0x07,
                ]),
                replacement=bytes([
                    # RVA
                    0x44, 0xB5, 0x01, 0x00,
                    # ImplFlags
                    0x00, 0x00,
                    # Flags (replace Family with Public)
                    0xC6, 0x00,
                    # Everything else remains as-is
                ]),
            ),
        ]
    )
)


def run():
    for patch_set in PATCH_SETS:
        print(f'Patching {patch_set.binary_path.name}...', file=sys.stderr)
        with open(str(patch_set.binary_path), 'r+b') as dll:
            backup_pending = True
            input_bytes = dll.read()
            for patch in patch_set.patches:
                print(f'--- Patch: "{patch.name}"', file=sys.stderr)
                offset = input_bytes.find(patch.marker)
                if offset == -1:
                    print('------ Marker not found. Skipping...', file=sys.stderr)
                    continue
                print('------ Marker found!', file=sys.stderr)
                if backup_pending:
                    print('------ Making a backup...', file=sys.stderr)
                    shutil.copy2(str(patch_set.binary_path), str(patch_set.binary_path) + '.bak')
                    backup_pending = False
                print('------ Patching...')
                dll.seek(offset)
                dll.write(patch.replacement)
        print(f'{patch_set.binary_path.name} patched!', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(run())
