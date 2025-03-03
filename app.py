import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import base64
from PIL import Image
import io

# Streamlit UI Configuration
st.set_page_config(page_title="StegX", page_icon="🔒", layout="centered")

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

# Function to Generate Encryption Key
def generate_key():
    return Fernet.generate_key().decode()

# Function to Encrypt a Message
def encrypt_message(message, key):
    cipher_suite = Fernet(key.encode())  
    encrypted_message = cipher_suite.encrypt(message.encode())
    return base64.urlsafe_b64encode(encrypted_message).decode()

# Function to Decrypt a Message
def decrypt_message(encrypted_message, key):
    cipher_suite = Fernet(key.encode())  
    decrypted_message = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_message)).decode()
    return decrypted_message

# Function to Hide a Message in an Image
def hide_message(image, message, key):
    encrypted_message = encrypt_message(message, key)
    secret_image = lsb.hide(image, encrypted_message)
    return secret_image

# Function to Reveal a Hidden Message from an Image
def reveal_message(image, key):
    encrypted_message = lsb.reveal(image)
    if encrypted_message:
        try:
            return decrypt_message(encrypted_message, key)
        except Exception:
            return "❌ Decryption failed! Invalid key."
    return "⚠️ No hidden message found."

# Title
st.markdown("<h1 style='text-align: center;'>🔒 StegX 🔒</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Hide and Reveal Secret Messages in Images</h3>", unsafe_allow_html=True)

# Option Selection
st.markdown("---")
option = st.radio("📌 Choose an option:", ["Hide Message", "Reveal Message"], horizontal=True)
st.markdown("---")

# Hide Message Section
if option == "Hide Message":
    st.markdown("### 🖼️ Upload an Image")
    uploaded_image = st.file_uploader("Upload an image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    st.markdown("### 🔑 Secret Message")
    secret_message = st.text_area("Enter the secret message:")

    # Generate Key
    if st.button("🔑 Generate Encryption Key"):
        key = generate_key()
        st.text_area("🔑 Save this key for decryption:", key)
        st.markdown(f'<p style="color:gray; font-size:12px;">Copy this key safely for future use.</p>', unsafe_allow_html=True)

    encryption_key = st.text_input("🔐 Enter encryption key:")

    # Hide Message in Image
    if st.button("🖼️ Hide Message") and uploaded_image and secret_message and encryption_key:
        try:
            image = Image.open(uploaded_image)
            secret_image = hide_message(image, secret_message, encryption_key)

            # Save the encoded image in memory
            image_bytes = io.BytesIO()
            secret_image.save(image_bytes, format="PNG")
            image_bytes.seek(0)

            st.success("✅ Message hidden successfully!")
            st.download_button("⬇️ Download Encoded Image", image_bytes, "encoded_image.png", "image/png")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# Reveal Message Section
elif option == "Reveal Message":
    st.markdown("### 🔍 Upload an Encoded Image")
    uploaded_image = st.file_uploader("Upload the encoded image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

    st.markdown("### 🔑 Enter Decryption Key")
    decryption_key = st.text_input("Enter decryption key:")

    if st.button("🔓 Reveal Message") and uploaded_image and decryption_key:
        try:
            image = Image.open(uploaded_image)
            hidden_message = reveal_message(image, decryption_key)
            st.text_area("📩 Hidden Message:", hidden_message)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# Footer
st.markdown("---")
st.markdown("<h4 style='text-align: center; color: gray;'>Mini Project by Tims Tittus</h4>", unsafe_allow_html=True)
