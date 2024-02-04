import toloka.client as toloka
from config import config


def toloka_reject(ass_id: str, reject_comment: str, client) -> bool:
    try:
        client.reject_assignment(assignment_id=ass_id, public_comment=reject_comment)
        return True
    except Exception as e:
        print('reject error', ass_id)
        print(e)
        return False


def do_pool(pool, client):
    print('чтение всех сабмитов, пул', pool)
    assignments = client.get_assignments(pool_id=pool, batch_size=1000)
    unchecked, rejected = 0, 0
    for ass in assignments:
        status = ass.status.value

        # смотрим только непроверенные
        if status in ('SUBMITTED',):
            output = ass.solutions[0].output_values
            age = output.get('age')
            gender = output.get('gender')
            country = client.get_user(ass.user_id).country
            try:
                # woman 60
                if pool == '42740441':
                    if int(age) < 55 or gender == 'male':
                        toloka_reject(ass_id=ass.id, reject_comment='The task is only for 60+ years women', client=client)
                        print(f'reject {ass.id} {country} {gender} {age}')
                        rejected += 1
                    # если не отклонено
                    else:
                        unchecked += 1

                # kids
                elif pool == '42740443':
                    if int(age) > 15:
                        toloka_reject(ass_id=ass.id, reject_comment='The task is only for kids 15 years old or below', client=client)
                        print(f'reject {ass.id} {country} {gender} {age}')
                        rejected += 1
                    # если не отклонено
                    else:
                        unchecked += 1
            except Exception as e:
                print(ass.id, 'error', e)
                unchecked += 1
                continue
    output = f'\nПул {pool}\nотклонено {rejected}\nосталось {unchecked}\n'
    return output


def main():
    # толока
    toloka_client = toloka.TolokaClient(token=config.td5, environment='PRODUCTION')
    pools = [
        '42740441',  # woman 60+
        '42740443',  # kids
    ]
    result = ''
    for i in pools:
        result += do_pool(pool=i, client=toloka_client)
    return result

