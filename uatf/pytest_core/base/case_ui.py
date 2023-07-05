import time

from selenium.webdriver.chrome.webdriver import WebDriver

from ...pytest_core.base.case import Case
from ...logfactory import log
from ...ui.run_browser import RunBrowser
from ...ui.browser import Browser
from ...config import Config
import requests


class TestCaseUI(Case):
    driver: WebDriver = None
    browser = None
    config = Config()

    @classmethod
    def start_browser(cls):
        """Запускаем браузер"""

        cls.driver = RunBrowser().driver
        cls.browser = Browser(cls.driver)

    @classmethod
    def _setup_class_framework(cls):
        """Общие действия перед запуском всех тестов"""

        log('_setup_class_framework', '[d]')
        cls.start_browser()
        url = cls.config.get('SITE', 'GENERAL')
        assert cls.check_service(url) is True, 'Сервис недоступен'
        cls.browser.open(url)

    def _setup_framework(self, request):
        """Общие действия перед запуском каждого теста"""

        super()._setup_framework(request)
        log('_setup_framework', '[d]')

    def _teardown_framework(self, request, subtests):
        """Общие действия после прохода каждого теста"""

        super()._teardown_framework(request, subtests)
        log('_teardown_framework', '[d]')

    @classmethod
    def _teardown_class_framework(cls):
        """Общие действия после прохода всех тестов"""

        log('_teardown_class_framework', '[d]')
        if cls.config:
            cls.browser.delete_download_dir()
        cls.browser.quite()

    @staticmethod
    def check_service(url):
        """Проверка доступности сайта

        :param url: адрес сайта
        """
        try:
            response = requests.get(url, verify=Config().get('API_SSL_VERIFY', 'GENERAL'))
            result = response.status_code < 500
            log("Сайт (сервис) '%s' доступен. Код ответа: %d %s" %
                (url, response.status_code, response.text), '[d]')
        except Exception as err:
            log(f'Ошибка проверки url: {url}\n' + str(err))
            result = False
        return result

