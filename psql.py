import psycopg2
from functools import wraps
from config import config
table = 'car_data'


# postgres декоратор для обработки ошибок, открытия и закрытия коннекта
def postgres_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # подключение к БД
        conn = psycopg2.connect(host=config.host, dbname=config.dbname, user=config.user, password=config.password)
        conn.autocommit = True
        # исполнение sql запроса
        try:
            with conn.cursor() as cursor:
                result = func(cursor, *args, **kwargs)
                return result
        except Exception as e:
            print("[INFO] Postgres Error:", e)
        # закрытие
        finally:
            conn.close() if conn else None
    return wrapper


@postgres_decorator
def top_countries(cursor, num: int) -> list:
    query = f'''SELECT country, COUNT(*) AS count
            FROM {table}
            GROUP BY country
            ORDER BY count DESC
            LIMIT {num};'''

    cursor.execute(query)
    top = cursor.fetchall()
    return top


# убрать дубликаты
@postgres_decorator
def rm_duplicates(cursor):
    print('removing duplicates')
    query = f"""
        DELETE FROM {table}
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id,
                       ROW_NUMBER() OVER (PARTITION BY image_link ORDER BY id) AS rnum
                FROM {table}
            ) t
            WHERE t.rnum > 1
        );
    """
    cursor.execute(query)
    print('removed')
