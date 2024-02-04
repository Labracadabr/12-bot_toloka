import os
import json

# tg канал для логов
log_channel_id = ''
# log_channel_id = '-1002006918299'

# Список id админов
dima = "992863889"
admins: list[str] = [dima]

# где хранятся данные
logs = 'logs.tsv'

def check_files():
    file_list = [logs]
    for file in file_list:
        if not os.path.isfile(file):
            if file.endswith('json'):
                with open(file, 'w', encoding='utf-8') as f:
                    print('Отсутствующий файл создан:', file)
                    print('{}', file=f)
            elif file.endswith('sv'):
                with open(file, 'w', encoding='utf-8') as f:
                    print('Отсутствующий файл создан:', file)
                    print('\t'.join(('Time', 'User', 'Action')), file=f)
