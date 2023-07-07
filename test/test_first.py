from uatf import *
from pages.yandex import YandexCommonPage


class TestFirst(TestCaseUI):
    @classmethod
    def setUpClass(cls):
        cls.page = YandexCommonPage(cls.driver, open=True)

    def test_01(self):
        log('test_01')
        assert_that(self.driver.current_url, equal_to('https://dzen.ru/'), 'Ошибка')

    def tearDown(self):
        self.browser.close_windows_and_alert()

