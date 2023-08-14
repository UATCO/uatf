from uatf import *
from uatf.ui import *

class ProductCardMini(Region):
    """Мини карточка товара (открывается при добавлении товара в корзину)"""

    basket = Button(By.CLASS_NAME, 'cart-modal__cart-link', 'Перейти к корзине')

    def check_open(self):
        """Проверяем открытие карточки"""

        self.basket.should_be(Displayed)

    def go_to_basket(self):
        """Переходим в корзину"""

        from pages.basket_page import BasketPage
        self.basket.click()
        basket_page = BasketPage(self.driver)
        basket_page.check_load()
        return basket_page