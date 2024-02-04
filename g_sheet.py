import gspread
from gspread.exceptions import APIError

# GOOGLE API
# данные для подключения к таблице
service_file = 'google_token.json'
gc = gspread.service_account(filename=service_file)
sheet_url = 'https://docs.google.com/spreadsheets/d/1A-E-4OvnC1PSaB54TGoX4y0rn19HPJy9cpPy59fx0Xw/edit#gid=0'
spreadsheet = gc.open_by_url(sheet_url)

example_pool_params = {'account': 'avito',
         'date': '2024-01-29',
         'device': 'pc',
         'overlap': '300',
         'tasks': [{'input_values': {'code': '573', 'img_url': 'https://usabi.li/do/49e0d8d070c1/7439'}},
                   {'input_values': {'code': '574', 'img_url': 'https://usabi.li/do/49e0d8d070c1/7440'}}],
         'user_fullname': 'Dmitrii Minokin',
         'user_id': 992863889,
         'user_username': 'its_dmitrii'}


def g_sheet_report(pool_params: dict):
    tasks = pool_params.get('tasks')
    date = pool_params.get('date')
    for task in tasks:
        data = [date, task['input_values']['img_url']]  # дата,	ссылка
        google_append(page='tests', data=data)
    # res = f'Внесено в таблицу {sheet_url}'
    res = f'Внесено в  <a href="{sheet_url}">таблицу</a>'
    return res


# добавить строку в конец таблицы
def google_append(page: str, data: list):
    spreadsheet.worksheet(page).append_row(values=data)
    print(f'Внесено в лист {page}:')
    print(data)

