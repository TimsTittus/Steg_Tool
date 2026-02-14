from stegano import lsb
import binascii
from cryptography.fernet import InvalidToken
from crypto_utils import encrypt_message, decrypt_message

def hide_message(image, message, key):
    # If key is derived from PBKDF2, salt must be included in payload
    # Convention: encrypted_message = salt_hex:actual_encrypted_message
    if hasattr(key, 'pbkdf2_salt_hex'):
        salt_hex = key.pbkdf2_salt_hex
        encrypted_message = f"{salt_hex}:{encrypt_message(message, key)}"
    else:
        encrypted_message = encrypt_message(message, key)
    secret_image = lsb.hide(image, encrypted_message)
    return secret_image

def reveal_message(image, key):
    encrypted_message = lsb.reveal(image)
    if encrypted_message:
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
    return "No hidden message found."
