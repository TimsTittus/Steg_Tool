from stegano import lsb
import binascii
from cryptography.fernet import InvalidToken
from crypto_utils import encrypt_message, decrypt_message

def hide_message(image, message, key):
    # Add TIMSTEG header and version
    HEADER = "TIMSTEG:"
    if hasattr(key, 'pbkdf2_salt_hex'):
        salt_hex = key.pbkdf2_salt_hex
        payload = f"{HEADER}{salt_hex}:{encrypt_message(message, key)}"
    else:
        payload = f"{HEADER}{encrypt_message(message, key)}"
    secret_image = lsb.hide(image, payload)
    return secret_image

def reveal_message(image, key):
    payload = lsb.reveal(image)
    HEADER = "TIMSTEG:"
    if payload and payload.startswith(HEADER):
        encrypted_message = payload[len(HEADER):]
        # Check for salt in payload
        if ':' in encrypted_message:
            salt_hex, actual_encrypted = encrypted_message.split(':', 1)
            if hasattr(key, 'pbkdf2_salt_hex'):
                key.pbkdf2_salt_hex = salt_hex
            encrypted_message = actual_encrypted
        try:
            return decrypt_message(encrypted_message, key)
        except InvalidToken:
            return "Decryption failed! Invalid or incorrect key."
        except (ValueError, binascii.Error):
            return "Decryption failed! Corrupted or invalid encrypted data."
    elif payload:
        return "Invalid or unsupported stego payload (missing TIMSTEG header)."
    return "No hidden message found."
