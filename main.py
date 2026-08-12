#!/usr/bin/env python3
"""Генератор аккаунтов atomicmail.io.

Режим полуавтомат: браузер видимый, скрипт заполняет форму,
пользователь решает hCaptcha вручную.

Использование:
    python main.py -n 10 -p MyPass123!
    python main.py --count 5 --password "P@ssw0rd!" --output mails.txt
"""

import argparse
import asyncio
import sys

from generator import generate
from utils import random_password


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генератор аккаунтов atomicmail.io (полуавтомат)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            '  python main.py -n 10 -p "MyStr0ng!Pass"\n'
            '  python main.py -n 5 --output my_accounts.txt\n'
        ),
    )
    parser.add_argument(
        "-n", "--count", type=int, required=True,
        help="Количество аккаунтов для генерации",
    )
    parser.add_argument(
        "-p", "--password", type=str, default=None,
        help="Пароль для всех аккаунтов (если не указан — генерируется)",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="accounts.txt",
        help="Файл для сохранения в формате mail:pass (по умолчанию accounts.txt)",
    )
    parser.add_argument(
        "-s", "--seeds", type=str, default="seeds.txt",
        help="Файл для сохранения seed-фраз (по умолчанию seeds.txt)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.count <= 0:
        print("Ошибка: количество должно быть больше 0", file=sys.stderr)
        sys.exit(1)

    password = args.password or random_password()

    print("=" * 50)
    print("  AtomicMail.io генератор аккаунтов")
    print("=" * 50)
    print(f"  Количество:  {args.count}")
    print(f"  Пароль:      {password}")
    print(f"  Аккаунты:    {args.output}")
    print(f"  Seed-фразы:  {args.seeds}")
    print("=" * 50)
    print()
    print("  ⚠ Режим полуавтомат:")
    print("  Скрипт заполнит форму автоматически.")
    print("  На шаге CAPTCHA — решите её вручную в окне браузера.")
    print("  После решения регистрация завершится автоматически.")
    print()

    try:
        success, failed = asyncio.run(
            generate(args.count, password, args.output, args.seeds)
        )
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем.")
        sys.exit(130)

    print("\n" + "=" * 50)
    print(f"  Готово! Успешно: {success} | Неудачно: {failed}")
    print(f"  Аккаунты сохранены в: {args.output}")
    print(f"  Seed-фразы в:        {args.seeds}")
    print("=" * 50)


if __name__ == "__main__":
    main()
