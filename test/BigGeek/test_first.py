from uatf import *
from test.BigGeek.pages.BigGeek import BigGeekMain


class TestFirst(TestCaseUI):
    @classmethod
    def setUpClass(cls):
        cls.main_page = BigGeekMain(cls.driver)

    def test_01(self):

        log('Проверяем открытие корзины')
        self.main_page.check_basket_displayed()

    def tearDown(self):
        self.browser.close_windows_and_alert()

