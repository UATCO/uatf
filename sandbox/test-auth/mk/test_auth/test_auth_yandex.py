from uatf import *
from uatf.ui import *
from pages.main_page import MainPage


class TestAuthYandex(TestCaseUI):
    """Проверяем работу авторизации"""

    @classmethod
    def setUpClass(cls):
        cls.page = MainPage(cls.driver)

    def test_01_check_auth_yandex(self):
        """Проверяем авторизацию из главной страницы через яндекс"""

        self.page.auth(self.config.CUSTOM.get('YANDEX_NAME'), self.config.CUSTOM.get('YANDEX_PASSWORD'), through='YANDEX')

    def tearDown(self):
        self.browser.close_windows_and_alert()
