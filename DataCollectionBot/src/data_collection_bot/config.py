import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")

PARAMETERS_TABLE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parameters.xlsx')
)

DATA_TABLE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'data.xlsx')
)

ADMIN_INVITE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'admin_invite.txt')
)

DISK_PATH = "/app/data.xlsx"