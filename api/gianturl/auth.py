from typing import Optional, Tuple

from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from ratelimit.auths import EmptyInformation, Scope
from starlette_csrf import CSRFMiddleware


class ORJSONCSRFMiddleware(CSRFMiddleware):
    def _get_error_response(self, request: Request) -> ORJSONResponse:
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
