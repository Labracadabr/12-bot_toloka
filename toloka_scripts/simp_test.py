import os
import requests
import json
from config import config
from pprint import pprint

pool_params_exmpl = {'account': 'avito',
                     'device': 'pc',
                     'overlap': '250',
                     # 'tasks': [{'code': '250891', 'img_url': 'https://usabi.li/do/3610d86ca7e4/f4a3'},
                     #           {'code': '250891', 'img_url': 'https://usabi.li/do/887e72bf49db/c8e4'}],
                     'date': '2024-01-27',
                     'user_fullname': 'Dmitrii Minokin',
                     'user_id': 992863889,
                     'user_username': 'its_dmitrii'}

filter_map = {
    'pc': {
        "or": [
            {
                "category": "computed",
                "key": "device_category",
                "operator": "EQ",
                "value": "PERSONAL_COMPUTER"
            }
        ]
    },
    'mob': {
        "or": [
            {
                "category": "computed",
                "key": "device_category",
                "operator": "EQ",
                "value": "SMARTPHONE"
            }
        ]
    },
}
pool_filter = {
    "and": [
        {
            "or": [
                {
                    "category": "profile",
                    "key": "languages",
                    "operator": "IN",
                    "value": "RU"
                }
            ]
        },
        {
            "or": [
                {
                    "category": "computed",
                    "key": "region_by_phone",
                    "operator": "IN",
                    "value": 225  # RF
                }
            ]
        }
    ]
}


# toloka
async def start_test(pool_params: dict):
    print('создание')
    session = requests.Session()
    result = ''
    try:
        toloka_token = config.avi
        # url_api = "https://toloka.dev/api/v1"
        url_api = "https://tasks.yandex.ru/api/v1"
        headers = {"Authorization": "OAuth %s" % toloka_token, "Content-Type": "application/JSON"}

        # создать пул
        project_id = "2343"
        private_name = f"{pool_params['date']}_{pool_params['device']}_{pool_params['user_fullname']}"
        pool_data = {
            "project_id": project_id,
            "private_name": private_name,
            "will_expire": "2030-01-01T00:00:00.000Z",
            "may_contain_adult_content": False,
            "reward_per_assignment": 2,
            "assignment_max_duration_seconds": 1800,
            "auto_accept_solutions": True,
            "quality_control": {
                "configs": [
                    {
                        "collector_config": {
                            "type": "ANSWER_COUNT",
                            "uuid": "f6bf2ba0-dcd1-4a78-8e73-e6a66bd17d8c",
                            "parameters": {}
                        },
                        "rules": [
                            {
                                "conditions": [
                                    {
                                        "key": "assignments_accepted_count",
                                        "operator": "GTE",
                                        "value": 1
                                    }
                                ],
                                "action": {
                                    "type": "RESTRICTION_V2",
                                    "parameters": {
                                        "scope": "POOL",
                                        "duration_unit": "PERMANENT"
                                    }
                                }
                            },
                        ]
                    },
                    {
                        "collector_config": {
                            "type": "ANSWER_COUNT",
                            "uuid": "5eb8520b-121f-45df-95a3-c39a399242a3",
                            "parameters": {}
                        },
                        "rules": [
                            {
                                "conditions": [
                                    {
                                        "key": "assignments_accepted_count",
                                        "operator": "GT",
                                        "value": 0
                                    }
                                ],
                                "action": {
                                    "type": "RESTRICTION_V2",
                                    "parameters": {
                                        "duration": 1,
                                        "scope": "PROJECT",
                                        "duration_unit": "MINUTES"
                                    }
                                }
                            }
                        ]
                    }
                ]
            },
            "mixer_config": {
                "real_tasks_count": 1,
                "golden_tasks_count": 0,
                "training_tasks_count": 0,
                "force_last_assignment": True
            },
            "priority": 0,
            "owner": {
                "id": "44bf229a75ca9c797bc030e4ce49018a",
                "myself": True
            },
            "type": "REGULAR",
            "status": "CLOSED",
            "speed_quality_balance": {
                "percent": 80,
                "type": "TOP_PERCENTAGE_BY_QUALITY"
            },
            "defaults": {
                "default_overlap_for_new_task_suites": pool_params.get('overlap')
            },
        }
        r = session.post(url=url_api+"/pools", headers=headers, json=pool_data)
        pprint(r.json())
        assert r.ok
        pool_id = r.json()['id']
        # pool_link = f'https://platform.toloka.ai/requester/project/{project_id}/pool/{pool_id}'
        pool_link = f'https://tasks.yandex.ru/requester/project/{project_id}/pool/{pool_id}'
        result += f'Пул создан: {pool_link}\n'

        # загрузить задания
        for task in pool_params['tasks']:
            payload = {"pool_id": pool_id, "input_values": task['input_values'], "overlap": pool_params['overlap']}
            print('payload')
            pprint(payload)
            r = session.post(url=url_api + "/tasks", headers=headers, json=payload)
            assert r.ok
        result += f'Задания загружены: {len(pool_params["tasks"])} шт\n'

        # настроить фильтры
        device = pool_params.get('device')
        # gender = pool_params.get('gender')
        if device:
            pool_filter['and'].append(filter_map[device])
        # pool_data = session.get(f"{url_api}{pool_id}", headers=headers).json()
        pool_data['filter'] = pool_filter
        url = url_api + '/pools/' + pool_id
        r = session.put(url=url, headers=headers, json=pool_data)
        assert r.ok
        result += f'Фильтры настроены: {device}\n'

        # запустить пул
        r = session.post(url=url_api + '/pools/%s/open' % pool_id, headers=headers)
        assert r.ok
        result += f'Пул запущен\n'

    except AssertionError as e:  # если какой-либо запрос неудачный
        result += f'⚠️ Ошибка: {repr(e)}\n{r.json()}'
    except Exception as e:  # прочие ошибки
        result += f'🚫 Ошибка: {repr(e)}\n'

    finally:
        # print(result)
        return result
