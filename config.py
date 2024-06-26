from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    BOT_TOKEN: str = None   # телеграм бот
    td: str = None  # toloka
    td5: str = None  # toloka
    yaz: str = None  # я.задания
    avi: str = None  # я.задания


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    BOT_TOKEN=env('BOT_TOKEN'),
    td=env('td'),
    td5=env('td5'),
    yaz=env('yaz'),
    avi=env('avi'),
    )
