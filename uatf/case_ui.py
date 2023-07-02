from selenium.webdriver.chrome.webdriver import WebDriver

from .case import Case
from .logfactory import log
from .ui.run_browser import RunBrowser
from .ui.browser import Browser
from .config import Config


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
        cls.browser.open(cls.config.get('SITE', 'GENERAL'))

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
