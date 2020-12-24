import datetime as dt
import statistics
import typing as tp

from vkapi.friends import get_friends


def calculate_age(born):
    today = dt.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    friends = get_friends(user_id, fields=["bdate"])
    ages = []
    for f in friends.items:
        try:
            bdate = list(map(int, f['bdate'].split(".")))
            if len(bdate) < 3:
                continue
            else:
                ages.append(calculate_age(dt.date(day=bdate[0], month=bdate[1], year=bdate[2])))
        except (TypeError, KeyError) as e:
            continue
    return statistics.median(ages) if ages else None


if __name__ == "__main__":
    print(age_predict(146168589))
