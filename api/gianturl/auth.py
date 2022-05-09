from typing import List, Optional, Tuple

from cryptography.fernet import Fernet, MultiFernet
from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from ratelimit.auths import EmptyInformation, Scope
from starlette_csrf import CSRFMiddleware


class SecureCSRFMiddleware(CSRFMiddleware):
    def __init__(self, cookie_secrets: List[str], **kwargs):
        self.mfernet = MultiFernet(Fernet(s) for s in cookie_secrets)
        super().__init__(**kwargs)

    async def _get_submitted_csrf_token(self, request: Request) -> Optional[str]:
        """
        We're using encrypted cookies, so the contents of the header coming from the
        client will also be encrypted. The incoming cookie is decrypted automatically
        but the header is not, so we need to decrypt it manually so the CSRF middleware
        can compare them correctly.
        """
        return self.mfernet.decrypt(
            request.headers.get(self.header_name).encode()
        ).decode()

    def _get_error_response(self, request: Request) -> ORJSONResponse:
        """Serialize and return an orjson response, for speeeed."""
        return ORJSONResponse(
            {"detail": "Invalid CSRF token. Don't do that."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


async def rate_identifier(scope: Scope) -> Tuple[str, str]:
    """
    Attempts to parse IP address of the incoming client request, parsing the 'Forwarded'
    header if present.
    """
    client_addr: Optional[Tuple[str, int]] = scope.get("client")
    client_host = client_addr[0] if client_addr else None

    headers = dict(scope["headers"])
    if b"forwarded" in headers:
        client_host = headers[b"forwarded"].decode("latin1").strip()

    if not client_host:
        raise EmptyInformation(scope)

    return client_host, "default"
