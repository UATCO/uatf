from uatf import *
from uatf.ui import *


class BigGeekMain(Region):
    """Главная страница"""

    basket = Element(By.CSS_SELECTOR, '.user-header-middle__link--cart', 'Корзина')
    upper_tabs = CustomList(By.CSS_SELECTOR, '.static-header-bottom__item', 'Кнопки вкладок')

    def check_basket_displayed(self):
        """Открываем корзину"""

        self.basket.should_be(Displayed)

    def select_upper_tab(self, tab_name: str):
        """Переходим по вкладке сверху
        :param tab_name: Название вкладки"""

        self.upper_tabs.item(contains_text=tab_name).click()
