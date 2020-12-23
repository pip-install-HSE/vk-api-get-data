import time
import typing as tp
import random

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Session(requests.Session):
    """
    Сессия.

    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        super().__init__()
        self.base_url = base_url + "/" if base_url[-1] != "/" else base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retries = Retry(total=max_retries,
                             backoff_factor=backoff_factor,
                             status_forcelist=(500, 502, 504, 404))
        self.mount(base_url, HTTPAdapter(max_retries=self.retries))

    # def exponential_backoff(func):
    #     def wrapper(self, url: str, *args: tp.Any, **kwargs: tp.Any):
    #         delay = self.timeout
    #         i, e = 0, None
    #         while i < self.max_retries:
    #             try:
    #                 res = func(self, url, *args, **kwargs)
    #             except Exception as ex:
    #                 e = ex
    #                 time.sleep(delay)
    #                 delay = delay * self.backoff_factor
    #                 delay = delay + delay * (random.randint(0, 10) / 10)
    #                 i += 1
    #             else:
    #                 return res
    #         raise e
    #     return wrapper

    # @exponential_backoff
    def get(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        url = self.base_url + url
        return super().get(url=url, *args, **kwargs)

    # @exponential_backoff
    def post(self, url: str, *args: tp.Any, **kwargs: tp.Any) -> requests.Response:
        url = self.base_url + url
        return super().post(url=url, *args, **kwargs)


if __name__ == "__main__":
    import config
    s = Session(config.VK_CONFIG["domain"])
    print(s.get(url=""))
