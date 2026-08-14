import os
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

def encrypt_token(raw_token: str) -> str:
    """Encrypts plaintext authorization token before saving to database."""
    if not raw_token:
        return ""
    # Strip whitespace or extra Bearer prefixes if present
    clean_token = raw_token.strip()
    cipher = get_cipher()
    return cipher.encrypt(clean_token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts ciphertext token back to plaintext in memory for execution."""
    if not encrypted_token:
        return ""
    
    # If token is already plaintext (legacy tokens before encryption rollout)
    if encrypted_token.startswith("Bearer ") or encrypted_token.startswith("eyJ"):
        return encrypted_token

    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        print(f"❌ Token decryption failed: {e}")
        return ""
