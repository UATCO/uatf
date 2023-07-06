from uatf import *
from pages.yandex import YandexCommonPage


class TestFirst(TestCaseUI):
    @classmethod
    def setUpClass(cls):
        cls.page = YandexCommonPage(cls.driver)

    def setUp(self):
        self.page.open()

    def test_01(self):
        log('test_01')
        assert 1 == 1

    def tearDown(self):
        self.browser.close_windows_and_alert()




