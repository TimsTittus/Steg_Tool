import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def derive_fernet_key_from_password(password: str, salt: bytes, iterations: int = 390000) -> str:
    """
    Derive a Fernet-compatible key from a password and salt using PBKDF2.
    Returns a base64-urlsafe-encoded 32-byte key (44 chars).
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key).decode()

def generate_salt(length: int = 16) -> bytes:
    return os.urandom(length)
