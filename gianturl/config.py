from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    fernet_keys: List[bytes] = [b"LNx6pCeolI_NNVc9u7kLOoySoRNHXK-WUXPn43CjSl0="]
    max_candidate_length: int = 1000


settings = Settings()
