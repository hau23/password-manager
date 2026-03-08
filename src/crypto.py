import hashlib
import os
import base64
from cryptography.fernet import Fernet


class CryptoManager:
    """Handles all encryption, decryption and hashing operations."""

    def __init__(self):
        self._fernet = None  # will be set after master password is verified

    # ========== Master Password Hashing ==========

    def generate_salt(self):
        """Generate a random salt (16 bytes) for hashing."""
        return os.urandom(16)

    def hash_master_password(self, password, salt):
        """
        Hash the master password using SHA-256 with salt.
        This is ONE-WAY — you cannot reverse it back to the original password.
        Used for verifying the master password is correct.
        """
        salted = salt + password.encode('utf-8')
        return hashlib.sha256(salted).hexdigest()

    def verify_master_password(self, password, salt, stored_hash):
        """Check if the entered password matches the stored hash."""
        return self.hash_master_password(password, salt) == stored_hash

    # ========== Encryption Key Generation ==========

    def derive_key_from_password(self, password, salt):
        """
        Derive a Fernet encryption key from the master password.
        This key is used to encrypt/decrypt stored passwords.
        """
        # Combine password and salt, then hash to get 32 bytes
        salted = salt + password.encode('utf-8')
        key_bytes = hashlib.sha256(salted).digest()  # 32 bytes
        # Fernet requires base64-encoded 32-byte key
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        self._fernet = Fernet(fernet_key)
        return fernet_key

    # ========== Encrypt / Decrypt Passwords ==========

    def encrypt(self, plain_text):
        """Encrypt a string (e.g., a stored password). Returns encrypted string."""
        if self._fernet is None:
            raise Exception("Encryption key not set. Call derive_key_from_password() first.")
        return self._fernet.encrypt(plain_text.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_text):
        """Decrypt an encrypted string back to plain text."""
        if self._fernet is None:
            raise Exception("Encryption key not set. Call derive_key_from_password() first.")
        return self._fernet.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')


# ========== Quick Test ==========
if __name__ == "__main__":
    crypto = CryptoManager()

    # --- Test 1: Master password hashing ---
    print("=== Master Password Hashing ===")
    salt = crypto.generate_salt()
    master_password = "MySecretPass123!"
    hashed = crypto.hash_master_password(master_password, salt)
    print(f"  Salt (hex):   {salt.hex()}")
    print(f"  Hashed:       {hashed}")

    # Verify correct password
    print(f"  Correct pass: {crypto.verify_master_password('MySecretPass123!', salt, hashed)}")
    # Verify wrong password
    print(f"  Wrong pass:   {crypto.verify_master_password('WrongPass', salt, hashed)}")
    print()

    # --- Test 2: Encrypt and decrypt ---
    print("=== Encryption / Decryption ===")
    crypto.derive_key_from_password(master_password, salt)

    original = "github_password_2024!"
    encrypted = crypto.encrypt(original)
    decrypted = crypto.decrypt(encrypted)

    print(f"  Original:  {original}")
    print(f"  Encrypted: {encrypted}")
    print(f"  Decrypted: {decrypted}")
    print(f"  Match:     {original == decrypted}")
