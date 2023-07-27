import shutil
from typing import Optional

from selenium.webdriver.chrome.webdriver import WebDriver

from ...logfactory import log
from ...pytest_core.base.case import TestCase
from ...pytest_core.decorators import BrowserSettings


class BaseCaseUI(TestCase):
    driver: WebDriver = None
    browser = None
    browser_settings: Optional[BrowserSettings] = None

    @classmethod
    def start_browser(cls) -> None:
        raise NotImplementedError('Not implement method start_browser')

    @classmethod
    def get_settings(cls) -> BrowserSettings:
        if cls.browser_settings is None:
            headless = cls.config.get('HEADLESS_MODE', 'GENERAL')
            cls.browser_settings = BrowserSettings(headless)
        return cls.browser_settings

    @classmethod
    def _setup_class_framework(cls) -> None:
        """Метод выполняется перед запуском тестов"""

        super()._setup_class_framework()
        if not cls.config.device_name:
            raise ValueError('Не задан BROWSER/OS в config')

        if cls.config.get('DO_NOT_RESTART', 'GENERAL'):
            cls.start_browser()

    def _setup_framework(self, request):
        """Метод выполняется перед каждым тестом"""

        log('_setup.start', '[d]')
        super()._setup_framework(request)

        if not self.driver:
            raise ValueError('Не смогли запустить BROWSER/APP')

    def _teardown_framework(self, request, subtests):
        """Метод выполняется после каждого теста"""

        super()._teardown_framework(request, subtests)

    @classmethod
    def _teardown_class_framework(cls):
        """Метод выполняется после прохождения всех тестов"""

        super()._teardown_class_framework()
        cls._delete_gif_screen()

    @classmethod
    def _delete_gif_screen(cls):
        """Удаление темповой папки со скринами для gif"""

        screen_folder = cls.config.get('TMP_DIR_SCREENS', 'GENERAL')
        if screen_folder:
            shutil.rmtree(screen_folder, True)
        cls.config.set_option('TMP_DIR_SCREENS', None, 'GENERAL')