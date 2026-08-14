import os
from cryptography.fernet import Fernet

def get_cipher():
    """
    Retrieves the Fernet cipher instance using ENCRYPTION_KEY 
    from environment variables (GitHub Actions) or Streamlit secrets.
    """
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
    """Encrypts any plaintext string (token, name, user_id) into Fernet ciphertext."""
    if not val:
        return ""
    clean_val = str(val).strip()
    cipher = get_cipher()
    return cipher.encrypt(clean_val.encode()).decode()

def decrypt_value(val: str) -> str:
    """
    Decrypts ciphertext string back to plaintext.
    Maintains backward compatibility for unencrypted legacy plain text.
    """
    if not val:
        return ""
    
    # Return as-is if the string is not Fernet ciphertext
    if not str(val).startswith("gAAAAA"):
        return str(val)

    try:
        cipher = get_cipher()
        return cipher.decrypt(str(val).encode()).decode()
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return str(val)
