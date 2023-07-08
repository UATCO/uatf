from uatf import *
from uatf.ui import *


class BigGeekMain(Region):
    """Главная страница"""

    basket = Element(By.CSS_SELECTOR, '.user-header-middle__link--cart', 'Корзина')

    def check_basket_displayed(self):
        """Открываем корзину"""

        self.basket.should_be(Displayed)
