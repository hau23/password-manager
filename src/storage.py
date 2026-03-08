import json
import os
from abc import ABC, abstractmethod
from models import LoginEntry, CardEntry, NoteEntry
from crypto import CryptoManager


class BaseStorage(ABC):
    """Abstract base class for storage backends. (Abstraction + Polymorphism)"""

    @abstractmethod
    def save(self, data, filepath):
        """Save data to storage."""
        pass

    @abstractmethod
    def load(self, filepath):
        """Load data from storage."""
        pass

    @abstractmethod
    def file_exists(self, filepath):
        """Check if storage file exists."""
        pass


class JSONStorage(BaseStorage):
    """Stores encrypted entries in a JSON file. Inherits from BaseStorage."""

    def save(self, data, filepath):
        """Save dictionary data to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def load(self, filepath):
        """Load dictionary data from a JSON file."""
        if not self.file_exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)

    def file_exists(self, filepath):
        """Check if the JSON file exists."""
        return os.path.exists(filepath)


class Vault:
    """
    Manages all entries and handles saving/loading with encryption.
    This is the main controller that connects models, crypto, and storage.
    """

    def __init__(self, storage, crypto, filepath="vault.json"):
        self._storage = storage          # BaseStorage instance
        self._crypto = crypto            # CryptoManager instance
        self._filepath = filepath        # where to save the vault file
        self._entries = []               # list of Entry objects
        self._master_hash = None         # hashed master password
        self._salt = None                # salt for hashing

    # ========== Master Password Setup ==========

    def setup_master_password(self, password):
        """First time setup: hash and store the master password."""
        self._salt = self._crypto.generate_salt()
        self._master_hash = self._crypto.hash_master_password(password, self._salt)
        self._crypto.derive_key_from_password(password, self._salt)

    def unlock(self, password):
        """Verify master password and unlock the vault."""
        if self._crypto.verify_master_password(password, self._salt, self._master_hash):
            self._crypto.derive_key_from_password(password, self._salt)
            return True
        return False

    # ========== Entry Management ==========

    def add_entry(self, entry):
        """Add a new entry to the vault."""
        self._entries.append(entry)

    def delete_entry(self, index):
        """Delete an entry by its index."""
        if 0 <= index < len(self._entries):
            removed = self._entries.pop(index)
            return removed
        return None

    def get_all_entries(self):
        """Return all entries."""
        return self._entries

    def search_entries(self, keyword):
        """Search entries by title (case-insensitive)."""
        keyword = keyword.lower()
        results = []
        for entry in self._entries:
            if keyword in entry.get_title().lower():
                results.append(entry)
        return results

    def get_entries_by_type(self, entry_type):
        """Filter entries by type (e.g., LoginEntry, CardEntry)."""
        results = []
        for entry in self._entries:
            if isinstance(entry, entry_type):
                results.append(entry)
        return results

    # ========== Save & Load with Encryption ==========

    def save_vault(self):
        """Encrypt all entries and save to file."""
        entries_data = []
        for entry in self._entries:
            entry_dict = entry.to_dict()
            # Encrypt sensitive fields based on entry type
            if isinstance(entry, LoginEntry):
                entry_dict["password"] = self._crypto.encrypt(entry_dict["password"])
            elif isinstance(entry, CardEntry):
                entry_dict["card_number"] = self._crypto.encrypt(entry_dict["card_number"])
                entry_dict["cvv"] = self._crypto.encrypt(entry_dict["cvv"])
            elif isinstance(entry, NoteEntry):
                entry_dict["content"] = self._crypto.encrypt(entry_dict["content"])
            entries_data.append(entry_dict)

        vault_data = {
            "master_hash": self._master_hash,
            "salt": self._salt.hex(),
            "entries": entries_data
        }
        self._storage.save(vault_data, self._filepath)

    def load_vault(self, password):
        """Load vault from file and decrypt entries."""
        data = self._storage.load(self._filepath)
        if data is None:
            return False

        # Restore master password hash and salt
        self._master_hash = data["master_hash"]
        self._salt = bytes.fromhex(data["salt"])

        # Verify master password
        if not self.unlock(password):
            return False

        # Rebuild entry objects with decrypted data
        self._entries = []
        for entry_dict in data["entries"]:
            entry = self._rebuild_entry(entry_dict)
            if entry:
                self._entries.append(entry)
        return True

    def _rebuild_entry(self, entry_dict):
        """Rebuild an Entry object from a dictionary, decrypting sensitive fields."""
        entry_type = entry_dict.get("type")

        if entry_type == "login":
            return LoginEntry(
                title=entry_dict["title"],
                username=entry_dict["username"],
                password=self._crypto.decrypt(entry_dict["password"]),
                url=entry_dict.get("url", ""),
                category=entry_dict.get("category", "Login")
            )
        elif entry_type == "card":
            return CardEntry(
                title=entry_dict["title"],
                card_number=self._crypto.decrypt(entry_dict["card_number"]),
                expiry=entry_dict["expiry"],
                cvv=self._crypto.decrypt(entry_dict["cvv"]),
                category=entry_dict.get("category", "Card")
            )
        elif entry_type == "note":
            return NoteEntry(
                title=entry_dict["title"],
                content=self._crypto.decrypt(entry_dict["content"]),
                category=entry_dict.get("category", "Note")
            )
        return None

    def vault_exists(self):
        """Check if a vault file already exists."""
        return self._storage.file_exists(self._filepath)


# ========== Quick Test ==========
if __name__ == "__main__":
    # Setup
    storage = JSONStorage()
    crypto = CryptoManager()
    vault = Vault(storage, crypto, filepath="test_vault.json")

    # --- Test 1: Create new vault ---
    print("=== Creating New Vault ===")
    vault.setup_master_password("MyMaster123!")

    # Add entries
    vault.add_entry(LoginEntry("GitHub", "john123", "ghPass!@#", "https://github.com"))
    vault.add_entry(LoginEntry("Gmail", "john@gmail.com", "gmailPass456", "https://gmail.com"))
    vault.add_entry(CardEntry("My Visa", "4111222233334444", "12/27", "123"))
    vault.add_entry(NoteEntry("WiFi", "Home network password: wifi_2024"))

    # Save vault
    vault.save_vault()
    print("  Vault saved successfully!")
    print()

    # --- Test 2: Load vault with correct password ---
    print("=== Loading Vault (correct password) ===")
    vault2 = Vault(JSONStorage(), CryptoManager(), filepath="test_vault.json")
    success = vault2.load_vault("MyMaster123!")
    print(f"  Loaded: {success}")
    print(f"  Total entries: {len(vault2.get_all_entries())}")
    print()

    # Display all entries
    for entry in vault2.get_all_entries():
        entry.display()
        print()

    # --- Test 3: Load vault with wrong password ---
    print("=== Loading Vault (wrong password) ===")
    vault3 = Vault(JSONStorage(), CryptoManager(), filepath="test_vault.json")
    success = vault3.load_vault("WrongPassword")
    print(f"  Loaded: {success}")
    print()

    # --- Test 4: Search ---
    print("=== Search for 'git' ===")
    results = vault2.search_entries("git")
    for entry in results:
        entry.display()

    # Clean up test file
    os.remove("test_vault.json")
    print("\n  Test file cleaned up.")
