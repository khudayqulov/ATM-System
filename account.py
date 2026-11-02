"""Bank hisobining OOP modeli va uning amallari."""

import hashlib
import hmac
import secrets

from transaction import Transaction


class Account:
    """PIN va balansni inkapsulyatsiya qiluvchi bank hisobi."""

    _PIN_ITERATIONS = 200_000

    def __init__(
        self,
        card_number: str,
        owner_name: str,
        pin_salt: str,
        pin_hash: str,
        balance: int = 0,
        transactions: list[Transaction] | None = None,
    ):
        if type(balance) is not int or balance < 0:
            raise ValueError("Hisob balansi manfiy bo'lishi mumkin emas.")
        self.card_number = card_number
        self.owner_name = owner_name
        self.__pin_salt = pin_salt
        self.__pin_hash = pin_hash
        self.__balance = balance
        self.__transactions = list(transactions) if transactions is not None else []

    @staticmethod
    def valid_pin(pin: str) -> bool:
        return len(pin) == 4 and all("0" <= c <= "9" for c in pin)

    @classmethod
    def create(cls, card_number: str, owner_name: str, pin: str) -> "Account":
        if not cls.valid_pin(pin):
            raise ValueError("PIN-kod aynan 4 ta raqamdan iborat bo'lishi kerak.")

        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, cls._PIN_ITERATIONS)
        return cls(card_number, owner_name, salt.hex(), digest.hex())

    def verify_pin(self, pin: str) -> bool:
        if not self.valid_pin(pin):
            return False
        expected = hashlib.pbkdf2_hmac(
            "sha256", pin.encode("utf-8"), bytes.fromhex(self.__pin_salt), self._PIN_ITERATIONS
        )
        return hmac.compare_digest(expected, bytes.fromhex(self.__pin_hash))

    @property
    def balance(self) -> int:
        return self.__balance

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self.__transactions)

    @staticmethod
    def _validate_amount(amount: int) -> None:
        if type(amount) is not int or amount <= 0:
            raise ValueError("Summa 0 dan katta butun son bo'lishi kerak.")

    def deposit(self, amount: int) -> None:
        self._validate_amount(amount)
        self.__balance += amount
        self.__transactions.append(Transaction("deposit", amount))

    def withdraw(self, amount: int) -> None:
        self._validate_amount(amount)
        if amount > self.__balance:
            raise ValueError("Balansda yetarli mablag' yo'q.")
        self.__balance -= amount
        self.__transactions.append(Transaction("withdraw", amount))

    def to_dict(self) -> dict:
        return {
            "card_number": self.card_number,
            "owner_name": self.owner_name,
            "pin_salt": self.__pin_salt,
            "pin_hash": self.__pin_hash,
            "balance": self.__balance,
            "transactions": [t.to_dict() for t in self.__transactions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        return cls(
            card_number=data["card_number"],
            owner_name=data["owner_name"],
            pin_salt=data["pin_salt"],
            pin_hash=data["pin_hash"],
            balance=data["balance"],
            transactions=[Transaction.from_dict(t) for t in data["transactions"]],
        )
