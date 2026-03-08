from abc import ABC, abstractmethod
from datetime import datetime


class Entry(ABC):
    """Abstract base class for all password manager entries."""

    def __init__(self, title, category="General"):
        self._title = title  # encapsulation: protected attribute
        self._category = category
        self._created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._updated_at = self._created_at

    # --- Getters and Setters (Encapsulation) ---
    def get_title(self):
        return self._title

    def set_title(self, new_title):
        self._title = new_title
        self._updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_category(self):
        return self._category

    def get_created_at(self):
        return self._created_at

    # --- Abstract methods (Abstraction) ---
    @abstractmethod
    def display(self):
        """Display the entry details. Each subclass shows different info."""
        pass

    @abstractmethod
    def to_dict(self):
        """Convert entry to dictionary for saving to file."""
        pass

    # --- Common method ---
    def __str__(self):
        return f"[{self._category}] {self._title}"


class LoginEntry(Entry):
    """Stores website login credentials. Inherits from Entry."""

    def __init__(self, title, username, password, url="", category="Login"):
        super().__init__(title, category)  # call parent constructor
        self._username = username
        self.__password = password  # encapsulation: private attribute
        self._url = url

    # Getter for private password
    def get_password(self):
        return self.__password

    def set_password(self, new_password):
        self.__password = new_password
        self._updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Polymorphism: each subclass implements display() differently
    def display(self):
        print(f"--- Login Entry ---")
        print(f"  Title:    {self._title}")
        print(f"  URL:      {self._url}")
        print(f"  Username: {self._username}")
        print(f"  Password: {'*' * len(self.__password)}")
        print(f"  Category: {self._category}")
        print(f"  Created:  {self._created_at}")

    def to_dict(self):
        return {
            "type": "login",
            "title": self._title,
            "username": self._username,
            "password": self.__password,
            "url": self._url,
            "category": self._category,
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }


class CardEntry(Entry):
    """Stores credit/debit card information. Inherits from Entry."""

    def __init__(self, title, card_number, expiry, cvv, category="Card"):
        super().__init__(title, category)
        self._card_number = card_number
        self.__cvv = cvv  # private: sensitive data
        self._expiry = expiry

    def get_cvv(self):
        return self.__cvv

    # Polymorphism: different display format for cards
    def display(self):
        masked_number = "****-****-****-" + self._card_number[-4:]
        print(f"--- Card Entry ---")
        print(f"  Title:   {self._title}")
        print(f"  Number:  {masked_number}")
        print(f"  Expiry:  {self._expiry}")
        print(f"  CVV:     ***")
        print(f"  Category: {self._category}")
        print(f"  Created:  {self._created_at}")

    def to_dict(self):
        return {
            "type": "card",
            "title": self._title,Z
            "card_number": self._card_number,
            "expiry": self._expiry,
            "cvv": self.__cvv,
            "category": self._category,
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }


class NoteEntry(Entry):
    """Stores secure text notes. Inherits from Entry."""

    def __init__(self, title, content, category="Note"):
        super().__init__(title, category)
        self._content = content

    def get_content(self):
        return self._content

    def set_content(self, new_content):
        self._content = new_content
        self._updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Polymorphism: different display format for notes
    def display(self):
        preview = self._content[:50] + "..." if len(self._content) > 50 else self._content
        print(f"--- Note Entry ---")
        print(f"  Title:    {self._title}")
        print(f"  Content:  {preview}")
        print(f"  Category: {self._category}")
        print(f"  Created:  {self._created_at}")

    def to_dict(self):
        return {
            "type": "note",
            "title": self._title,
            "content": self._content,
            "category": self._category,
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }


# ========== Quick Test ==========
if __name__ == "__main__":
    # Test LoginEntry
    login = LoginEntry("GitHub", "john123", "myP@ss!", "https://github.com")
    login.display()
    print()

    # Test CardEntry
    card = CardEntry("My Visa", "4111222233334444", "12/27", "123")
    card.display()
    print()

    # Test NoteEntry
    note = NoteEntry("WiFi Password", "Home network password is: wifi_2024_secure")
    note.display()
    print()

    # Test polymorphism: same method, different behaviour
    print("=== Polymorphism Demo ===")
    entries = [login, card, note]
    for entry in entries:
        print(entry)  # calls __str__ from base class