from selenium import webdriver
from ..config import Config
from ..logfactory import log


class RunBrowser:
    """Класс для запуска браузеров"""

    def __init__(self):
        self.config = Config()
        self.driver = None
        if self.config.options['GENERAL']['BROWSER'] == 'chrome':
            self.run_chrome()

    def run_chrome(self):
        """Запускаем хром"""

        self.driver = webdriver.Chrome()
        log("BROWSER: Chrome")

