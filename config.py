from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    BOT_TOKEN: str = None   # телеграм бот
    td: str = None  # toloka
    td5: str = None  # toloka
    yaz: str = None  # toloka
    avi: str = None  # toloka
    aws_id: str = None  # aws s3
    aws_sc: str = None  # aws s3

    host: str = None                # хост
    dbname: str = None              # имя базы данных
    user: str = None                # пользователь
    password: str = None            # пароль
    port: int = None                # порт


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    BOT_TOKEN=env('BOT_TOKEN'),
    td=env('td'),
    td5=env('td5'),
    yaz=env('yaz'),
    avi=env('avi'),
    aws_id=env('aws_id'),
    aws_sc=env('aws_sc'),
    host=env('host'),
    dbname=env('dbname'),
    user=env('user'),
    password=env('password'),
    port=env.int('port')
    )
