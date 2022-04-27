from fastapi import HTTPException, status

INFINITE_LOOP = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Within this URL I see a possibility for infinite loops, where there"
    " be dragons.",
)

URL_TOO_LARGE = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Enlarging the provided URL would exceed the maximum URL length for"
    " browser compatability. Sorry!",
)
