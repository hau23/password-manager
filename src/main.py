import getpass
import secrets
import string
from models import LoginEntry, CardEntry, NoteEntry
from crypto import CryptoManager
from storage import JSONStorage, Vault


VAULT_FILE = "vault.json"


def display_menu():
    """Display the main menu options."""
    print("\n========== Password Manager ==========")
    print("  1. Add new entry")
    print("  2. View all entries")
    print("  3. Search entries")
    print("  4. Edit an entry")
    print("  5. Delete an entry")
    print("  6. Generate random password")
    print("  7. Save and quit")
    print("======================================")


def display_entry_type_menu():
    """Display entry type selection."""
    print("\n  Choose entry type:")
    print("    1. Login (website/app credentials)")
    print("    2. Card (credit/debit card)")
    print("    3. Note (secure text note)")


def add_entry(vault):
    """Add a new entry to the vault."""
    display_entry_type_menu()
    choice = input("  Enter choice (1-3): ").strip()

    if choice == "1":
        title = input("  Site/App name: ").strip()
        url = input("  URL (optional, press Enter to skip): ").strip()
        username = input("  Username: ").strip()
        password = getpass.getpass("  Password (hidden): ")
        category = input("  Category (default: Login): ").strip() or "Login"
        entry = LoginEntry(title, username, password, url, category)

    elif choice == "2":
        title = input("  Card name (e.g. My Visa): ").strip()
        card_number = input("  Card number: ").strip()
        expiry = input("  Expiry date (MM/YY): ").strip()
        cvv = getpass.getpass("  CVV (hidden): ")
        category = input("  Category (default: Card): ").strip() or "Card"
        entry = CardEntry(title, card_number, expiry, cvv, category)

    elif choice == "3":
        title = input("  Note title: ").strip()
        content = input("  Content: ").strip()
        category = input("  Category (default: Note): ").strip() or "Note"
        entry = NoteEntry(title, content, category)

    else:
        print("  Invalid choice.")
        return

    vault.add_entry(entry)
    print(f"  Entry '{title}' added successfully!")


def view_all_entries(vault):
    """Display all entries in the vault."""
    entries = vault.get_all_entries()
    if not entries:
        print("\n  Vault is empty. No entries found.")
        return

    print(f"\n  Total entries: {len(entries)}")
    print("  " + "-" * 40)
    for i, entry in enumerate(entries):
        print(f"\n  [{i}]", end=" ")
        entry.display()


def search_entries(vault):
    """Search entries by keyword."""
    keyword = input("\n  Enter search keyword: ").strip()
    if not keyword:
        print("  Please enter a keyword.")
        return

    results = vault.search_entries(keyword)
    if not results:
        print(f"  No entries found matching '{keyword}'.")
        return

    print(f"\n  Found {len(results)} result(s):")
    for i, entry in enumerate(results):
        print(f"\n  [{i}]", end=" ")
        entry.display()


def edit_entry(vault):
    """Edit an existing entry."""
    entries = vault.get_all_entries()
    if not entries:
        print("\n  Vault is empty. Nothing to edit.")
        return

    # Show entries for selection
    view_all_entries(vault)
    try:
        index = int(input("\n  Enter entry number to edit: ").strip())
    except ValueError:
        print("  Invalid number.")
        return

    if index < 0 or index >= len(entries):
        print("  Invalid entry number.")
        return

    entry = entries[index]
    print(f"\n  Editing: {entry.get_title()}")
    print("  (Press Enter to keep current value)\n")

    if isinstance(entry, LoginEntry):
        new_title = input(f"  Title [{entry.get_title()}]: ").strip()
        new_password = getpass.getpass("  New password (hidden, Enter to keep): ")
        if new_title:
            entry.set_title(new_title)
        if new_password:
            entry.set_password(new_password)

    elif isinstance(entry, CardEntry):
        new_title = input(f"  Title [{entry.get_title()}]: ").strip()
        if new_title:
            entry.set_title(new_title)

    elif isinstance(entry, NoteEntry):
        new_title = input(f"  Title [{entry.get_title()}]: ").strip()
        new_content = input("  New content (Enter to keep): ").strip()
        if new_title:
            entry.set_title(new_title)
        if new_content:
            entry.set_content(new_content)

    print("  Entry updated successfully!")


def delete_entry(vault):
    """Delete an entry from the vault."""
    entries = vault.get_all_entries()
    if not entries:
        print("\n  Vault is empty. Nothing to delete.")
        return

    view_all_entries(vault)
    try:
        index = int(input("\n  Enter entry number to delete: ").strip())
    except ValueError:
        print("  Invalid number.")
        return

    removed = vault.delete_entry(index)
    if removed:
        print(f"  Entry '{removed.get_title()}' deleted.")
    else:
        print("  Invalid entry number.")


def generate_password():
    """Generate a random secure password."""
    try:
        length = int(input("\n  Password length (default 16): ").strip() or "16")
    except ValueError:
        length = 16

    if length < 8:
        print("  Minimum length is 8. Using 8.")
        length = 8

    # Ensure at least one of each character type
    characters = string.ascii_letters + string.digits + string.punctuation
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    # Fill the rest randomly
    for _ in range(length - 4):
        password.append(secrets.choice(characters))

    # Shuffle to randomize positions
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    final_password = ''.join(password_list)

    print(f"\n  Generated password: {final_password}")
    print("  (Copy it before it's gone!)")


def setup_new_vault():
    """Create a new vault with a master password."""
    print("\n========== New Vault Setup ==========")
    while True:
        password = getpass.getpass("  Create master password: ")
        if len(password) < 8:
            print("  Password must be at least 8 characters. Try again.")
            continue
        confirm = getpass.getpass("  Confirm master password: ")
        if password != confirm:
            print("  Passwords don't match. Try again.")
            continue
        break

    storage = JSONStorage()
    crypto = CryptoManager()
    vault = Vault(storage, crypto, filepath=VAULT_FILE)
    vault.setup_master_password(password)
    print("  Vault created successfully!")
    return vault


def unlock_existing_vault():
    """Unlock an existing vault with the master password."""
    print("\n========== Unlock Vault ==========")
    storage = JSONStorage()
    crypto = CryptoManager()
    vault = Vault(storage, crypto, filepath=VAULT_FILE)

    max_attempts = 3
    for attempt in range(max_attempts):
        password = getpass.getpass("  Enter master password: ")
        if vault.load_vault(password):
            print("  Vault unlocked successfully!")
            return vault
        remaining = max_attempts - attempt - 1
        if remaining > 0:
            print(f"  Wrong password. {remaining} attempt(s) left.")
        else:
            print("  Too many failed attempts. Exiting.")
            return None
    return None


def main():
    """Main entry point of the password manager."""
    print("\n  Welcome to Secure Password Manager")
    print("  " + "=" * 35)

    # Check if vault exists
    storage = JSONStorage()
    if storage.file_exists(VAULT_FILE):
        vault = unlock_existing_vault()
    else:
        vault = setup_new_vault()

    if vault is None:
        return

    # Main loop
    while True:
        display_menu()
        choice = input("  Enter choice (1-7): ").strip()

        if choice == "1":
            add_entry(vault)
        elif choice == "2":
            view_all_entries(vault)
        elif choice == "3":
            search_entries(vault)
        elif choice == "4":
            edit_entry(vault)
        elif choice == "5":
            delete_entry(vault)
        elif choice == "6":
            generate_password()
        elif choice == "7":
            vault.save_vault()
            print("\n  Vault saved. Goodbye!")
            break
        else:
            print("  Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
