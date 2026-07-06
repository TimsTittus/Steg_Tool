# StegTool

StegTool is a web-based steganography tool that seamlessly hides and reveals encrypted secret messages within images. Developed as a Python project, it combines Least Significant Bit (LSB) steganography with Fernet symmetric encryption to ensure your data remains secure and invisible.

## ✨ Features

- **Secure Steganography**: Embeds hidden messages inside image files (PNG, JPG, JPEG) using LSB techniques.
- **Advanced Encryption**: Secures payloads with `cryptography.fernet`. Supports both auto-generated keys and password-derived keys (using PBKDF2HMAC with salting).
- **Data Compression**: Automatically applies `zlib` compression to maximize text capacity within images.
- **Batch Processing**: Hide or reveal secret messages across multiple images simultaneously.
- **Modern Web UI**: An intuitive, responsive interface powered by Streamlit, featuring real-time image previews and one-click copy to clipboard functionality.

## 🛠️ Technology Stack

- **Frontend/Backend**: Python & Streamlit (`streamlit`)
- **Cryptography**: `cryptography` (Fernet, PBKDF2)
- **Steganography**: `stegano`
- **Image Processing**: `Pillow` (PIL)

## 🚀 Installation

1. **Navigate to the project directory**:
   ```bash
   cd Steg_Tool
   ```

2. **Set up a virtual environment (Recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

To launch the TimSteg web interface, run the following command in your terminal:

```bash
streamlit run app.py
```

The application will open in your default web browser (typically at `http://localhost:8501`).

### Hiding a Message
1. Select the **Hide Message** tab.
2. Upload one or more target images (Max size: 5MB per file).
3. Enter your secret message.
4. Generate a secure random encryption key or provide a custom password.
5. Click **Hide Message** and download the resulting encoded PNG images. *(Note: Output images are saved as lossless PNGs to preserve the LSB payload).*

### Revealing a Message
1. Select the **Reveal Message** tab.
2. Upload the encoded image(s).
3. Enter the exact decryption key or password used during encryption.
4. Click **Reveal Message** to decrypt and view the hidden text.

## ⚠️ Security Notice

While steganography effectively conceals the *existence* of a message, it is not a replacement for strong cryptography. TimSteg pairs steganography with Fernet encryption to provide layered security. Always keep your encryption keys and passwords secure; losing them means the hidden message cannot be recovered.

---
*Developed as a Semester 4 Python Micro-Project.*