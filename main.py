"""ATM loyihasini ishga tushiruvchi asosiy fayl."""

from atm import ATM


def main() -> None:
    try:
        atm = ATM()
        atm.run()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Dastur to'xtatildi.")
    except (OSError, RuntimeError) as error:
        print(f"❌ Xatolik: {error}")


if __name__ == "__main__":
    main()
