import configparser
import os
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Option:
    """Класс для описания опций конфига / командной строки"""

    name: str
    default: Any
    help: str
    type: Any = None
    nargs: Optional[str] = None
    action: Any = None


DEFAULT_VALUES = {
    'GENERAL': [
        Option("SHOW_CHECK_LOG", False, help='показать логи проверок (уровень сh)'),
        Option("DEBUG", False, help="выводить сообщения уровня DEBUG или нет"),
        Option('RESTART_AFTER_BUILD_MODE', False, action='store_true',
               help='Перезапускать ли упавшие тесты внутри сборки упавших тестов в конце сборки'),
        Option('NODE_IDS', [], action="store", type=str, nargs="+",
               help='Тут будет список всех node_id, pytest subtest не находит'),
    ]
}


class Config:
    """Класс считывающий данные с конфига"""

    def __init__(self, path: str = None):
        self._path = path
        self.options = {}
        self._set_default_values()
        self._read_file()

    def _read_file(self):
        """Разбираем config.ini файл"""

        path = os.path.join(os.getcwd(), "config.ini")
        parser = configparser.ConfigParser()
        _file = open(path, 'r')
        parser.read_file(_file)
        for section in parser.sections():
            self.options.fromkeys(section.upper(), {})
            for option in parser.options(section):
                self.options[section.upper()][option.upper()] = parser.get(section, option)
        return self.options

    def _set_default_values(self):
        """Выставляем значения по умолчанию"""

        for group, options in DEFAULT_VALUES.items():
            self.options[group] = {}
            for option in options:
                self.options[group][option.name] = option.default

    @property
    def pycharm_run(self):
        return os.environ.get('PYCHARM_HOSTED') == '1'

    @property
    def is_last_run(self) -> bool:
        """Не сохраняем отчеты если перезапуск"""

        return not self.get('RESTART_AFTER_BUILD_MODE', 'GENERAL')

    def get(self, option: str, section: Optional[str] = None):
        """Возвращает значение опции
        :param option: имя опции заглавными буквами
        :param section: имя секции
        """

        return self.options[section][option]
