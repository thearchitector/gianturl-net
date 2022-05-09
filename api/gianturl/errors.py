from fastapi import HTTPException, status

BAD_URL = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="This URL doesn't look quite right. Did you type it correctly?",
)

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
