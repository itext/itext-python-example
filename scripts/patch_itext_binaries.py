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


ROOT_DIR = Path(__file__).parent.parent.absolute()
# Path to the .NET binaries we want to patch
ITEXT_BINARIES_DIR = ROOT_DIR / 'itextpy' / 'binaries'
# Path to the iText.IO binary
ITEXT_IO_PATH = ITEXT_BINARIES_DIR / 'itext.io.dll'

PATCH_SETS = (
    PatchSet(
        binary_path=ITEXT_IO_PATH,
        patches=[
            # This patch is here to fix an exception, which happens, when you
            # are running iText in Python under .NET Core.
            #
            # What the patch does is that it modifies this check:
            # https://github.com/itext/itext-dotnet/blob/74700467506d83c6c5c9031cdb31181072f79ba0/itext/itext.io/itext/io/util/ResourceUtil.cs#L227
            #
            # It replaces this line:
            #     if (FileUtil.GetBaseDirectory() != null) {
            # With this:
            #     return; {
            #
            # With this change it unconditionally skips the last if block.
            # Since we don't bundle the font libraries, it shouldn't have any
            # negative effects. Binary is, also, not signed, so we can safely
            # do this.
            #
            # This should not be required in 9.2.0, as a fix for it has already
            # been merged:
            # https://github.com/itext/itext-dotnet/commit/cbe1e782aa40e1fb5267095c225d2c964d09cdd0
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
