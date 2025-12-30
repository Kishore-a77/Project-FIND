from cryptography.fernet import Fernet
import streamlit as st

KEY = st.secrets["storage"]["fernet_key"].encode()
cipher = Fernet(KEY)

def encrypt_image(data: bytes) -> bytes:
    return cipher.encrypt(data)

def decrypt_image(data: bytes) -> bytes:
    return cipher.decrypt(data)
