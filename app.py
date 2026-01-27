import streamlit as st
from clipboard_utils import clipboard_button
from crypto_utils import generate_key, is_valid_fernet_key, encrypt_message, decrypt_message
from stego_utils import hide_message, reveal_message
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

## Crypto and stego logic moved to crypto_utils.py and stego_utils.py

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
    with st.form("hide_message_form"):
        st.markdown("### Upload an Image")
        uploaded_image = st.file_uploader("Upload an image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

        if uploaded_image and uploaded_image.size <= MAX_FILE_SIZE_BYTES:
            try:
                img_preview = Image.open(uploaded_image)
                st.image(img_preview, caption="Preview of uploaded image", width=700)
            except Exception:
                st.warning("Could not preview this image.")

        if uploaded_image and uploaded_image.size > MAX_FILE_SIZE_BYTES:
            st.error(f"File too large! Maximum allowed size is {MAX_FILE_SIZE_MB} MB. Your file is {uploaded_image.size / (1024 * 1024):.2f} MB.")
            uploaded_image = None

        st.markdown("### Secret Message")
        secret_message = st.text_area("Enter the secret message:")

        # Generate Key
        gen_key_col, show_key_col = st.columns([1, 2])
        with gen_key_col:
            gen_key_btn = st.form_submit_button("Generate Encryption Key")
        with show_key_col:
            show_key = st.checkbox("Show generated encryption key")

        if gen_key_btn:
            st.session_state.generated_key = generate_key()

        if st.session_state.generated_key and show_key:
            st.text_area("Save this key for decryption:", st.session_state.generated_key, key="key_display")
            clipboard_button(st.session_state.generated_key, label="Copy to Clipboard")
            st.markdown('<p style="color:gray; font-size:12px;">Copy this key safely for future use.</p>', unsafe_allow_html=True)

        encryption_key = st.text_input("Enter encryption key:")
        hide_btn = st.form_submit_button("Hide Message")

        if hide_btn and uploaded_image and secret_message and encryption_key:
            if not is_valid_fernet_key(encryption_key):
                st.error("Invalid encryption key format. Key must be 44 url-safe base64 characters.")
            else:
                try:
                    image = Image.open(uploaded_image)
                    # Convert to PNG and RGB for LSB safety
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    png_bytes = io.BytesIO()
                    image.save(png_bytes, format="PNG")
                    png_bytes.seek(0)
                    image = Image.open(png_bytes)

                    capacity = image.width * image.height
                    encrypted_message = encrypt_message(secret_message, encryption_key)
                    if len(encrypted_message) > capacity:
                        st.error(f"Message too large to hide in this image. Max size: {capacity} bytes, message size: {len(encrypted_message)} bytes.")
                    else:
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
    with st.form("reveal_message_form"):
        st.markdown("### Upload an Encoded Image")
        uploaded_image = st.file_uploader("Upload the encoded image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

        if uploaded_image and uploaded_image.size <= MAX_FILE_SIZE_BYTES:
            try:
                img_preview = Image.open(uploaded_image)
                st.image(img_preview, caption="Preview of uploaded image", width=700)
            except Exception:
                st.warning("Could not preview this image.")

        if uploaded_image and uploaded_image.size > MAX_FILE_SIZE_BYTES:
            st.error(f"File too large! Maximum allowed size is {MAX_FILE_SIZE_MB} MB. Your file is {uploaded_image.size / (1024 * 1024):.2f} MB.")
            uploaded_image = None

        st.markdown("### Enter Decryption Key")
        decryption_key = st.text_input("Enter decryption key:")
        reveal_btn = st.form_submit_button("Reveal Message")

        if reveal_btn and uploaded_image and decryption_key:
            if not is_valid_fernet_key(decryption_key):
                st.error("Invalid decryption key format. Key must be 44 url-safe base64 characters.")
            else:
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
