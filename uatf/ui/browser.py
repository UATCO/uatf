from ..config import Config
from ..ui.run_browser import RunBrowser


class Browser:
    """Класс для работы с браузером"""

    def __init__(self):
        self.config = Config()
        self.runner = RunBrowser()
        if self.config.options['general']['browser'] == 'chrome':
            self.driver = self.runner.run_chrome()

    def open(self, url: str):
        """Метод для откртытия веб-страницы
        :param url: ссылка по которой переходим"""

        self.driver.get(url)
