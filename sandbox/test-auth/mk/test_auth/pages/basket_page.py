from uatf import *
from uatf.ui import *
from controls import *


class BasketPage(Region):
    """Страница корзины"""

    bread_crumbs = ControlBreadcrumbs()
    empty_view = Text(By.CLASS_NAME, 'cart__container', 'Корзина пуста')
    products = CustomList(By.CLASS_NAME, 'product-cart__item', 'Товары')
    order = Button(By.CLASS_NAME, 'sticky-cart__button', 'Оформить заказ')

    def check_load(self):
        """Проверка загрузки"""

        self.bread_crumbs.item(contains_text='Корзина').should_be(Displayed)

    def check_empty_basket(self):
        """Проверяем что корзина пуста"""

        self.empty_view.should_be(ContainsText('Корзина пуста'))

    def get_products(self, product_name: str):
        """Название товара
        :param product_name: название товара"""

        return self.products.item(contains_text=product_name)

    def check_product_exist(self, product_name: str, displayed: bool = True):
        """Проверяем наличие товара
        :param product_name: название товара
        :param displayed: должен ли отображаться?"""

        product = self.get_products(product_name)
        if displayed:
            product.should_be(Displayed)
            product.should_not_be(CssClass('product-cart__item--disabled'))
        else:
            product.should_be(CssClass('product-cart__item--disabled'), Displayed)

    def delete_product(self, product_name: str):
        """Удаляем товар из корзины
        :param product_name: название товара"""

        self.get_products(product_name).element(By.CLASS_NAME, 'product-cart__remove-button').click()

    def make_order(self):
        """Оформляем заказ"""

        from pages.order_page import OrderPage
        self.order.click()
        order_page = OrderPage(self.driver)
        order_page.check_load()
        return order_page
