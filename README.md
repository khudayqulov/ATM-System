# 🏦 ATM System — Bankomat boshqaruv tizimi

Python 3 da **Object-Oriented Programming (OOP)** asosida yozilgan **o‘quv uchun bankomat simulyatori**.
Bu dastur haqiqiy bankka yoki to‘lov tizimiga ulanmaydi: barcha kartalar va pullar **virtual**.

## ⚙️ Imkoniyatlar

- Yangi hisob yaratish: ism, 4 xonali PIN va avtomatik yaratiladigan 16 xonali **test karta raqami**.
- Karta raqami va PIN bilan kirish (har safar ko‘pi bilan 3 urinish).
- Balansni tekshirish.
- Pul kiritish va pul yechish (so‘mda, faqat musbat butun summa).
- Sana, vaqt va summali tranzaksiyalar tarixini ko‘rish.
- Hisobdan va dasturdan chiqish.
- Ma’lumotlarni `data/accounts.json` faylida saqlash (dastur qayta ochilganda ham qoladi).

## 📁 Loyiha tuzilishi

```text
ATM_Project/
├── main.py          # Dastur boshlanishi
├── account.py       # Account klasi: PIN, balans, amallar
├── atm.py           # ATM klasi: menyu, login, faylga saqlash
├── transaction.py   # Transaction klasi: amallar tarixi
├── README.md
└── data/             # Birinchi hisob yaratilganda avtomatik hosil bo'ladi
    └── accounts.json
```

## ▶️ Ishga tushirish

1. Python **3.10 yoki undan yuqori** versiyasini o‘rnating.
2. Terminalda `ATM_Project` papkasiga kiring.
3. Buyruqni bajaring:

```bash
python main.py
```

Agar Windows da `python` ishlamasa, `py main.py` buyrug‘ini sinab ko‘ring.
**Hech qanday tashqi kutubxona o‘rnatish shart emas.**

## 🧪 Foydalanish namunasi

1. Bosh menyudan `1` ni tanlang.
2. Ism/familiya, 4 xonali PIN kiriting va PINni tasdiqlang.
3. Ekranda chiqadigan **test karta raqami**ni saqlab qo‘ying.
4. `2` ni tanlang va karta raqamingiz hamda PINingiz bilan kiring.
5. Hisob menyusidan balans, pul kiritish, pul yechish va tarixni tekshiring.
6. `0` bosib hisobdan chiqing. Bosh menyuda yana `0` bosib dasturni yoping.

**Muhim:** PIN terminalga kiritilganda odatda ko‘rinmaydi (`getpass` ishlatilgan).
Test kartalar `9999` prefiksi bilan yaratiladi. **Haqiqiy karta raqamingizni yoki haqiqiy PINingizni kiritmang.**

## 🧩 OOP tushunchalari

| Tushuncha | Loyihadagi misol |
| --- | --- |
| `class` | `Account`, `ATM`, `Transaction` |
| `__init__` | Har bir klassning konstruktori |
| Encapsulation | `Account.__balance`, `Account.__pin_hash` |
| `@property` | `Account.balance`, `Account.transactions` |
| Methods | `deposit()`, `withdraw()`, `verify_pin()`, `run()` |
| Lists | Tranzaksiyalar ro‘yxati |
| Dictionaries | `ATM.accounts`, JSON obyektlar |
| Conditional statements | Menyudagi `if / elif / else` |
| Loops | `while`, `for` |

PIN **ochiq matnda saqlanmaydi**: tasodifiy salt va PBKDF2-SHA256 bilan xeshlanadi. JSON fayl almashtirish orqali yoziladi, ammo bu **real bank uchun ishlab chiqarish darajasidagi xavfsizlik tizimi emas** — loyiha faqat ta’lim uchun mo‘ljallangan.
