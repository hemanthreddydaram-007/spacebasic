import os
import streamlit as st
from cryptography.fernet import Fernet

def get_secret_key() -> str:
    key = os.getenv("SECRET_KEY")
    if not key:
        try:
            key = st.secrets["SECRET_KEY"]
        except Exception:
            key = None
            
    if not key:
        raise ValueError("SECRET_KEY is missing from environment or Streamlit secrets.")
    return key.strip()

def encrypt_value(raw_value: str) -> str:
    if not raw_value:
        return ""
    cipher = Fernet(get_secret_key().encode())
    return cipher.encrypt(raw_value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value:
        return ""
    cipher = Fernet(get_secret_key().encode())
    return cipher.decrypt(encrypted_value.encode()).decode()
