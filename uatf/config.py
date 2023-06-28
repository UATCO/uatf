import configparser


class Config():
    """Класс считывающий данные с конфига"""

    def __init__(self, path: str):
        self._path = path
        self.options = {}

    def read_file(self):
        """Разбираем config.ini файл"""

        parser = configparser.ConfigParser()
        _file = open(self._path, 'r')
        parser.read_file(_file)
        for section in parser.sections():
            self.options[section] = {}
            for option in parser.options(section):
                self.options[section][option] = parser.get(section, option)
        return self.options
