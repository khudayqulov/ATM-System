"""Bank hisobidagi bitta amal (tranzaksiya) modeli."""

from datetime import datetime


class Transaction:
    """Pul kiritish yoki yechish haqidagi ma'lumotni saqlaydi."""

    TYPES = {
        "deposit": "Pul kiritildi",
        "withdraw": "Pul yechildi",
    }

    def __init__(self, kind: str, amount: int, created_at: str | None = None):
        if kind not in self.TYPES:
            raise ValueError("Noma'lum tranzaksiya turi.")
        if type(amount) is not int or amount <= 0:
            raise ValueError("Tranzaksiya summasi musbat butun son bo'lishi kerak.")

        self.kind = kind
        self.amount = amount
        self.created_at = created_at or datetime.now().astimezone().isoformat(timespec="seconds")

    @property
    def description(self) -> str:
        return self.TYPES[self.kind]

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "amount": self.amount,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            kind=data["kind"],
            amount=data["amount"],
            created_at=data["created_at"],
        )
