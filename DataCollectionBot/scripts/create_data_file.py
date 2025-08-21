import os
from openpyxl import Workbook

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data.xlsx")

# 1. Убедись, что папка существует
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# 2. Если файла нет И это не папка — СОЗДАТЬ пустой Excel файл
if not os.path.exists(DATA_FILE) or os.path.isdir(DATA_FILE):
    # Если папка ошибочно называется data.xlsx — удалить!
    if os.path.isdir(DATA_FILE):
        import shutil
        shutil.rmtree(DATA_FILE)
    wb = Workbook()
    sheet = wb.active
    sheet.title = 'init'
    wb.save(DATA_FILE)
    print(f"✅ Создан файл: {DATA_FILE}")
else:
    print(f"✅ Файл уже есть: {DATA_FILE}")