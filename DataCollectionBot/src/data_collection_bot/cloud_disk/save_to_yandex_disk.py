from src.data_collection_bot.config import YANDEX_TOKEN, DATA_TABLE_PATH
import yadisk


def upload_to_yandex_disk(local_path, disk_path):
    y = yadisk.YaDisk(token=YANDEX_TOKEN)
    y.upload(local_path, disk_path, overwrite=True)
    print("✅ Файл синхронизирован с Яндекс.Диском!")