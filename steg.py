from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class ImageSteganography:
    def __init__(self):
        self.delimiter = "$$END$$"

    def _get_key_from_password(self, password):
        """Generate encryption key from password using PBKDF2"""
        salt = b'salt_123'  # In production, use a random salt and store it
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def hide_message(self, image_path, message, password, output_path):
        """Hide an encrypted message in the least significant bits of the image"""
        # Load image and convert to RGB if necessary
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array with uint8 data type
        img_array = np.array(img, dtype=np.uint8)
        
        # Encrypt message
        key = self._get_key_from_password(password)
        f = Fernet(key)
        encrypted_message = f.encrypt((message + self.delimiter).encode())
        binary_message = ''.join(format(b, '08b') for b in encrypted_message)
        
        if len(binary_message) > img_array.size:
            raise ValueError("Message too large for this image")
        
        # Flatten array and modify least significant bits
        flat_array = img_array.flatten()
        
        for i, bit in enumerate(binary_message):
            # Clear the least significant bit and set it to our message bit
            flat_array[i] = (flat_array[i] & 0xFE) | int(bit)
        
        # Reshape and save modified image
        modified_array = flat_array.reshape(img_array.shape)
        modified_image = Image.fromarray(modified_array, mode='RGB')
        modified_image.save(output_path, format='PNG')

    def extract_message(self, image_path, password):
        """Extract and decrypt hidden message from image"""
        # Load image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img, dtype=np.uint8)
        
        # Extract binary message from least significant bits
        flat_array = img_array.flatten()
        binary_message = ''.join(str(pixel & 1) for pixel in flat_array)
        
        # Convert binary to bytes
        byte_message = bytearray()
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            if len(byte) == 8:
                byte_message.append(int(byte, 2))
        
        # Try to decrypt with password
        try:
            key = self._get_key_from_password(password)
            f = Fernet(key)
            decrypted_message = f.decrypt(bytes(byte_message))
            message = decrypted_message.decode()
            
            # Extract message up to delimiter
            if self.delimiter in message:
                return message.split(self.delimiter)[0]
            return message
        except Exception as e:
            return "Incorrect password or no hidden message found"

def main():
    steg = ImageSteganography()
    
    while True:
        print("\nImage Steganography Tool")
        print("1. Hide message in image")
        print("2. Extract message from image")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            input_image = input("Enter input image path: ").strip().replace('"', '')
            output_image = input("Enter output image path: ").strip().replace('"', '')
            message = input("Enter message to hide: ")
            password = input("Enter password: ")
            
            try:
                steg.hide_message(input_image, message, password, output_image)
                print("Message hidden successfully!")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '2':
            image_path = input("Enter image path: ").strip().replace('"', '')
            password = input("Enter password: ")
            
            try:
                message = steg.extract_message(image_path, password)
                print(f"Extracted message: {message}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '3':
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()