import textwrap
import time
import typing as tp
import string
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
        all_count = 0,
        params = """ + str(params_) + """,
        response;
    
    if (params.count == 0){
        params.count = 100;
        response = API.wall.get(params);
        all_count = response.count;
        items = items + response.items;
        calls = calls + 1;
    }else{
        all_count = params.count;
        if (params.count >= 100){
            params.count = 100;
        }        
    }
    var max_calls = """ + str(max_count) + """ / 100; 
    while(calls < max_calls && all_count > params.offset) {

        calls = calls + 1;  

        response = API.wall.get(params);
        items = items + response.items;
        params.offset = params.offset + params.count;
    };
    return {
        all_count: all_count,
        items: items
     };"""

    params = {
        "code": code,
        "access_token": config.VK_CONFIG['access_token'],
        "v": "5.126"
    }
    r = {"items": [],
         "all_count": 1}

    with progress(total=r["all_count"]) as pbar:
        while len(r['items']) < r["all_count"]:
            j = session.post(
                url="execute",
                data=params
            ).json()

            time.sleep(1)

            try:
                r["items"] += j["response"]["items"]
                r["all_count"] = j["response"]["all_count"]
            except KeyError:
                raise APIError(j["error"])

            params["count"] = r["all_count"]
            pbar.total = r["all_count"]
            pbar.update(len(r["items"]) - params_["offset"])
            params_["offset"] = len(r["items"])

    # texts = []
    # for i in r["items"]:
    #     text = i["text"]
    #     text = re.sub(r'[^\w\s]', '', text)
    #     emoji_pattern = re.compile("["
    #                                u"\U0001F600-\U0001F64F"  # emoticons
    #                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    #                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
    #                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    #                                "]+", flags=re.UNICODE)
    #     text = emoji_pattern.sub(r'', text)
    #     text = re.sub(r'http\S+', '', text)
    #     texts.append(text)
    return pd.DataFrame(r)


if __name__ == "__main__":
    wall_ = get_wall_execute(domain="cs102py", count=1)
    print(wall_)
