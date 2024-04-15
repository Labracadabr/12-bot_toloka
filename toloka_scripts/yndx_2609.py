import requests
from pprint import pprint
import json
import os
from config import config

# толока или яндекс: закомментить одно из двух
api_url = 'https://tasks.yandex.ru/api/v1/'
# api_url = 'https://platform.toloka.ai/api/v1/'

# подключение
headers = {'Authorization': f'OAuth {config.yaz}'}
session = requests.Session()

# отклонить задание
def toloka_reject(ass_id: str, reject_comment: str) -> bool:
    try:
        # текст авто отказа начинается на tag
        tag = '~'
        reject_comment = reject_comment if tag in reject_comment else tag + reject_comment
        url = f"{api_url}assignments/{ass_id}"
        print(url)
        payload = {
            "status": "REJECTED",
            "public_comment": f"{reject_comment}"
        }

        result = session.patch(url, headers=headers, json=payload)
        print(result.status_code)
        if result.ok:
            return True
        else:
            pprint(result.json())
            exit(f'Ошибка запроса, код {result.status_code}')
    except Exception as e:
        print('reject error', ass_id)
        print(e)
        return False


# проверить файлы из задания
def read_assignment(assignment: dict, ):
    # прочитать аутпут задания
    try:
        output_data: dict = assignment['solutions'][0]['output_values']

        # id задания
        ass_id = assignment.get('id')
        print(f'\nid {assignment.get("id")} прислано {assignment.get("submitted")}')
        pprint(output_data)

        # проверить возраст
        age = output_data.get('age')
        if int(age) > 15:
            toloka_reject(ass_id=ass_id, reject_comment='Задание только для детей до 15 лет')
            print(f'reject {ass_id} {age}')
            return False
        return True

    except Exception as e:
        print('error', e)
        return True


# перебор заданий
def read_pool(pool, ):
    rejected = 0
    unchecked = 0

    # запрос
    assignments_url = f'{api_url}assignments?pool_id={pool}&limit=100000'
    print('assignments_url', assignments_url)
    response = session.get(assignments_url, headers=headers)

    # ответ
    if not response.ok:
        pprint(response.json())
        exit(f'Ошибка запроса, код {response.status_code}')

    assignments = json.loads(response.content).get('items')
    print('найдено заданий:', len(assignments))
    # pprint(assignments)

    for ass in assignments:
        # смотрим только не проверенные
        status = ass.get('status')
        # print(f'{status = }')
        # if status in ('REJECTED',):
        if status in ('SUBMITTED',):
            res = read_assignment(assignment=ass, )
            if res:
                unchecked += 1
            else:
                rejected += 1

    output = f'\nПул {pool}\nотклонено {rejected}\nосталось {unchecked}\n'
    return output


if __name__ == '__main__':

    read_pool(pool='1763442')

