#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
# Path to the .NET binary we want to patch
ITEXT_IO_PATH = SCRIPT_DIR / 'itextpy' / 'binaries' / 'itext.io.dll'

#
# This is a simple script, which patches the itext.io.dll 9.1.0 binary to work
# with coreclr under Python.NET.
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

marker = bytes([
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
])
patch = bytes([
    # IL_002e: ret nop nop nop nop
    #          ^ return from function (i.e. skip the if block entirely)
    0x2A, 0x00, 0x00, 0x00, 0x00,
    # IL_002f: nop nop nop nop nop
    0x00, 0x00, 0x00, 0x00, 0x00,
    # Everything else remains as-is
])


def run():
    print('Patching itext.io.dll...', file=sys.stderr)
    with open(str(ITEXT_IO_PATH), 'r+b') as dll:
        input_bytes = dll.read()
        offset = input_bytes.find(marker)
        if offset == -1:
            print('--- Marker not found. Nothing to patch.', file=sys.stderr)
            return 0
        print('--- Marker found. Making a backup...', file=sys.stderr)
        shutil.copy2(str(ITEXT_IO_PATH), str(ITEXT_IO_PATH) + '.bak')
        dll.seek(offset)
        dll.write(patch)
    print('itext.io.dll patched!', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(run())
