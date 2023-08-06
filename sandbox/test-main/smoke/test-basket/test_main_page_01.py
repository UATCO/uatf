from uatf import *
from sandbox.pages.main_page import MainPage


class TestMainPage01(TestCaseUI):
    """Проверяем работу главной страницы"""

    @classmethod
    def setUpClass(cls):
        cls.page = MainPage(cls.driver)

    def test_01_check_basket(self):
        """Проверяем открытие корзины"""

        self.page.open_basket()

    def test_02_check_auth(self):
        """Проверяем авторизацию"""

        self.page.auth(self.config.GENERAL.get(''), self.config.GENERAL.get('PASSWORD'))

    def tearDown(self):
        self.browser.close_windows_and_alert()
        self.page.open()
