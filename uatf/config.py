import configparser
import os
from dataclasses import dataclass
from typing import Any, Optional
from distutils import util


def type_bool(x: str) -> bool:
    """Проблема с type=bool у аргументов, нужно передавать пустой объект
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    return bool(util.strtobool(x))


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
        Option("DEBUG", False, type=type_bool, help="выводить сообщения уровня DEBUG или нет"),
        Option('RESTART_AFTER_BUILD_MODE', False, action='store_true',
               help='Перезапускать ли упавшие тесты внутри сборки упавших тестов в конце сборки'),
        Option('NODE_IDS', [], action="store", type=str, nargs="+",
               help='Тут будет список всех node_id, pytest subtest не находит'),
        Option("SITE", '', type=str, help='Тестируемый сайт'),
        Option("DOWNLOAD_DIR", "", action="store", type=str,
               help="Корневая папка (локальная) в которой будут создаваться tmp папки для выгрузки файлов"),
        Option("DOWNLOAD_DIR_BROWSER", "", action="store", type=str,
               help="Папка в которой будут создаваться tmp папки для выгрузки файлов"),
        Option("BROWSER_LOG_LEVEL", "SEVERE", type=str, help="Уровень логирования"),
    ]
}


class Config:
    """Класс считывающий данные с конфига"""

    instance = None

    def __new__(cls, *args, **kwargs):  # singleton
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, path: str = None, first_init: bool = True):
        if not hasattr(self, 'first_init'):
            self._path = path
            self.first_init = first_init
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

        if option not in self.options[section]:
            return None
        else:
            return self.options[section][option]

    def set_option(self, name: str, value, section: str):
        """Устанавливает значение аттрибута класса
        .. warning:: метод для служебного использования!
        """
        option_name = name.upper()
        section_name = section.upper()
        self.options[section_name][option_name] = value
