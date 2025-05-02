import itextpy
itextpy.load()

from typing import Self

from utils import TestOcspResponseBuilder

from System.Collections.Generic import Dictionary
from iText.Bouncycastleconnector import BouncyCastleFactoryCreator
from iText.Commons.Bouncycastle.Asn1 import IDerObjectIdentifier
from iText.Commons.Bouncycastle.Asn1.X509 import IX509Extension
from iText.Commons.Bouncycastle.Cert import IX509Certificate
from iText.Commons.Bouncycastle.Cert.Ocsp import ICertID, IOcspRequest
from iText.Commons.Bouncycastle.Crypto import IPrivateKey
from iText.Kernel.Pdf import PdfEncryption
from iText.Signatures import IOcspClient


class TestOcspClient(IOcspClient):
    # This is the namespace for this object in .NET
    # Without this, it won't work with Python.NET
    __namespace__ = "Sandbox.Signatures"

    _FACTORY = BouncyCastleFactoryCreator.GetFactory()

    def __init__(self):
        self.cert_dn_to_response_builder = {}

    def GetEncoded(self, check_cert: IX509Certificate, issuer_cert: IX509Certificate, url: str) -> bytes | None:
        cert_id = self._FACTORY.CreateCertificateID(
            self._FACTORY.CreateCertificateID().GetHashSha1(),
            issuer_cert,
            check_cert.GetSerialNumber()
        )
        check_dn = str(check_cert.GetSubjectDN())
        try:
            builder = self.cert_dn_to_response_builder[check_dn]
        except KeyError:
            return None
        return builder.make_ocsp_response(self._generate_ocsp_request_with_nonce(cert_id).GetEncoded())

    def init_builder_for_certificate(self, cert: IX509Certificate, private_key: IPrivateKey) -> Self:
        return self.add_builder_for_certificate(cert, TestOcspResponseBuilder(cert, private_key))

    def add_builder_for_certificate(self, cert: IX509Certificate, builder: TestOcspResponseBuilder) -> Self:
        dn = str(cert.GetSubjectDN())
        self.cert_dn_to_response_builder[dn] = builder
        return self

    def _generate_ocsp_request_with_nonce(self, id: ICertID) -> IOcspRequest:
        gen = self._FACTORY.CreateOCSPReqBuilder()
        gen.AddRequest(id)

        # create details for nonce extension
        extensions_dict = Dictionary[IDerObjectIdentifier, IX509Extension]()

        extensions_dict.Add(
            self._FACTORY.CreateOCSPObjectIdentifiers().GetIdPkixOcspNonce(),
            self._FACTORY.CreateExtension(
                False,
                self._FACTORY.CreateDEROctetString(
                    PdfEncryption.GenerateNewDocumentId()
                )
            ),
        )

        gen.SetRequestExtensions(self._FACTORY.CreateExtensions(extensions_dict))
        return gen.Build()
