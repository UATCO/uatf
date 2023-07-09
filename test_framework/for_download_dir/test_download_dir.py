from uatf import *
from uatf.ui import *


class TestDownloadDir(TestCaseUI):

    def test(self):
        assert_that(self.config.GENERAL['DOWNLOAD_DIR'], not_equal(None), 'Не задана опция DOWNLOAD_DIR')
        assert_that(self.config.GENERAL['DOWNLOAD_DIR'], equal_to(self.config.GENERAL['DOWNLOAD_DIR']),
                    'Неверно заданы настройки')
        assert_that(self.config.GENERAL['ETH_DOWNLOAD_DIR'], equal_to(self.config.GENERAL['ETH_DOWNLOAD_DIR']),
                    'Неверно заданы настройки')
        assert_that(self.config.GENERAL['ETH_DOWNLOAD_DIR'], not_equal(self.config.GENERAL['DOWNLOAD_DIR']),
                    'Не изменили папку для загрузки')
        assert_that(self.config.GENERAL['ETH_DOWNLOAD_DIR'], not_equal(self.config.GENERAL['DOWNLOAD_DIR']),
                    'Не изменили папку для загрузки')
        assert_that(self.config.GENERAL['DOWNLOAD_DIR_BROWSER'], not_equal(None),
                    'Не задана опция DOWNLOAD_DIR_BROWSER')
        assert_that(self.config.GENERAL['DOWNLOAD_DIR_BROWSER'], equal_to(self.config.GENERAL['DOWNLOAD_DIR_BROWSER']),
                    'Неверно заданы настройки')
        assert_that(self.config.GENERAL['ETH_DOWNLOAD_DIR_BROWSER'], equal_to(self.config.GENERAL['ETH_DOWNLOAD_DIR_BROWSER']),
                    'Неверно заданы настройки')
        assert_that(self.config.GENERAL['ETH_DOWNLOAD_DIR_BROWSER'],
                    not_equal(self.config.GENERAL['DOWNLOAD_DIR_BROWSER']),
                    'Не изменили папку для загрузки')
        assert_that(self.config.GENERAL['ETH_DOWNLOAD_DIR_BROWSER'], not_equal(self.config.GENERAL['DOWNLOAD_DIR_BROWSER']),
                    'Не изменили папку для загрузки')
