from uatf import *


class YandexCommonPage(Region):
    """Яндекс страница"""

    def open(self):
        """Открываем главную страницу"""

        self.browser.open('https://dzen.ru/?force_common_feed=1')
