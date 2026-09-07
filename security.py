import os
import streamlit as st
from cryptography.fernet import Fernet

def get_secret_key() -> str:
    # 1. Check OS Environment Variables (Local PC or GitHub Actions)
    key = os.getenv("SECRET_KEY") or os.getenv("ENCRYPTION_KEY")
    
    # 2. Check Streamlit Secrets (Streamlit Cloud deployment)
    if not key:
        try:
            key = st.secrets.get("SECRET_KEY") or st.secrets.get("ENCRYPTION_KEY")
        except Exception:
            key = None
            
    if not key:
        raise ValueError("SECRET_KEY or ENCRYPTION_KEY is missing from environment or Streamlit secrets.")
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
