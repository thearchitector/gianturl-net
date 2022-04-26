import base64

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "Hello World"}


@app.get("/api")
async def enlarge(request: Request, url: str):
    # infinite loops cause problems, for them not for us
    if url.startswith(f"{request.url.scheme}://{request.url.netloc}"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="There's a possibility for infinite loops, where there be dragons",
        )

    urlb = url.encode()
    candidate = url
    rounds = 0

    # while the current length is less than the maximum URL length with padding
    while len(candidate) <= 1000:
        rounds += 1
        urlb = base64.urlsafe_b64encode(urlb)
        candidate = (
            f"{request.url.scheme}://{request.url.netloc}/{urlb.decode()}?r={rounds}"
        )

    # if the number of rounds didn't change (original URL was too large), throw
    # a HTTP 422 error with a nice informative message
    if rounds == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enlarging the provided URL would exceed the maximum URL length for"
            " browser compatability. Sorry!",
        )

    return ORJSONResponse(
        {
            "original": url,
            "enlarged": candidate,
            "improvement": "{0:.6g}%".format((len(candidate) / len(url)) * 100),
        }
    )


@app.get("/{encoded_url}")
async def redirect(
    encoded_url: str,
    r: int = 0,
):
    try:
        assert r >= 1
        encoded = encoded_url.encode()

        # decode round-by-round
        for _ in range(r):
            encoded = base64.urlsafe_b64decode(encoded)

        # redirect for good, which is probably bad
        to_redirect = encoded.decode()
        return RedirectResponse(
            to_redirect, status_code=status.HTTP_301_MOVED_PERMANENTLY
        )
    except Exception:
        # TODO: should return nice 400 page
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
