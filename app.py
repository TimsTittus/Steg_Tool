import streamlit as st
from clipboard_utils import clipboard_button
from crypto_utils import generate_key, is_valid_fernet_key, encrypt_message, decrypt_message
from pbkdf2_utils import derive_fernet_key_from_password, generate_salt
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

# Security Notice
st.markdown(
    """
    <div style='background:#fff3cd;border-left:6px solid #ffe066;padding:12px 18px;margin-bottom:16px;'>
        <strong>Security Notice:</strong> Steganography only hides the existence of a message, but does not provide strong security by itself. Always use strong encryption (like Fernet) in addition to steganography for sensitive information. Never rely on steganography alone to protect secrets.
    </div>
    """,
    unsafe_allow_html=True
)

# Option Selection
st.markdown("---")
option = st.radio("Choose an option:", ["Hide Message", "Reveal Message"], horizontal=True)
st.markdown("---")

# Hide Message Section
if option == "Hide Message":
    with st.form("hide_message_form"):
        st.markdown("### Upload an Image")
        uploaded_images = st.file_uploader(
            label="Upload images (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            help="Select one or more image files to hide your message in.",
            accept_multiple_files=True
        )

        valid_images = []
        if uploaded_images:
            for img_file in uploaded_images:
                if img_file.size > MAX_FILE_SIZE_BYTES:
                    st.error(f"File '{img_file.name}' too large! Maximum allowed size is {MAX_FILE_SIZE_MB} MB. Your file is {img_file.size / (1024 * 1024):.2f} MB.")
                else:
                    try:
                        img_preview = Image.open(img_file)
                        st.image(
                            img_preview,
                            caption=f"Preview: {img_file.name}",
                            width=700,
                            output_format="PNG",
                            channels="RGB",
                            use_column_width=False,
                            alt=f"Preview of uploaded image {img_file.name} for screen readers"
                        )
                        valid_images.append(img_file)
                    except Exception:
                        st.warning(f"Could not preview image '{img_file.name}'.")

        st.markdown("### Secret Message")
        secret_message = st.text_area(
            label="Enter the secret message:",
            placeholder="Type your secret message here...",
            help="This message will be encrypted and hidden in the image."
        )

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

        st.markdown("#### Password-Based Encryption Key")
        password = st.text_input("Enter password:", type="password", help="A password will be used to derive the encryption key.")
        salt = st.text_input("Salt (leave blank to auto-generate):", help="A random salt is recommended for each message. Save it for decryption.")
        if not salt:
            if 'generated_salt' not in st.session_state:
                st.session_state.generated_salt = generate_salt().hex()
            salt = st.session_state.generated_salt
        st.code(f"Salt (save this for decryption!): {salt}")
        class KeyWithSalt(str):
            pass
        encryption_key = KeyWithSalt(derive_fernet_key_from_password(password, bytes.fromhex(salt))) if password else ""
        if encryption_key:
            encryption_key.pbkdf2_salt_hex = salt
        hide_btn = st.form_submit_button("Hide Message")

        if hide_btn and valid_images and secret_message and encryption_key:
            if not is_valid_fernet_key(encryption_key):
                st.error("Invalid encryption key format. Key must be 44 url-safe base64 characters.")
            else:
                for img_file in valid_images:
                    try:
                        image = Image.open(img_file)
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        png_bytes = io.BytesIO()
                        image.save(png_bytes, format="PNG")
                        png_bytes.seek(0)
                        image = Image.open(png_bytes)
                        capacity = image.width * image.height
                        secret_image = hide_message(image, secret_message, encryption_key)
                        image_bytes = io.BytesIO()
                        secret_image.save(image_bytes, format="PNG")
                        image_bytes.seek(0)
                        st.success(f"Message hidden in '{img_file.name}' successfully!")
                        st.download_button(f"⬇Download Encoded Image ({img_file.name})", image_bytes, f"encoded_{img_file.name}.png", "image/png")
                    except ValueError as e:
                        st.error(f"[{img_file.name}] Invalid encryption key format: {e}")
                    except UnidentifiedImageError:
                        st.error(f"[{img_file.name}] Cannot process this image. Please upload a valid PNG, JPG, or JPEG file.")
                    except Exception as e:
                        st.error(f"[{img_file.name}] Unexpected error: {e}")

elif option == "Reveal Message":
    with st.form("reveal_message_form"):
        st.markdown("### Upload an Encoded Image")
        uploaded_images = st.file_uploader(
            label="Upload encoded images (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            help="Select one or more image files containing the hidden message.",
            accept_multiple_files=True
        )

        valid_images = []
        if uploaded_images:
            for img_file in uploaded_images:
                if img_file.size > MAX_FILE_SIZE_BYTES:
                    st.error(f"File '{img_file.name}' too large! Maximum allowed size is {MAX_FILE_SIZE_MB} MB. Your file is {img_file.size / (1024 * 1024):.2f} MB.")
                else:
                    try:
                        img_preview = Image.open(img_file)
                        st.image(
                            img_preview,
                            caption=f"Preview: {img_file.name}",
                            width=700,
                            output_format="PNG",
                            channels="RGB",
                            use_column_width=False,
                            alt=f"Preview of uploaded image {img_file.name} for screen readers"
                        )
                        valid_images.append(img_file)
                    except Exception:
                        st.warning(f"Could not preview image '{img_file.name}'.")

        st.markdown("### Password-Based Decryption Key")
        password = st.text_input("Enter password:", type="password", help="Enter the password used for encryption.", key="reveal_password")
        # salt will be extracted from payload automatically
        class KeyWithSalt(str):
            pass
        decryption_key = KeyWithSalt(derive_fernet_key_from_password(password, b"")) if password else ""
        reveal_btn = st.form_submit_button("Reveal Message")

    if reveal_btn and valid_images and decryption_key:
            if not is_valid_fernet_key(decryption_key):
                st.error("Invalid decryption key format. Key must be 44 url-safe base64 characters.")
            else:
                for img_file in valid_images:
                    try:
                        image = Image.open(img_file)
                        hidden_message = reveal_message(image, decryption_key)
                        st.text_area(
                            label=f"Hidden Message from {img_file.name}:",
                            value=hidden_message,
                            help="This is the message revealed from the image.",
                            placeholder="Revealed message will appear here..."
                        )
                    except ValueError as e:
                        st.error(f"[{img_file.name}] Invalid decryption key format: {e}")
                    except UnidentifiedImageError:
                        st.error(f"[{img_file.name}] Cannot process this image. Please upload a valid encoded image.")
                    except Exception as e:
                        st.error(f"[{img_file.name}] Unexpected error: {e}")

st.markdown("---")
st.markdown("<h4 style='text-align: center; color: gray;'>TimSteg</h4>", unsafe_allow_html=True)
