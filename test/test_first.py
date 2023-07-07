from uatf import *
from pages.yandex import YandexCommonPage


class TestFirst(TestCaseUI):
    @classmethod
    def setUpClass(cls):
        cls.page = YandexCommonPage(cls.driver, open=True)

    def test_01(self):
        log('test_01')
        assert_that(1, equal_to(2), 'Числа не равны')

    def tearDown(self):
        self.browser.close_windows_and_alert()




