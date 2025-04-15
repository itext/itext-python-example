import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from System.Collections.Generic import List
from System.IO import FileAccess, FileMode, FileStream
from iText.Bouncycastle.Crypto import PrivateKeyBC
from iText.Bouncycastle.X509 import X509CertificateBC
from iText.Commons.Bouncycastle.Cert import IX509Certificate
from iText.Forms.Form.Element import SignatureFieldAppearance
from iText.IO.Image import ImageDataFactory
from iText.Kernel.Crypto import DigestAlgorithms
from iText.Kernel.Geom import Rectangle
from iText.Kernel.Pdf import PdfReader, StampingProperties
from iText.Signatures import AccessPermissions, CrlClientOnline, \
    ICrlClient, OcspClientBouncyCastle, PdfSigner, PrivateKeySignature, \
    SignerProperties
from Org.BouncyCastle.Pkcs import Pkcs12Store, Pkcs12StoreBuilder

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
SRC_PATH = str(RESOURCES_DIR / "pdfs" / "signExample.pdf")
CRT_PATH = str(RESOURCES_DIR / "cert" / "signCertRsa01.p12")
IMG_PATH = str(RESOURCES_DIR / "img" / "sign.jpg")


def get_private_key_signature(pk12: Pkcs12Store) -> PrivateKeySignature:
    """ Method reads pkcs12 file's first private key and returns a
    PrivateKeySignature instance, which uses SHA-512 hash algorithm."""
    alias = next((a for a in pk12.Aliases if pk12.IsKeyEntry(a)), None)
    pk = PrivateKeyBC(pk12.GetKey(alias).Key)
    return PrivateKeySignature(pk, DigestAlgorithms.SHA512)


def get_certificate_chain(pk12: Pkcs12Store) -> list[IX509Certificate]:
    """Method reads first public certificate chain."""
    alias = next((a for a in pk12.Aliases if pk12.IsKeyEntry(a)), None)
    chain = list(X509CertificateBC(e.Certificate) for e in pk12.GetCertificateChain(alias))
    return chain


def manipulate_pdf(dest):
    with (disposing(PdfReader(SRC_PATH)) as pdf_reader,
          disposing(FileStream(dest, FileMode.Create)) as out_stream):
        pdf_signer = PdfSigner(pdf_reader, out_stream, StampingProperties())
        signer_properties = SignerProperties()
        signer_properties.SetCertificationLevel(AccessPermissions.NO_CHANGES_PERMITTED)

        # Set the name indicating the field to be signed.
        # The field can already be present in the document but shall not be signed
        signer_properties.SetFieldName("signature")

        pdf_signer.SetSignerProperties(signer_properties)

        client_signature_image = ImageDataFactory.Create(IMG_PATH)

        # If you create new signature field (or use SetFieldName(System.String)
        # with the name that doesn't exist in the document or don't specify i
        # at all) then the signature is invisible by default.
        appearance = (SignatureFieldAppearance(SignerProperties.IGNORED_ID)
                      .SetContent(client_signature_image))
        (signer_properties
         .SetPageNumber(1)
         .SetPageRect(Rectangle(25, 25, 25, 25))
         .SetSignatureAppearance(appearance))

        pk12 = Pkcs12StoreBuilder().Build()
        with disposing(FileStream(CRT_PATH, FileMode.Open, FileAccess.Read)) as cert_stream:
            pk12.Load(cert_stream, "testpass")

        pks = get_private_key_signature(pk12)
        chain = get_certificate_chain(pk12)
        ocsp_client = OcspClientBouncyCastle()
        crl_clients = List[ICrlClient]()
        crl_clients.Add(CrlClientOnline())

        # Sign the document using the detached mode, CMS or CAdES equivalent.
        # This method closes the underlying pdf document, so the instance of
        # PdfSigner cannot be used after this method call
        pdf_signer.SignDetached(pks, chain, crl_clients, ocsp_client, None, 0, PdfSigner.CryptoStandard.CMS)


if __name__ == "__main__":
    manipulate_pdf("signature_example.pdf")
