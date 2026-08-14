import os
import hashlib
from cryptography.fernet import Fernet

def get_cipher():
    """Retrieves Fernet cipher using key from environment or Streamlit secrets."""
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

def encrypt_value(raw_val: str) -> str:
    """Encrypts any plaintext string (token, name, user_id)."""
    if not raw_val:
        return ""
    clean_val = str(raw_val).strip()
    cipher = get_cipher()
    return cipher.encrypt(clean_val.encode()).decode()

def decrypt_value(encrypted_val: str) -> str:
    """Decrypts ciphertext string back to plaintext."""
    if not encrypted_val:
        return ""
    try:
        cipher = get_cipher()
        return cipher.decrypt(str(encrypted_val).encode()).decode()
    except Exception:
        # Backward compatibility if already plain
        return str(encrypted_val)

def hash_id(user_id: str) -> str:
    """Generates a consistent SHA-256 hash for database row identification."""
    return hashlib.sha256(str(user_id).strip().encode()).hexdigest()
