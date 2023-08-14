from uatf import *
from uatf.ui import *
from controls import *


class Catalog(Region):
    """Каталог товаров"""

    bread_crumbs = ControlBreadcrumbs()
    grid = ControlCatalogGrid()
    search = ControlSearch()
    filter = ControlFilterPanel()

    def check_load(self):
        """Проверяем загрузку каталога"""

        self.filter.should_be(Displayed)
        self.grid.item(1).should_be(Displayed)

    def add_to_basket(self, product_name: str = '', product_number: int = None):
        """Добавляем товар корзину
        :param product_name: название товара
        :param product_number: номер товара"""

        from pages.product_card_mini import ProductCardMini
        self.grid.add_to_basket(product_name=product_name, product_number=product_number)
        card_mini = ProductCardMini(self.driver)
        card_mini.check_open()
        return card_mini

    def open_product(self, product_name: str = '', product_number: int = None):
        """Открываем карточку товара
        :param product_name: название товара
        :param product_number: номер товара"""

        from pages.product_card import ProductCard
        self.grid.item(item_number=product_number, contains_text=product_name).scroll_into_view().click()
        card = ProductCard(self.driver)
        card.check_load()
        return card

    def search_product(self, product_name: str):
        """Ищем необходимый товар
        :param product_name: название товара"""

        self.search.search(product_name)
        self.search.search_panel.open_catalog()

    def set_filter(self, **kwargs):
        """Устанавливаем фильтр
        Цена=['500', '1500']
        Бренд=['Apple', 'Beats', 'BigGeek']"""

        if 'Цена' in kwargs:
            price = kwargs.get('Цена')
            self.grid.check_change(lambda: self.filter.price_filter.set_price(price[0], price[1]))
        elif 'Бренд' in kwargs:
            self.filter.brend_filter.select_brend(kwargs.get('Бренд'))
            self.grid.check_change(lambda: self.filter.show_products())

    def check_count_products(self, count: int):
        """Проверяем кол-во продуктов
        :param count: кол-во продуктов"""

        self.grid.check_count(count)
