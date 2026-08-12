"""Playwright автоматизация регистрации на atomicmail.io.

Регистрация — 4 шага:
  1. Имя + фамилия
  2. Юзернейм (email адрес)
  3. Пароль + подтверждение
  4. Seed phrase → Download & Proceed → CAPTCHA (ручное решение)

Режим полуавтомат: браузер видимый, пользователь решает hCaptcha руками.
"""

from __future__ import annotations

import asyncio
import glob
import os
import re

from playwright.async_api import BrowserContext, Page, TimeoutError as PWTimeout

from utils import random_first_name, random_last_name, random_username

SIGNUP_URL = "https://atomicmail.io/app/auth/sign-up"

# Авто-поиск chromium среди установленных Playwright браузеров
_MS_PLAYWRIGHT = os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "ms-playwright"
)


def find_chromium() -> str | None:
    """Найти chrome.exe среди установленных версий chromium-XXXX."""
    pattern = os.path.join(_MS_PLAYWRIGHT, "chromium-*", "chrome-win64", "chrome.exe")
    paths = sorted(glob.glob(pattern), reverse=True)
    return paths[0] if paths else None


CHROMIUM_PATH = find_chromium()


async def _fill_step1(page: Page) -> tuple[str, str]:
    """Шаг 1: имя + фамилия."""
    first = random_first_name()
    last = random_last_name()
    await page.fill("input[placeholder='e.g. Alfred']", first)
    await page.fill("input[placeholder*='Hitchcock']", last)
    await page.click("button[type=submit]")
    return first, last


async def _fill_step2(page: Page, first: str, last: str) -> str:
    """Шаг 2: юзернейм. Повторяет при занятом имени."""
    for _ in range(5):
        username = random_username(first, last)
        await page.fill("input[placeholder='e.g. alfie.hitchcock']", username)
        await page.click("button[type=submit]")
        # Ждём либо перехода на шаг пароля, либо ошибку
        try:
            await page.wait_for_selector(
                "input[type=password]", timeout=5000
            )
            return username
        except PWTimeout:
            # Возможно ошибка «занято» — пробуем другой username
            body = await page.inner_text("body")
            if "password" not in body.lower():
                continue
            return username
    raise RuntimeError("Не удалось подобрать свободный username за 5 попыток")


async def _fill_step3(page: Page, password: str) -> None:
    """Шаг 3: пароль + подтверждение."""
    fields = await page.query_selector_all("input[type=password]")
    await fields[0].fill(password)
    await fields[1].fill(password)
    await page.click("button[type=submit]")


async def _extract_seed(page: Page) -> list[str]:
    """Шаг 4: извлечь 12 слов seed phrase."""
    body = await page.inner_text("body")
    # Формат: «01\n\nслово\n\n02\n\nслово ...»
    words = re.findall(r"\b\d{2}\s+([a-z]+)\b", body)
    if len(words) >= 12:
        return words[:12]
    # Запасной вариант: ищем слова после номеров
    nums_words = re.findall(r"(\d{2})\s+([a-z]+)", body)
    return [w for _, w in nums_words[:12]]


async def _wait_captcha_solved(page: Page, timeout: int = 300) -> bool:
    """Ждать ручного решения CAPTCHA.

    После «Download & Proceed» появляется hCaptcha.
    Регистрация завершена когда URL меняется c /auth/sign-up.
    timeout в секундах (по умолчанию 5 минут на ручное решение).
    """
    print("  ⚠ Решите CAPTCHA в окне браузера...")
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        url = page.url
        # Регистрация завершена — редирект на /app/auth/welcome
        # (или любой URL вне /auth/sign-up)
        if "/auth/sign-up" not in url:
            return True
        await asyncio.sleep(1)
    return False


async def register_account(
    context: BrowserContext, password: str
) -> dict | None:
    """Полный цикл регистрации одного аккаунта.

    Возвращает dict:
      {username, email, password, seed: [слово,...]}
    или None при ошибке.
    """
    page = await context.new_page()
    try:
        await page.goto(SIGNUP_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(1)

        # Шаг 1
        first, last = await _fill_step1(page)
        await asyncio.sleep(3)

        # Шаг 2
        username = await _fill_step2(page, first, last)
        await asyncio.sleep(3)

        # Шаг 3
        await _fill_step3(page, password)
        await asyncio.sleep(5)

        # Шаг 4: seed phrase
        seed = await _extract_seed(page)
        # Кнопка «Download & Proceed» — это button[type=submit]
        await page.click("button[type=submit]")

        # Ждать ручного решения CAPTCHA
        solved = await _wait_captcha_solved(page, timeout=300)
        if not solved:
            print("  ✗ CAPTCHA не решена за отведённое время")
            return None

        return {
            "username": username,
            "email": f"{username}@atomicmail.io",
            "password": password,
            "seed": seed,
        }
    except Exception as e:
        print(f"  ✗ Ошибка регистрации: {e}")
        return None
    finally:
        await page.close()
