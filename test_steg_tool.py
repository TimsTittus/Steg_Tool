import unittest
from PIL import Image
import io
from crypto_utils import generate_key, encrypt_message, decrypt_message, is_valid_fernet_key
from stego_utils import hide_message, reveal_message

class TestCryptoUtils(unittest.TestCase):
    def setUp(self):
        self.key = generate_key()
        self.message = "Secret123!"

    def test_key_validity(self):
        self.assertTrue(is_valid_fernet_key(self.key))
        self.assertFalse(is_valid_fernet_key("invalidkey"))

    def test_encrypt_decrypt(self):
        encrypted = encrypt_message(self.message, self.key)
        decrypted = decrypt_message(encrypted, self.key)
        self.assertEqual(decrypted, self.message)

    def test_decrypt_invalid_key(self):
        encrypted = encrypt_message(self.message, self.key)
        with self.assertRaises(Exception):
            decrypt_message(encrypted, generate_key())

class TestStegoUtils(unittest.TestCase):
    def setUp(self):
        self.key = generate_key()
        self.message = "StegoTest!"
        self.image = Image.new("RGB", (100, 100), color="white")

    def test_hide_and_reveal(self):
        secret_img = hide_message(self.image, self.message, self.key)
        buf = io.BytesIO()
        secret_img.save(buf, format="PNG")
        buf.seek(0)
        loaded_img = Image.open(buf)
        revealed = reveal_message(loaded_img, self.key)
        self.assertEqual(revealed, self.message)

    def test_reveal_with_wrong_key(self):
        secret_img = hide_message(self.image, self.message, self.key)
        buf = io.BytesIO()
        secret_img.save(buf, format="PNG")
        buf.seek(0)
        loaded_img = Image.open(buf)
        wrong_key = generate_key()
        revealed = reveal_message(loaded_img, wrong_key)
        self.assertIn("Decryption failed", revealed)

if __name__ == "__main__":
    unittest.main()
