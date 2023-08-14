from uatf import *
from uatf.ui import *


class ProductCard(Region):
    """Карточка товара"""

    product_name = Text(By.CLASS_NAME, 'produt-section__title', 'Название товара')
    price = Text(By.CLASS_NAME, 'price', 'Цена')
    basket = Button(By.CLASS_NAME, 'prod-info-price__cart-btn', 'В корзину')

    def check_name(self, product_name: str):
        """Проверяем название товара
        :param product_name: название товара"""

        self.product_name.should_be(ContainsText(product_name), msg='Название товара не совпадает')

    def add_to_basket(self):
        """Добавляем товар в корзину"""

        from pages.product_card_mini import ProductCardMini
        self.basket.click()
        card_mini = ProductCardMini(self.driver)
        card_mini.check_open()
        return card_mini

    def check_load(self):
        """Проверяем загрузку карточки"""

        self.product_name.should_be(Displayed)
