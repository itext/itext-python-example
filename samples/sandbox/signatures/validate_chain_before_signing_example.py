import itextpy
itextpy.load()

from itextpy.util import disposing

from pathlib import Path

from _utils import PemFileHelper, TestOcspResponseBuilder
from _clients import TestOcspClient

from System import Func
from System.Collections.Generic import List
from System.IO import MemoryStream
from iText.Commons.Bouncycastle.Cert import IX509Certificate
from iText.Commons.Utils import DateTimeUtil
from iText.Forms.Form.Element import SignatureFieldAppearance
from iText.Kernel.Geom import Rectangle
from iText.Kernel.Pdf import PdfReader
from iText.Signatures import IOcspClient, IssuingCertificateRetriever, \
    PdfPadesSigner, SignerProperties
from iText.Signatures.Validation import SignatureValidationProperties, \
    ValidatorChainBuilder
from iText.Signatures.Validation.Context import CertificateSource, \
    TimeBasedContext, ValidationContext, ValidatorContext
from iText.Signatures.Validation.Report import ValidationReport
from Org.BouncyCastle.Pkcs import Pkcs12Store, Pkcs12StoreBuilder

SCRIPT_DIR = Path(__file__).parent.absolute()
RESOURCES_DIR = SCRIPT_DIR / ".." / ".." / "resources"
CERT_CHAIN_PATH = str(RESOURCES_DIR / "cert" / "chain.pem")
ROOT_CERT_PATH = str(RESOURCES_DIR / "cert" / "root.pem")
SIGN_CERT_PATH = str(RESOURCES_DIR / "cert" / "sign.pem")
PASSWORD = "testpassphrase"


def get_ocsp_client(certificate_chain: list[IX509Certificate]) -> IOcspClient:
    builder = TestOcspResponseBuilder(certificate_chain[1], PemFileHelper.read_first_key(ROOT_CERT_PATH, PASSWORD))
    current_date = DateTimeUtil.GetCurrentUtcTime()
    builder.this_update = DateTimeUtil.GetCalendar(current_date)
    builder.next_update = DateTimeUtil.GetCalendar(current_date.AddDays(10))
    return TestOcspClient().add_builder_for_certificate(certificate_chain[0], builder)


def create_signer_properties() -> SignerProperties:
    appearance = (SignatureFieldAppearance(SignerProperties.IGNORED_ID)
                  .SetContent("Approval test signature.\nCreated by iText."))
    return (SignerProperties()
            .SetFieldName("Signature1")
            .SetPageNumber(1)
            .SetPageRect(Rectangle(50, 650, 200, 100))
            .SetSignatureAppearance(appearance)
            .SetReason("Reason")
            .SetLocation("Location"))


def sign_document(src: str, certificate_chain: list[IX509Certificate]) -> None:
    with (disposing(PdfReader(src)) as pdf_reader,
          disposing(MemoryStream()) as out_stream):
        pades_signer = PdfPadesSigner(pdf_reader, out_stream)
        pades_signer.SignWithBaselineBProfile(
            create_signer_properties(),
            certificate_chain,
            PemFileHelper.read_first_key(SIGN_CERT_PATH, PASSWORD)
        )


def manipulate_pdf(src, dest):
    """Basic example of the certificate chain validation before the document signing."""
    certificate_chain = PemFileHelper.read_first_chain(CERT_CHAIN_PATH)
    signing_cert = certificate_chain[0]
    root_cert = certificate_chain[1]

    # Set up the validator.
    properties = SignatureValidationProperties().AddOcspClient(get_ocsp_client(certificate_chain))
    trusted_certs = List[IX509Certificate]()
    trusted_certs.Add(root_cert)
    certificate_retriever = IssuingCertificateRetriever()
    certificate_retriever.SetTrustedCertificates(trusted_certs)
    certificate_retriever_factory = Func[IssuingCertificateRetriever](lambda: certificate_retriever)
    validator_chain_builder = (ValidatorChainBuilder()
                               .WithIssuingCertificateRetrieverFactory(certificate_retriever_factory)
                               .WithSignatureValidationProperties(properties))
    validator = validator_chain_builder.BuildCertificateChainValidator()
    base_context = ValidationContext(
        ValidatorContext.CERTIFICATE_CHAIN_VALIDATOR,
        CertificateSource.SIGNER_CERT,
        TimeBasedContext.PRESENT
    )
    # Validate the chain. ValidationReport will contain all the validation report messages.
    report = validator.ValidateCertificate(base_context, signing_cert, DateTimeUtil.GetCurrentTime())
    if ValidationReport.ValidationResult.VALID == report.GetValidationResult():
        sign_document(src, certificate_chain)

    # Write validation report to the file.
    with open(dest, 'wt') as out:
        out.write(str(report))


if __name__ == "__main__":
    manipulate_pdf(
        str(RESOURCES_DIR / "pdfs" / "hello.pdf"),
        str(SCRIPT_DIR / "validate_chain_before_signing_example.txt"),
    )
