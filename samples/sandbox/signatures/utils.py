import itextpy
itextpy.load()

from System import DateTime, DateTimeKind
from System.Collections.Generic import Dictionary
from System.IO import File
from iText.Commons.Bouncycastle.Asn1 import IDerObjectIdentifier
from iText.Commons.Bouncycastle.Asn1.Ocsp import IBasicOcspResponse
from iText.Commons.Bouncycastle.Asn1.X509 import IX509Extension
from iText.Commons.Bouncycastle.Cert.Ocsp import ICertStatus, IReq
from iText.Bouncycastleconnector import BouncyCastleFactoryCreator
from iText.Commons.Bouncycastle.Cert import IX509Certificate
from iText.Commons.Bouncycastle.Crypto import IPrivateKey
from itextpy.util import clr_isinstance, clr_try_cast, disposing

_FACTORY = BouncyCastleFactoryCreator.GetFactory()


class PemFileHelper:
    @staticmethod
    def read_first_chain(pem_file_path: str) -> list[IX509Certificate]:
        with disposing(File.OpenText(pem_file_path)) as file:
            parser = _FACTORY.CreatePEMParser(file, None)
            obj = parser.ReadObject()
            certificates = []
            while obj is not None:
                cert = clr_try_cast(obj, IX509Certificate)
                if cert is not None:
                    certificates.append(obj)
                obj = parser.ReadObject()
            return certificates

    @staticmethod
    def read_first_key(pem_file_path: str, key_pass: str) -> IPrivateKey:
        with disposing(File.OpenText(pem_file_path)) as file:
            parser = _FACTORY.CreatePEMParser(file, key_pass)
            obj = parser.ReadObject()
            while (obj is not None) and (not clr_isinstance(obj, IPrivateKey)):
                obj = parser.ReadObject()
            return clr_try_cast(obj, IPrivateKey)

    @staticmethod
    def init_store(pem_file_path: str) -> list[IX509Certificate]:
        return PemFileHelper.read_first_chain(pem_file_path)[:1]


class TestOcspResponseBuilder:
    SIGN_ALG = "SHA256withRSA"
    TEST_DATE_TIME = DateTime(2000, 2, 14, 14, 14, 2, DateTimeKind.Utc)

    def __init__(self,
                 issuer_cert: IX509Certificate,
                 issuer_private_key: IPrivateKey,
                 certificate_status: ICertStatus = None):
        self.issuer_cert = issuer_cert
        self.issuer_private_key = issuer_private_key
        self.certificate_status = certificate_status
        if self.certificate_status is None:
            self.certificate_status = _FACTORY.CreateCertificateStatus().GetGood()
        self.response_builder = _FACTORY.CreateBasicOCSPRespBuilder(
            _FACTORY.CreateRespID(
                self.issuer_cert.GetSubjectDN()
            )
        )
        self.this_update = self.TEST_DATE_TIME.AddDays(-1)
        self.next_update = self.TEST_DATE_TIME.AddDays(30)

    def make_ocsp_response(self, request_bytes: bytes) -> bytes:
        return self.make_ocsp_response_object(request_bytes).GetEncoded()

    def make_ocsp_response_object(self, request_bytes: bytes) -> IBasicOcspResponse:
        ocsp_request = _FACTORY.CreateOCSPReq(request_bytes)
        request_list: list[IReq] = list(ocsp_request.GetRequestList())

        ext_nonce = ocsp_request.GetExtension(_FACTORY.CreateOCSPObjectIdentifiers().GetIdPkixOcspNonce())
        if not _FACTORY.IsNullExtension(ext_nonce):
            # TODO ensure
            extensions_dict = Dictionary[IDerObjectIdentifier, IX509Extension]()
            extensions_dict.Add(_FACTORY.CreateOCSPObjectIdentifiers().GetIdPkixOcspNonce(), ext_nonce)
            response_extensions = _FACTORY.CreateExtensions(extensions_dict)
            self.response_builder.SetResponseExtensions(response_extensions)

        for req in request_list:
            self.response_builder.AddResponse(
                req.GetCertID(),
                self.certificate_status,
                self.this_update.ToUniversalTime(),
                self.next_update.ToUniversalTime(),
                _FACTORY.CreateExtensions()
            )

        signer = _FACTORY.CreateContentSigner(self.SIGN_ALG, self.issuer_private_key)
        return self.response_builder.Build(signer, [self.issuer_cert], self.TEST_DATE_TIME)
