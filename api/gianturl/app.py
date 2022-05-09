from urllib.parse import urlparse

import validators
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.slidingredis import SlidingRedisBackend
from securecookies import SecureCookiesMiddleware

from .auth import SecureCSRFMiddleware, rate_identifier
from .config import settings
from .encoding import decode, encode
from .errors import BAD_URL, INFINITE_LOOP, URL_TOO_LARGE
from .models import EnlargeResponse

app = FastAPI(
    title="GiantURL API",
    description="GiantURL enlarges your pesky small URLs by three or four, securely,"
    " uniquely, and forever.\n\nThis API is rate-limited to 25 request per hour.",
    version="1.1.0",
    contact={
        "name": "Elias Gabriel",
        "url": "https://www.eliasfgabriel.com",
        "email": "me@eliasfgabriel.com",
    },
    license_info={
        "name": "BSD-3-Clause",
        "url": "https://opensource.org/licenses/BSD-3-Clause",
    },
    docs_url=None,
    redoc_url="/docs",
)

# rate limiting and csrf protection middlewares
if settings.env == "production":
    app.add_middleware(
        RateLimitMiddleware,
        authenticate=rate_identifier,
        backend=SlidingRedisBackend(settings.redis_host),
        config={
            r"^/api": [Rule(hour=25)],
        },
    )
    app.add_middleware(
        SecureCSRFMiddleware,
        secret=settings.csrf_secret,
        cookie_secrets=[settings.cookie_secret],
        cookie_name="__Host-csrftoken",
        cookie_secure=True,
        cookie_samesite="strict",
    )
    app.add_middleware(SecureCookiesMiddleware, secrets=[settings.cookie_secret])


@app.post(
    "/api",
    response_model=EnlargeResponse,
    responses={
        422: {
            "description": "Missing URL parameter.",
        }
    },
)
async def enlarge(
    request: Request,
    url: str = Query(
        ...,
        description="The short URL to encode. This URL is never internally visited"
        ", and thus is not checked and may not resolve.",
    ),
):
    """
    Validates and enlarges the given url through rounded encoding and dual-step
    symmetric Fernet encryption. URLs cannot be self-referencing. Encoding may fail
    if the original URL is already too long.

    This endpoint pretty dumb. It will not check if the URLs point to a resource that
    resolves, and only checks if the URL is of the fairly standard form
    "[scheme://]netloc[/path;parameters?query#fragment]", where all but "netloc" is
    optional.

    If "scheme://" is omitted, "http://" is automatically prepended. This behavior is
    technically incorrect as per RFC 1808, but more inline with common use.
    """
    urlparts = urlparse(url.strip())
    if urlparts.scheme == request.url.scheme and urlparts.netloc == request.url.netloc:
        # infinite loops cause problems, for them not for us
        raise INFINITE_LOOP
    elif not urlparts.scheme:
        # append http scheme if doesn't exist. note that this not technically correct
        # as per RFC 1808 (which requires a preceding "//"), but more inline with
        # common use
        #
        # https://datatracker.ietf.org/doc/html/rfc1808.html
        url = f"http://{url}"

    if not validators.url(url):
        # if the url isn't valid
        raise BAD_URL

    # encode the candidate with repeated fernet encryption
    candidate = encode(url)

    # if the number of rounds didn't change (original URL was too large), throw
    # a HTTP 422 error with a nice informative message
    if not candidate:
        raise URL_TOO_LARGE

    new_url = f"{request.url.scheme}://{request.url.netloc}/r/{candidate}"
    return EnlargeResponse(
        original=url,
        enlarged=new_url,
        improvement=(len(new_url) / len(url)) * 100,
    )


@app.get(
    "/r/{token}",
    response_class=RedirectResponse,
    status_code=status.HTTP_301_MOVED_PERMANENTLY,
    responses={
        301: {
            "description": "Valid URL token redirect.",
        },
        400: {
            "description": "Invalid encoded URL token.",
        },
        422: {
            "description": "Missing token parameter.",
        },
    },
)
async def redirect(
    request: Request,
    token: str = Query(
        ...,
        description="The encoded URL token to which to redirect.",
    ),
):
    """
    Accept a URL encoding, parse it, and permanently redirect the request
    if the decoding was successful.
    """
    try:
        # decode and construct a valid url, adding the scheme if non exists
        redirection = decode(token)

        # redirect for good, which is probably bad
        return redirection
    except Exception:
        # TODO: should return nice 400 page
        raise HTTPException(
            detail=f"'{token}' is not a valid URL token."
            f" Return to {request.url.scheme}://{request.url.netloc}.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


app.mount("/", StaticFiles(directory="ui", html=True), name="home")
