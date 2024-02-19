import requests
from pprint import pprint
import json
import os
from config import config
import re


def check_html(project_url: str) -> str:
    result = ''
    try:
        if 'yandex' in project_url:
            api_url = 'https://tasks.yandex.ru/api/v1/projects/'
            token = config.yaz
        else:
            api_url = 'https://platform.toloka.ai/api/v1/projects/'
            token = config.td
        project_id = project_url.split('/')[-1]
        api_url += project_id

        # запрос
        print('request', api_url)
        headers = {'Authorization': f'OAuth {token}'}
        response = requests.get(url=api_url, headers=headers)

        # ответ
        if not response.ok:
            pprint(response.json())
            raise AssertionError(f'Ошибка запроса, код {response.status_code}')
        print('response status_code', response.status_code, '\n')
        task_spec = response.json().get('task_spec')

        project_name = response.json().get('public_name')
        result += f'Проект: {project_name}\n'

        # output_data
        output_data = task_spec.get('output_spec')
        output_names = set(output_data.keys())

        # HTML
        html = task_spec.get('view_spec').get('markup')
        pattern = r'name="([^"]+)"'
        html_names = set(re.findall(pattern, html))

        # разница множеств
        # html_not_output = output_names - html_names
        html_not_output = html_names - output_names
        result += f'\nHTML: {len(html_names)} полей.\nЕсть в HTML, но нет в output_data: {len(html_not_output)} полей\n'
        for i, field in enumerate(html_not_output, start=1):
            result += f'{i}. {field}\n'

        # output_not_html = html_names - output_names
        output_not_html = output_names - html_names
        result += f'\nOutput data: {len(output_data)} полей.\nЕсть в output_data, но нет в HTML: {len(output_not_html)} полей\n'
        for i, field in enumerate(output_not_html, start=1):
            result += f'{i}. {field}\n'

    except Exception as e:  # прочие ошибки
        result += f'\nОшибка {repr(e)}\n'

    finally:
        return result
