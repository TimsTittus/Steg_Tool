import base64
from cryptography.fernet import Fernet, InvalidToken
import zlib

def generate_key():
    return Fernet.generate_key().decode()

def is_valid_fernet_key(key):
    if not isinstance(key, str):
        return False
    try:
        decoded = base64.urlsafe_b64decode(key.encode())
        return len(decoded) == 32
    except Exception:
        return False

def encrypt_message(message, key):
    if not is_valid_fernet_key(key):
        raise ValueError("Invalid Fernet key format. Key must be 44 url-safe base64 characters.")
    cipher_suite = Fernet(key.encode())
    compressed = zlib.compress(message.encode())
    use_compression = len(compressed) < len(message.encode())
    if use_compression:
        data = b'C' + compressed  # 'C' = Compressed
    else:
        data = b'U' + message.encode()  # 'U' = Uncompressed
    encrypted_message = cipher_suite.encrypt(data)
    return base64.urlsafe_b64encode(encrypted_message).decode()

def decrypt_message(encrypted_message, key):
    if not is_valid_fernet_key(key):
        raise ValueError("Invalid Fernet key format. Key must be 44 url-safe base64 characters.")
    cipher_suite = Fernet(key.encode())
    data = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_message))
    if data[:1] == b'C':
        try:
            return zlib.decompress(data[1:]).decode()
        except Exception:
            return "[Decompression failed]"
    elif data[:1] == b'U':
        return data[1:].decode()
    else:
        return data.decode(errors='replace')
