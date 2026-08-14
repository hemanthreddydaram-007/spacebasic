import os
import hashlib
from cryptography.fernet import Fernet

def get_cipher():
    """Retrieves Fernet cipher instance using key from environment or Streamlit secrets."""
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
    """Encrypts any string into a Fernet ciphertext (randomized IV)."""
    if not val:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(str(val).strip().encode()).decode()

def decrypt_value(val: str) -> str:
    """Decrypts Fernet ciphertext back to plain text."""
    if not val:
        return ""
    # If not encrypted (legacy plain text), return as-is
    if not str(val).startswith("gAAAAA"):
        return str(val)
    try:
        cipher = get_cipher()
        return cipher.decrypt(str(val).encode()).decode()
    except Exception as e:
        print(f"❌ Decryption error: {e}")
        return str(val)

def hash_identifier(val: str) -> str:
    """Creates a consistent SHA-256 hash used as the unique database row key."""
    if not val:
        return ""
    return hashlib.sha256(str(val).strip().encode()).hexdigest()
