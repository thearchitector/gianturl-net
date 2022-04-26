from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse

from .crypto import decode, encode

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

    # encode the candidate with repeated fernet encryption
    candidate = encode(url)

    # if the number of rounds didn't change (original URL was too large), throw
    # a HTTP 422 error with a nice informative message
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enlarging the provided URL would exceed the maximum URL length for"
            " browser compatability. Sorry!",
        )

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
    try:
        redirection = decode(token)

        # redirect for good, which is probably bad
        return RedirectResponse(
            redirection, status_code=status.HTTP_301_MOVED_PERMANENTLY
        )
    except Exception as e:
        # TODO: should return nice 400 page
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
