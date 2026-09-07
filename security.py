import os
from cryptography.fernet import Fernet

def get_cipher():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("ENCRYPTION_KEY")
        except Exception:
            pass

    if not key:
        raise ValueError("⛔ CRITICAL: ENCRYPTION_KEY is missing from environment variables / secrets!")

    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt_value(val: str) -> str:
    """Encrypts raw text (e.g., password) into Fernet ciphertext."""
    if not val:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(str(val).strip().encode()).decode()

def decrypt_value(val: str) -> str:
    """Decrypts ciphertext string back to plaintext."""
    if not val:
        return ""
    if not str(val).startswith("gAAAAA"):
        return str(val)
    try:
        cipher = get_cipher()
        return cipher.decrypt(str(val).encode()).decode()
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return str(val)
