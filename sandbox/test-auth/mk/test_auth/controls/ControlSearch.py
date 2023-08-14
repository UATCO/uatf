from uatf import *
from uatf.ui import *
from .ControlSearchPanel import ControlSearchPanel


class ControlSearch(Control):
    """Контрол поиска"""

    def __str__(self):
        return "контрол поиска"

    def __init__(self, how=By.CLASS_NAME, locator='header-middle-search', rus_name='Поиск', **kwargs):
        super().__init__(how, locator, rus_name, **kwargs)

        self.search_input = TextField(By.CLASS_NAME,
                                      'search-header-middle__input',
                                      'Инпут поиска')

        self.search_btn = Button(By.CLASS_NAME,
                                 'search-header-middle__submit',
                                 'Кнопка поиска')

        self.search_panel = ControlSearchPanel()

    def open_search_panel(self):
        """Открываем панель поиска"""

        self.click()
        self.search_panel.check_open()
        return self.search_panel

    def search(self, search_text: str):
        """Делаем поиск
        :param search_text: что ищем?"""

        self.open_search_panel()
        self.search_panel.check_change(lambda: self.search_input.type_in(search_text))
