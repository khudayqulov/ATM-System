"""Bankomat menyusi, login va JSON faylga saqlash."""

import json
import os
from getpass import getpass
from pathlib import Path
import secrets
import tempfile

from account import Account


def format_money(amount: int) -> str:
    """Misol: 1250000 -> '1 250 000 soʻm'."""
    return f"{amount:,}".replace(",", " ") + " so'm"


class ATM:
    """Hisoblarni boshqarish va foydalanuvchi bilan ishlash."""

    def __init__(self, data_file: str | Path | None = None):
        self.data_file = Path(data_file) if data_file else Path(__file__).resolve().parent / "data" / "accounts.json"
        self.accounts: dict[str, Account] = {}
        self._load()

    def _load(self) -> None:
        if not self.data_file.exists():
            return

        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            for item in data["accounts"]:
                account = Account.from_dict(item)
                if account.card_number in self.accounts:
                    raise ValueError("Takroriy karta raqami topildi.")
                self.accounts[account.card_number] = account
        except (OSError, ValueError, KeyError, TypeError) as error:
            # Eski hisoblar yo'qolmasligi uchun buzilgan fayl ustidan yozmaymiz.
            raise RuntimeError(f"Hisoblar faylini o'qib bo'lmadi: {self.data_file} ({error})") from error

    def _save(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        content = {"accounts": [account.to_dict() for account in self.accounts.values()]}
        temp_name = None

        try:
            # Avval yangi faylga yozib, keyin asl faylni almashtiramiz.
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.data_file.parent,
                prefix=".atm_", suffix=".tmp", delete=False
            ) as temp:
                temp_name = temp.name
                json.dump(content, temp, ensure_ascii=False, indent=4)
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(temp_name, self.data_file)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def _luhn_check_digit(number_15: str) -> str:
        """Test uchun yaratilgan 15 raqamdan nazorat raqamini topadi."""
        total = 0
        for i, char in enumerate(reversed(number_15)):
            digit = int(char)
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return str((-total) % 10)

    def _new_card_number(self) -> str:
        # 9999 prefiksi — haqiqiy bank kartasi emas, faqat ta'limiy ID.
        while True:
            base = "9999" + "".join(str(secrets.randbelow(10)) for _ in range(11))
            card_number = base + self._luhn_check_digit(base)
            if card_number not in self.accounts:
                return card_number

    @staticmethod
    def _read_amount() -> int:
        raw = input("Summani kiriting (so'm): ").strip()
        if not raw or not all("0" <= c <= "9" for c in raw):
            raise ValueError("Faqat musbat butun son kiriting (masalan, 50000).")
        amount = int(raw)
        if amount <= 0:
            raise ValueError("Summa 0 dan katta bo'lishi kerak.")
        return amount

    def _register(self) -> None:
        print("\n--- YANGI HISOB ---")
        name = input("Ism va familiya: ").strip()
        if len(name) < 2:
            print("❌ Ism va familiya kamida 2 ta belgidan iborat bo'lishi kerak.")
            return

        pin = getpass("4 xonali PIN-kod: ")
        if not Account.valid_pin(pin):
            print("❌ PIN-kod aynan 4 ta raqamdan iborat bo'lishi kerak.")
            return
        confirm_pin = getpass("PIN-kodni takrorlang: ")
        if pin != confirm_pin:
            print("❌ PIN-kodlar mos kelmadi.")
            return

        card = self._new_card_number()
        account = Account.create(card, name, pin)
        self.accounts[card] = account
        try:
            self._save()
        except OSError as error:
            del self.accounts[card]
            print(f"❌ Hisobni saqlab bo'lmadi: {error}")
            return

        print("✅ Hisob yaratildi!")
        print(f"👤 Egasi: {name}")
        print(f"💳 Karta raqamingiz: {card}")
        print("ℹ️ Keyin kirish uchun ushbu TEST karta raqamini saqlang.")

    def _login(self) -> None:
        print("\n--- TIZIMGA KIRISH ---")
        card = input("Karta raqami (16 ta raqam): ").strip().replace(" ", "")
        if len(card) != 16 or not all("0" <= c <= "9" for c in card):
            print("❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak.")
            return

        for attempt in range(1, 4):
            pin = getpass("PIN-kod: ")
            account = self.accounts.get(card)
            if account is not None and account.verify_pin(pin):
                print(f"\n✅ Xush kelibsiz, {account.owner_name}!")
                self._account_menu(account)
                return
            print(f"❌ Karta raqami yoki PIN noto'g'ri. Qolgan urinish: {3 - attempt}")

        print("⚠️ 3 ta noto'g'ri urinish. Bosh menyuga qaytildi.")

    def _account_menu(self, account: Account) -> None:
        while True:
            print("\n========== HISOB MENYUSI ==========")
            print("1. Balansni tekshirish")
            print("2. Pul kiritish (Deposit)")
            print("3. Pul yechish (Withdraw)")
            print("4. Tranzaksiyalar tarixi")
            print("0. Hisobdan chiqish")
            choice = input("Tanlang: ").strip()

            if choice == "1":
                print(f"💰 Joriy balans: {format_money(account.balance)}")
            elif choice in ("2", "3"):
                try:
                    amount = self._read_amount()
                    # Saqlash ishlamasa foydalanuvchi balansini qayta tiklaymiz.
                    snapshot = account.to_dict()
                    if choice == "2":
                        account.deposit(amount)
                    else:
                        account.withdraw(amount)
                    try:
                        self._save()
                    except OSError as error:
                        self.accounts[account.card_number] = Account.from_dict(snapshot)
                        print(f"❌ Tranzaksiya saqlanmadi, amal bekor qilindi: {error}")
                        return  # Eski obyektga qayta murojaat qilmaslik uchun menyudan chiqamiz.
                    operation = "kiritildi" if choice == "2" else "yechildi"
                    print(f"✅ {format_money(amount)} muvaffaqiyatli {operation}.")
                    print(f"💰 Yangi balans: {format_money(account.balance)}")
                except ValueError as error:
                    print(f"❌ {error}")
            elif choice == "4":
                self._show_transactions(account)
            elif choice == "0":
                print("🔒 Hisobdan xavfsiz chiqildi.")
                return
            else:
                print("❌ Noto'g'ri tanlov. 0 dan 4 gacha son kiriting.")

    @staticmethod
    def _show_transactions(account: Account) -> None:
        if not account.transactions:
            print("📭 Tranzaksiyalar tarixi hozircha bo'sh.")
            return
        print("\n--- TRANZAKSIYALAR TARIXI ---")
        for index, item in enumerate(account.transactions, start=1):
            sign = "+" if item.kind == "deposit" else "-"
            print(f"{index}. {item.created_at} | {item.description}: {sign}{format_money(item.amount)}")

    def run(self) -> None:
        print("🏦 ATM — BANKOMAT BOSHQARUV TIZIMI")
        print("Bu haqiqiy bank emas, o'quv dasturidir.")
        while True:
            print("\n========== BOSH MENYU ==========")
            print("1. Yangi hisob yaratish")
            print("2. Tizimga kirish")
            print("0. Dasturdan chiqish")
            choice = input("Tanlang: ").strip()

            if choice == "1":
                self._register()
            elif choice == "2":
                self._login()
            elif choice == "0":
                print("👋 Dasturdan chiqildi. Xayr!")
                break
            else:
                print("❌ Noto'g'ri tanlov. 0, 1 yoki 2 ni kiriting.")
