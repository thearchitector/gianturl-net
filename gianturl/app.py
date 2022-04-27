from urllib.parse import urlparse, urlunparse

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .encoding import decode, encode
from .errors import INFINITE_LOOP, URL_TOO_LARGE

app = FastAPI(
    title="GiantURL API",
    description=(
        "GiantURL enlarges your pesky small URLs by three or four, securely"
        ", uniquely, and forever."
    ),
    version="0.0.1",
    contact={
        "name": "Elias Gabriel",
        "url": "https://www.eliasfgabriel.com",
        "email": "me@eliasfgabriel.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url=None,
    redoc_url="/docs",
)


@app.get("/api")
async def enlarge(request: Request, url: str):
    """
    Validates and enlarges the given url through rounded dual-step symmetric Fernet
    encryption. URLs cannot be self-referencing. Encoding may fail if the original URL
    is already too long.
    """
    # infinite loops cause problems, for them not for us
    if url.startswith(f"{request.url.scheme}://{request.url.netloc}"):
        raise INFINITE_LOOP

    # encode the candidate with repeated fernet encryption
    candidate = encode(url)

    # if the number of rounds didn't change (original URL was too large), throw
    # a HTTP 422 error with a nice informative message
    if not candidate:
        raise URL_TOO_LARGE

    new_url = f"{request.url.scheme}://{request.url.netloc}/{candidate}"
    return ORJSONResponse(
        {
            "original": url,
            "enlarged": new_url,
            "improvement": "{0:.6g}%".format((len(new_url) / len(url)) * 100),
        }
    )


@app.get("/{token}")
async def redirect(token: str):
    """
    Accept a URL encoding, parse it, and permanently redirect the request
    if the decoding was successful.
    """
    try:
        # decode and construct a valid url, adding the scheme if non exists
        redirection = urlunparse(urlparse(decode(token), scheme="http"))

        # redirect for good, which is probably bad
        return RedirectResponse(
            redirection, status_code=status.HTTP_301_MOVED_PERMANENTLY
        )
    except Exception:
        # TODO: should return nice 400 page
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


app.mount("/", StaticFiles(directory="ui/public", html=True), name="home")
