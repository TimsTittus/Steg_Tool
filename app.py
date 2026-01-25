import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet, InvalidToken
import base64
import binascii
from PIL import Image, UnidentifiedImageError
import io

st.set_page_config(page_title="StegX", page_icon=" ", layout="centered")

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Custom Styling
st.markdown(
    """
    <style>
        .stTextArea textarea { font-size: 16px !important; }
        .stTextInput input { font-size: 16px !important; }
        .stButton button { font-size: 18px !important; padding: 8px 20px; }
        .stDownloadButton button { background-color: #4CAF50 !important; color: white !important; }
    </style>
    """,
    unsafe_allow_html=True
)

def generate_key():
    return Fernet.generate_key().decode()

def encrypt_message(message, key):
    cipher_suite = Fernet(key.encode())  
    encrypted_message = cipher_suite.encrypt(message.encode())
    return base64.urlsafe_b64encode(encrypted_message).decode()

def decrypt_message(encrypted_message, key):
    cipher_suite = Fernet(key.encode())  
    decrypted_message = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_message)).decode()
    return decrypted_message

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

# Session state for storing the encryption key
if "generated_key" not in st.session_state:
    st.session_state.generated_key = None

# Title
st.markdown("<h1 style='text-align: center;'>TimSteg</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Hide and Reveal Secret Messages in Images</h3>", unsafe_allow_html=True)

# Option Selection
st.markdown("---")
option = st.radio("Choose an option:", ["Hide Message", "Reveal Message"], horizontal=True)
st.markdown("---")

# Hide Message Section
if option == "Hide Message":
    st.markdown("### Upload an Image")
    uploaded_image = st.file_uploader("Upload an image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_image and uploaded_image.size > MAX_FILE_SIZE_BYTES:
        st.error(f"File too large! Maximum allowed size is {MAX_FILE_SIZE_MB} MB. Your file is {uploaded_image.size / (1024 * 1024):.2f} MB.")
        uploaded_image = None
    
    st.markdown("### Secret Message")
    secret_message = st.text_area("Enter the secret message:")

    # Generate Key
    if st.button("Generate Encryption Key"):
        st.session_state.generated_key = generate_key()
    
    # Display the generated key if it exists
    if st.session_state.generated_key:
        st.text_area("Save this key for decryption:", st.session_state.generated_key, key="key_display")
        st.markdown('<p style="color:gray; font-size:12px;">Copy this key safely for future use.</p>', unsafe_allow_html=True)

    encryption_key = st.text_input("Enter encryption key:", value=st.session_state.generated_key or "")

    if st.button("Hide Message") and uploaded_image and secret_message and encryption_key:
        try:
            image = Image.open(uploaded_image)
            secret_image = hide_message(image, secret_message, encryption_key)

            image_bytes = io.BytesIO()
            secret_image.save(image_bytes, format="PNG")
            image_bytes.seek(0)

            st.success("Message hidden successfully!")
            st.download_button("⬇Download Encoded Image", image_bytes, "encoded_image.png", "image/png")
        except ValueError as e:
            st.error(f"Invalid encryption key format: {e}")
        except UnidentifiedImageError:
            st.error("Cannot process this image. Please upload a valid PNG, JPG, or JPEG file.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

elif option == "Reveal Message":
    st.markdown("### Upload an Encoded Image")
    uploaded_image = st.file_uploader("Upload the encoded image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_image and uploaded_image.size > MAX_FILE_SIZE_BYTES:
        st.error(f"File too large! Maximum allowed size is {MAX_FILE_SIZE_MB} MB. Your file is {uploaded_image.size / (1024 * 1024):.2f} MB.")
        uploaded_image = None

    st.markdown("### Enter Decryption Key")
    decryption_key = st.text_input("Enter decryption key:")

    if st.button("Reveal Message") and uploaded_image and decryption_key:
        try:
            image = Image.open(uploaded_image)
            hidden_message = reveal_message(image, decryption_key)
            st.text_area("Hidden Message:", hidden_message)
        except ValueError as e:
            st.error(f"Invalid decryption key format: {e}")
        except UnidentifiedImageError:
            st.error("Cannot process this image. Please upload a valid encoded image.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.markdown("---")
st.markdown("<h4 style='text-align: center; color: gray;'>TimSteg</h4>", unsafe_allow_html=True)
