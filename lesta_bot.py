import sys
import os
import asyncio

print(">>> [СТАРТ] Запуск координатного кликера по 30 дням...", flush=True)

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ОШИБКА: Playwright не найден в этом Python.")
    sys.exit(1)

USER_DATA_DIR = os.path.abspath("./lesta_profile")
CALENDAR_URL = "https://tanki.su/ru/daily-check-in/"

async def main():
    p = await async_playwright().start()
    
    # Задаем фиксированное разрешение, чтобы координаты всегда попадали в цель
    browser = await p.firefox.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=True,
        viewport={"width": 1280, "height": 900}
    )

    page = browser.pages[0] if browser.pages else await browser.new_page()
    print(f">>> Заходим на {CALENDAR_URL}...", flush=True)
    await page.goto(CALENDAR_URL, wait_until="domcontentloaded")

    print(">>> Ожидаем прогрузку наград (7 секунд)...", flush=True)
    await page.wait_for_timeout(7000)

    # 1. Прокручиваем страницу в исходное положение к шапке календаря
    print(">>> Выставляем страницу на стартовую позицию...", flush=True)
    await page.evaluate("window.scrollTo(0, 220);")
    await page.wait_for_timeout(1500)

    # 2. Геометрия сетки 7x5 (30 дней) для окна 1280px
    # Центр первого ряда колонок:
    # 7 колонок распределены симметрично вокруг центра экрана (X=640)
    col_x = [360, 455, 550, 640, 735, 830, 925]
    
    # 5 рядов по вертикали с шагом между карточками:
    row_y = [230, 370, 510, 650, 790]

    print(">>> Начинаем прокликивание ВСЕХ 30 дней по координатам...", flush=True)
    
    day_num = 1
    for r_idx, y in enumerate(row_y):
        # На 4 и 5 рядах делаем дополнительный небольшой доскролл, чтобы они были видны
        if r_idx == 3:
            await page.evaluate("window.scrollBy(0, 250);")
            await page.wait_for_timeout(800)
            y -= 250
        elif r_idx == 4:
            y -= 250

        for x in col_x:
            if day_num > 30:
                break
            
            # Кликаем физической мышкой в центр карточки дня
            await page.mouse.click(x, y)
            print(f">>> День {day_num:02d}: клик в координаты (X={x}, Y={y})", flush=True)
            await page.wait_for_timeout(200) # микропауза между кликами
            day_num += 1

    print(">>> Все 30 дней успешно прокликаны физической мышкой!", flush=True)
    await page.wait_for_timeout(3000)

    await browser.close()
    await p.stop()
    print(">>> Готово! Скрипт закрыт.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())