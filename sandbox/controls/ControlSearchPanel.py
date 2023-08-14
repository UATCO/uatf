from uatf import *
from uatf.ui import *


class ControlSearchPanel(Control):
    """Панель поиска"""

    def __str__(self):
        return "панель поиска"

    def __init__(self, how=By.CLASS_NAME, locator='digi-ac', rus_name='Панель поиска', **kwargs):
        super().__init__(how, locator, rus_name, **kwargs)
        self.set_absolute_position()

        self.history_panel = Element(By.CLASS_NAME,
                                     'digi-ac__set_main',
                                     'История поиска')

        self.product_panel = Element(By.CLASS_NAME,
                                     'digi-ac__set_products',
                                     'Продукты')

        self.all_results = Button(By.CLASS_NAME,
                                  'digi-ac-find__button',
                                  'Все результаты')

    def check_open(self):
        """Проверяем открытие панели"""

        self.product_panel.should_be(Displayed)

    def open_catalog(self):
        """Открываем каталог по кнопке Все результаты"""

        self.all_results.click()
