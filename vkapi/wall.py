import textwrap
import time
import typing as tp
import pymorphy2
import re

import pandas as pd
from pandas import json_normalize
from tqdm import tqdm

from vkapi import config, session
from vkapi.exceptions import APIError


def get_posts_2500(
        owner_id: str = "",
        domain: str = "",
        offset: int = 0,
        count: int = 10,
        max_count: int = 2500,
        filter: str = "owner",
        extended: int = 0,
        fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:
    pass


def get_wall_execute(
        owner_id: str = "",
        domain: str = "",
        offset: int = 0,
        count: int = 100,
        max_count: int = 2500,
        filter: str = "owner",
        extended: int = 0,
        fields: tp.Optional[tp.List[str]] = None,
        progress=tqdm,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """

    params_ = {
        "owner_id": owner_id,
        "domain": domain,
        "offset": offset,
        "count": count,
        "filter": filter,
        "extended": extended,
        "fields": ",".join(fields) if fields else '',
        "max_count": max_count,
    }

    code = """
    var calls = 0,
        items = [],
        records = 0,
        params = """ + str(params_) + """,
        response = {"count":"1"};
    
    if (params.count == 0){
        params.count = 100;
        response = API.wall.get(params);
        records = response.count;
        items = items + response.items;
        calls = calls + 1;
    }else{
        records = params.count;
        if (params.count >= 100){
            params.count = 100;
        }        
    }
    var max_calls = """ + str(max_count) + """ / 100; 
    while(calls < max_calls && records > params.offset) {

        calls = calls + 1;  

        response = API.wall.get(params);
        items = items + response.items;
        params.offset = params.offset + params.count;
    };
    return {
        count: records,
        items: items
     };"""

    params = {
        "code": code,
        "access_token": config.VK_CONFIG['access_token'],
        "v": "5.126"
    }
    r = {"items": [],
         "count": 1}

    with progress(total=r["count"]) as pbar:
        while len(r['items']) < r["count"]:
            j = session.post(
                url="execute",
                data=params
            ).json()

            time.sleep(1)

            try:
                r["items"] += j["response"]["items"]
                r["count"] = j["response"]["count"]
            except KeyError:
                raise APIError(j["error"])

            params["count"] = r["count"]
            pbar.total = r["count"]
            pbar.update(len(r["items"]) - params_["offset"])
            params_["offset"] = len(r["items"])

    return pd.DataFrame(r["items"])


if __name__ == "__main__":
    wall_ = get_wall_execute(domain="cs102py", count=1)
    print(wall_)
