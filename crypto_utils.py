import base64
from cryptography.fernet import Fernet, InvalidToken

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
    encrypted_message = cipher_suite.encrypt(message.encode())
    return base64.urlsafe_b64encode(encrypted_message).decode()

def decrypt_message(encrypted_message, key):
    if not is_valid_fernet_key(key):
        raise ValueError("Invalid Fernet key format. Key must be 44 url-safe base64 characters.")
    cipher_suite = Fernet(key.encode())
    decrypted_message = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_message)).decode()
    return decrypted_message
