"""Оркестрация генерации аккаунтов: цикл регистрации + сохранение в файлы."""

from __future__ import annotations

import asyncio

from playwright.async_api import async_playwright

from browser import CHROMIUM_PATH, register_account


def _append_line(path: str, line: str) -> None:
    """Дописать строку в файл (создать если нет)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


async def generate(
    count: int,
    password: str,
    output: str = "accounts.txt",
    seeds_file: str = "seeds.txt",
) -> tuple[int, int]:
    """Сгенерировать count аккаунтов.

    Возвращает (успешно, неудачно).
    """
    success = 0
    failed = 0

    async with async_playwright() as p:
        launch_kwargs = {"headless": False}
        if CHROMIUM_PATH:
            launch_kwargs["executable_path"] = CHROMIUM_PATH

        browser = await p.chromium.launch(**launch_kwargs)

        try:
            for i in range(1, count + 1):
                print(f"\n{'='*50}")
                print(f"Аккаунт {i}/{count}")
                print(f"{'='*50}")

                # Свежий контекст на каждый аккаунт:
                # чистые куки + localStorage + сессия
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 900},
                    accept_downloads=True,
                )

                result = await register_account(context, password)

                # Полная очистка: куки, localStorage, кэш
                await context.clear_cookies()
                await context.close()

                if result:
                    # Сохранить mail:pass
                    _append_line(output, f"{result['email']}:{result['password']}")
                    # Сохранить seed фразу
                    if result["seed"]:
                        seed_str = " ".join(result["seed"])
                        _append_line(
                            seeds_file, f"{result['email']}:{seed_str}"
                        )
                    success += 1
                    print(f"  ✓ Готово: {result['email']}")
                else:
                    failed += 1
                    print(f"  ✗ Пропуск аккаунта {i}")

                # Пауза между регистрациями
                if i < count:
                    print("  Пауза 3 сек перед следующим...")
                    await asyncio.sleep(3)
        finally:
            await browser.close()

    return success, failed
