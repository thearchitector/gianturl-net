import base64
from typing import Optional

from cryptography.fernet import Fernet, MultiFernet

from .config import settings

APPROX_FERNET_OVERHEAD = 2
fernet = MultiFernet([Fernet(k) for k in settings.fernet_keys])


def encode(url: str) -> Optional[str]:
    """
    Encrypts the given url repeatedly using url-safe base64 until the candidate
    is sufficiently long, then returns a final token containing the candidate and
    the number of inner encoding rounds encrypted with symmetric Fernet.
    """
    urlb = c = url.encode()
    rounds = 0

    # while the current length is less than the maximum URL length, padding for
    # the size increase from the final fernet encryption
    while len(c) * APPROX_FERNET_OVERHEAD <= settings.max_candidate_length:
        urlb = c
        rounds += 1
        c = base64.urlsafe_b64encode(urlb)

    return (
        None
        if rounds == 0
        else fernet.encrypt(f"{rounds - 1}|".encode() + urlb).decode()
    )


def decode(token: str) -> str:
    """
    Attempts to decode, parse, and fully decrypt the given URL token.
    """
    r, t = fernet.decrypt(token.encode()).decode().split("|")
    rounds, tokenb = int(r), t.encode()

    for _ in range(rounds):
        tokenb = base64.urlsafe_b64decode(tokenb)

    return tokenb.decode()
