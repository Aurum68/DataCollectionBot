import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
MYSQL_USERNAME=os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD=os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_PORT=os.getenv("MYSQL_PORT")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE")
ADMIN_TELEGRAM_ID = [int(i) for i in os.getenv("ADMIN_TELEGRAM_ID").split(',') if i.strip()]
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

HOUR = 17
MINUTE = 50