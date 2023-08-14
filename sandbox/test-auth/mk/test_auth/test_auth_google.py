from uatf import *
from uatf.ui import *
from pages.main_page import MainPage


class TestAuthGoogle(TestCaseUI):
    """Проверяем работу авторизации"""

    @classmethod
    def setUpClass(cls):
        cls.page = MainPage(cls.driver)

    def test_01_check_auth_google(self):
        """Проверяем авторизацию из главной страницы через гугл"""

        self.page.auth(self.config.CUSTOM.get('GOOGLE_NAME'), self.config.CUSTOM.get('GOOGLE_PASSWORD'), through='GOOGLE')

    def tearDown(self):
        self.browser.close_windows_and_alert()
