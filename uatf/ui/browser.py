from selenium.webdriver.chrome.webdriver import WebDriver

from ..config import Config


class Browser:
    """Класс для работы с браузером"""

    def __init__(self, driver):
        self.config = Config()
        self.driver: WebDriver = driver

    def open(self, url: str):
        """Метод для откртытия веб-страницы
        :param url: ссылка по которой переходим"""

        self.driver.get(url)

    def quite(self):
        """Закрываем браузер"""

        self.driver.quit()
