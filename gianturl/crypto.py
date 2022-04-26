from typing import Optional

from cryptography.fernet import Fernet, MultiFernet

from .config import settings

fernet = MultiFernet([Fernet(k) for k in settings.fernet_keys])


def encode(url: str) -> Optional[str]:
    """
    Encrypts the given url repeatedly using symmetric Fernet until the candidate
    is sufficiently long, then returns a final token containing the candidate and
    the number of inner encryption rounds.
    """
    urlb = url.encode()
    rounds = 0

    # while the current length is less than the maximum URL length
    while len(urlb) <= settings.max_candidate_length:
        rounds += 1
        urlb = fernet.encrypt(urlb)

    return (
        None if rounds == 0 else fernet.encrypt(f"{rounds}|".encode() + urlb).decode()
    )


def decode(token: str) -> str:
    """
    Attempts to decode, parse, and fully decrypt the given URL token.
    """
    r, t = fernet.decrypt(token.encode()).decode().split("|")
    rounds, tokenb = int(r), t.encode()

    for _ in range(rounds):
        tokenb = fernet.decrypt(tokenb)

    return tokenb.decode()
