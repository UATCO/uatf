"""Универсальные функции для работы фреймворка"""
import os
import time
from pathlib import Path
from typing import Optional, Union, Tuple
from urllib import parse

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


class Aggregator:
    js_errors = []

    @classmethod
    def add_errors(cls, errors: Optional[list] = None):
        from .ui.browser import Browser
        if errors is None:
            errors = Browser().get_js_error()
        if errors:
            cls.js_errors.extend(errors)

    @classmethod
    def clear(cls):
        cls.js_errors = []


def save_artifact(file_path: str, data: Union[str, list, bytes], folder='file_report',
                  mode='w', encoding='utf-8', src: Optional[str] = None) -> Tuple[str, str]:
    """Сохранение артефакта

    :param file_path путь до файла / имя файла
    :param data данные для сохранения
    :param folder папка в которою сохранять
    :param mode режим сохранения
    :param encoding кодировка
    :param src путь относительно папки с тестами, нужен для обновления файлов через jc
    """

    folder_path = get_artifact_path(folder)
    file_path = os.path.join(folder_path, os.path.normpath(file_path))
    file_dir = os.path.dirname(file_path)

    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    # для hash объектов не перезаписываем, но для эталонов надо
    if src or not os.path.isfile(file_path):
        encoding = encoding if mode != 'wb' else None
        with open(file_path, mode=mode, encoding=encoding) as file:
            if type(data) != list:
                file.write(data)
            else:
                for line in data:
                    try:
                        file.write(f'{line}\n')
                    except Exception as error:
                        log(f'Не смогли записать строку: {line}', '[e]')
                        log(f'Exception: {error}', '[e]')
                        log(file_path)
    return file_path, http_path(file_path, src)


def http_path(path, src: Optional[str] = None):
    """Вычисление HTTP_PATH
    :param path текущее расположение файла
    :param src путь до файла относительно папки с тестами, нужен для записи эталонов в git
    """
    _http_path = config.get('HTTP_PATH', 'GENERAL')
    path = os.path.abspath(path)
    if _http_path:
        artifact_path = get_artifact_path()
        path = path.replace(artifact_path, _http_path)
        if src:
            src_path = Path(src)
            if src_path.is_absolute():
                src_path = src_path.relative_to(os.getcwd())
            # по крайне мере с + в пути точно проблемы при вычислении параметра в jc
            # parse.parse_qs(query).get('src')
            src = parse.quote_plus(str(src_path).replace('\\', '/'))
            path += f'?src={src}'
    return path.replace('\\', '/')


def get_artifact_path(folder: Optional[str] = None) -> str:
    """Возвращаем путь до директории с артефактами"""

    artifact_dir = config.get('ARTIFACT_PATH', 'GENERAL')
    if folder:
        artifact_dir = os.path.join(artifact_dir, os.path.normpath(folder))
    if not os.path.isdir(artifact_dir):
        os.makedirs(artifact_dir)
    return os.path.abspath(artifact_dir)


def create_artifact_folder():
    """Создаем папку для артифактов"""

    if not os.path.isdir("artifact"):
        os.mkdir("artifact")