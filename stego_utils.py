from stegano import lsb
import binascii
from cryptography.fernet import InvalidToken
from crypto_utils import encrypt_message, decrypt_message

def hide_message(image, message, key):
    encrypted_message = encrypt_message(message, key)
    secret_image = lsb.hide(image, encrypted_message)
    return secret_image

def reveal_message(image, key):
    encrypted_message = lsb.reveal(image)
    if encrypted_message:
        try:
            return decrypt_message(encrypted_message, key)
        except InvalidToken:
            return "Decryption failed! Invalid or incorrect key."
        except (ValueError, binascii.Error):
            return "Decryption failed! Corrupted or invalid encrypted data."
    return "No hidden message found."
