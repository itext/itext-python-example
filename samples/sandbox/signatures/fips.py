#
# !!! THIS EXAMPLE WILL NOT WORK OUT OF THE BOX !!!
#
# By default, we use the regular `bouncy-castle-adapter`, which is specified
# in the itext.python.compat .NET project files. To run this script you need
# to change that dependency to `bouncy-castle-fips-adapter` instead and build
# a new wheel.
#
# Also, `bouncy-castle-fips-adapter` does not support .NET Framework, so .NET
# Core usage is explicit here.
#
# This code is based on the Java/C# example, which you can find here:
#   https://kb.itextpdf.com/itext/fips-sha3-examples-for-itext-core-8-0-0
#
import pythonnet
pythonnet.load("coreclr")

import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path
import sys

from utils import PemFileHelper

from System.IO import FileMode, FileStream
from iText.Kernel.Crypto import DigestAlgorithms
from iText.Kernel.Pdf import PdfReader, StampingProperties
from iText.Signatures import PdfSigner, PrivateKeySignature
from Org.BouncyCastle.Crypto import CryptoServicesRegistrar


SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC_PATH = str(RESOURCES_DIR / "pdfs" / "signExample.pdf")
SIGN_CERT_PATH = str(RESOURCES_DIR / "cert" / "sign.pem")
PASSWORD = "testpassphrase"


def manipulate_pdf(dest):
    try:
        CryptoServicesRegistrar.SetApprovedOnlyMode(True)
    except AttributeError:
        print('signatures/fips.py sample requires '
              'itext.bouncy-castle-fips-adapter, '
              'skipping...', file=sys.stderr)
        return
    chain = PemFileHelper.read_first_chain(SIGN_CERT_PATH)
    private_key = PemFileHelper.read_first_key(SIGN_CERT_PATH, PASSWORD)
    pk = PrivateKeySignature(private_key, DigestAlgorithms.SHA3_512)
    with (disposing(PdfReader(SRC_PATH)) as pdf_reader,
          disposing(FileStream(dest, FileMode.Create)) as out_stream):
        pdf_signer = PdfSigner(pdf_reader, out_stream, StampingProperties().UseAppendMode())
        pdf_signer.SignDetached(pk, chain, None, None, None, 0, PdfSigner.CryptoStandard.CMS)


if __name__ == "__main__":
    manipulate_pdf("fips.pdf")
