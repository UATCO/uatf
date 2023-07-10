from uatf import *
from uatf.ui import *


class BasketPage(Region):
    """Страница корзины"""

    bread_crumbs = CustomList(By.CLASS_NAME, 'breadcrumbs__item', 'Хлебные крошки')

    def check_load(self):
        """Проверка загрузки"""

        self.bread_crumbs.item(contains_text='Корзина').should_be(Displayed)