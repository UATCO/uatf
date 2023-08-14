from uatf import *
from uatf.ui import *


class ControlFilterPrice(Control):
    """Фильтр по цене"""

    def __str__(self):
        return 'фильтр по цене'

    def __init__(self, how=By.CLASS_NAME, locator='catalog-filter__item--1', rus_name='Фильтры в каталоге'):
        super().__init__(how, locator, rus_name)

        self.price_start = TextField(By.CSS_SELECTOR,
                                     '[name="pfrom"]',
                                     'от')

        self.price_end = TextField(By.CSS_SELECTOR,
                                   '[name="pto"]',
                                   'до')

    def set_price(self, price_start: str, price_end: str):
        """Заполняем фильтр по цене
        :param price_start: от
        :param price_end: до"""

        self.price_start.type_in(price_start)
        self.price_end.type_in(price_end + Keys.ENTER)


class ControlFilterBrend(Control):
    """Фильтр по бренду"""

    def __str__(self):
        return 'фильтр по бренду'

    def __init__(self, how=FindBy.JQUERY, locator='.catalog-filter__item:eq(1)', rus_name='Фильтры по бренду',
                 **kwargs):
        super().__init__(how, locator, rus_name, **kwargs)

        self.brends = CustomList(By.CLASS_NAME,
                                 'catalog-filter-checkboxes__item',
                                 'Бренды')

    def select_brend(self, brends: list):
        """Выбираем необходимый бренд
        :param brends: бренды"""

        for brend in brends:
            self.brends.item(contains_text=brend).click()


class ControlFilterPanel(Control):
    """Фильтры в каталоге"""

    def __str__(self):
        return 'фильтры в каталоге'

    def __init__(self, how=By.CLASS_NAME, locator='catalog-filter', rus_name='Фильтры в каталоге', **kwargs):
        super().__init__(how, locator, rus_name, **kwargs)

        self.price_filter = ControlFilterPrice()
        self.brend_filter = ControlFilterBrend()

        self.show_btn = Button(FindBy.JQUERY,
                               '.catalog-filter__submit:eq(1)',
                               'Показать n товаров',
                               absolute_position=True)

    def show_products(self):
        """Открываем отобранные параметры"""

        self.show_btn.should_be(Displayed)
        self.show_btn.click()
