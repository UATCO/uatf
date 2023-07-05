"""Универсальные функции для работы фреймворка"""

import time

from .config import Config
from .logfactory import log

config = Config()


def _wait(action, wait_time=True, log_msg=False):
    """Метод в качестве параметра получает функцию action

    Ждет wait_max время пока функция не вернет True
    Если не возвращает, то вернет в конце результат выполнения функции.

    :param action: действие которое ожиданем
    :param wait_time: время ожидания
    :param log_msg: выводить ли в лог сообщение
    """

    if wait_time is True:
        wait_element = config.get('WAIT_ELEMENT_LOAD', 'GENERAL')
        wait_time = wait_element
    end_time = time.time() + wait_time

    res = False
    while True:
        try:
            res = action()
            if res is not False:
                return res
            tmp_err = None
        except Exception as error:
            tmp_err = error
            if config.get('DEBUG', 'GENERAL'):
                log(tmp_err, "[d]")
        if time.time() > end_time:
            break
        time.sleep(0.1)

    if wait_time > 5 and log_msg:
        log("В WAIT заключено не работающее ожидание! Требуется исправить!", '[e]')
    if not res and tmp_err is None:
        return False
    else:
        return tmp_err