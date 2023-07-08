from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from ..config import Config
from ..ui.elements.base_element import BaseElement
from .find_elements import FindElements
from .browser import Browser
from selenium.webdriver.common.by import By

__all__ = ['Region', 'parent_element', 'BaseRegion']


class BaseRegion:
    """Базовый класс для страниц и групп элементов (псевдо-окон, форм, etc.)"""

    how = locator = None

    def __init__(self, driver=None, inherit_parent=False):
        """Прокидываем driver в элементы и другие Region"""

        self.inherit_parent = inherit_parent
        if driver:
            if not isinstance(driver, WebDriver):
                raise TypeError('В класс Region передан не драйвер, а %s' % type(driver))
            self.driver: WebDriver = driver
            self.config: Config = Config()

    def get_elements(self) -> list:
        """Получение потенциально элементов из класса
         нужен из-за того что dir вычисляет свойства, а нам нужны только атрибуты класса"""

        # нам важен порядок элементов, из-за ссылок, нужно как в инициализации, поэтому не dir
        attr_list = []
        for index, _class in enumerate(self.__class__.__mro__):
            is_my = index == 0
            for key, value in _class.__dict__.items():
                if key not in attr_list and not key.startswith('__') and \
                        not isinstance(getattr(self.__class__, key), property):
                    value = getattr(self, key)
                    if isinstance(value, (BaseElement, BaseRegion)):
                        attr_list.append(key)
                        yield key, value, is_my

    def open(self, *args, **kwargs):
        """Метод для переопределения в наследуемых классах.
        Используется для перехода на страницу
        """
        pass

    def init(self):
        """Инициализация класса когда передали driver"""

        for key, cur_value, is_my in self.get_elements():
            if isinstance(cur_value, BaseElement):
                try:
                    setattr(self, key, cur_value.new_instance(self.driver, region=self))
                except Exception as error:
                    raise type(error)(f'Не смогли создать копию элемента\n'
                                      f'key: {key}\n'
                                      f'type: {type(cur_value)}\n'
                                      f'{repr(error)}')
            elif isinstance(cur_value, BaseRegion):
                if cur_value.inherit_parent:
                    cur_value.how = self.how
                    cur_value.locator = self.locator
                    cur_value.parent_func = self.parent_func
                    # нужно для метода элемента get_po_path
                    # палка о двух концах: один и тот же компонент встроен в разные места
                    # пока считаем его одним и тем же
                    # cur_value.parent_region = self
                    # cur_value.name = key
                cur_value.__init__(self.driver, inherit_parent=cur_value.inherit_parent)

    def parent_func(self):
        if self.how:
            return FindElements(self.how, self.locator)

    def get_element_name(self, value):
        names = [i for i in dir(self) if not i.startswith('__')]
        for key in names:
            if not isinstance(getattr(self.__class__, key, None), property):
                cur_value = getattr(self, key)
                if value == cur_value:
                    return key


class Region(BaseRegion):
    """Базовый класс для страниц и групп элементов (псевдо-окон, форм, etc.)"""

    def __init__(self, driver=None, open=False, inherit_parent=False):
        """Прокидываем driver в элементы и другие Region"""

        super().__init__(driver, inherit_parent)
        if driver:
            self.browser: Browser = Browser(driver)
            self.init()
            if open:
                self.open()


def parent_element(how: str, locator: Optional[str] = None):
    """Декоратор для Region
    Указываем в нем родительский элемент, все остальные элементы, будут искаться в родительском
    @parent_element('стратегия поиска', 'локатор')
    """

    if locator is None:
        locator = how
        how = By.CSS_SELECTOR

    def class_decorator(clazz):
        clazz.how = how
        clazz.locator = locator
        return clazz

    return class_decorator
