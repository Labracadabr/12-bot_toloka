import toloka.client as toloka
from config import config


def toloka_reject(ass_id: str, public_comment, client) -> bool:
    try:
        client.reject_assignment(assignment_id=ass_id, public_comment=public_comment)
        return True
    except Exception as e:
        print('reject error', ass_id)
        print(e)
        return False

def do_pool(pool, client):
    rejected, unchecked = 0, 0
    print('чтение всех заданий')
    assignments = client.get_assignments(pool_id=pool, batch_size=10000)
    for ass in assignments:
        status = ass.status.value
        # print(status)

        # смотрим только непроверенные
        if status in 'SUBMITTED':
            try:
                # считаем затраченное время
                time_spent = ass.submitted - ass.created
                sec_spent = time_spent.total_seconds()
                # print(sec_spent)

                # отклонить, если мало времени
                if sec_spent < 250:
                    toloka_reject(ass_id=ass.id, public_comment='Not by instruction', client=client)
                    print(f'reject {ass.id}, {sec_spent} sec')
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
    pools = ['42755635']  # Selfie+ID

    result = ''
    for i in pools:
        result += do_pool(pool=i, client=toloka_client)
    return result
