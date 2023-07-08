import re
from typing import TypeVar, Callable, List, Optional, Any, Union, Type

from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from abc import ABC

from .base_element import BaseElement
from ..find_elements import FindElements, convert_to_css
from ...helper import _wait
from ...ui.helper import ListIterator
from ...ui.elements.element import Element

__all__ = ['CustomList', 'Item']


ElementType = TypeVar('ElementType', bound=Element)


def escape_text(text):
    """Преобразование текста для экранирования кавычек"""

    return "concat('" + text.replace("'", "', \"'\", '") + "', '')"


def ignore_text_case(text):
    """Игнорирование регистра текста"""

    text = escape_text(text.lower())
    return "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ', " \
           "'abcdefghijklmnopqrstuvwxyzйцукенгшщзхъфывапролджэячсмитьбю'), {0}".format(text)


class BaseItemCustomList(BaseElement):
    """BaseItemCustomList"""

    def __str__(self) -> str:
        base_name = 'элемент списка'
        if self.item_number:
            element_name = f"{base_name} №{self.item_number}"
        elif self.with_text:
            element_name = f"{base_name} с текстом \"{self.with_text}\""
        elif self.contains_text:
            element_name = f"{base_name} содержащий текст \"{self.contains_text}\""
        elif self.contains_text_ignoring_case:
            element_name = f"{base_name} содержащему текст \"{self.contains_text_ignoring_case}\" БЕЗ учета регистра"
        else:
            element_name = base_name
        return element_name

    def __init__(self, how: str, locator: str, rus_name: str, custom_list,
                 item_number: int = 0, with_text: str = '', contains_text: str = '',
                 contains_text_ignoring_case: str = '', **kwargs):
        super().__init__(how, locator, rus_name, custom_list=custom_list,
                         item_number=item_number, with_text=with_text, contains_text=contains_text,
                         contains_text_ignoring_case=contains_text_ignoring_case, **kwargs)
        self.copy_parent_from_element(custom_list)
        self._custom_list = custom_list

        self._patch_locator: bool = False  # понять сгенерили мы уже локатор или нет
        self.item_number: int = item_number
        self.with_text: str = with_text
        self.contains_text: str = contains_text
        self.contains_text_ignoring_case: str = contains_text_ignoring_case
        self._find_by_selector: bool = kwargs.get('find_by_selector', False)

    @property
    def find_element(self):
        return self._get_search_strategy()

    @find_element.setter
    def find_element(self, value):
        self._find_element = value

    def _get_item_by_locator_and_text(self) -> Callable:
        """Возвращает WebElement элемента списка"""

        raise NotImplementedError('Not implemented _get_item_by_locator_and_text')

    def _get_search_strategy(self) -> Callable:
        """Возвращает WebElement указанного элемента списка"""

        if self._find_by_selector:
            method = FindElements(self.how, self.locator)
        # для contains_text мы можем сконвертировать локаторы и будет работать с любой стратегией поиска
        elif self.contains_text or self.contains_text_ignoring_case or self.with_text:
            method = self._get_item_by_locator_and_text()
        elif self.item_number:
            def method(driver: WebDriver, webelement: WebElement) -> List[WebElement]:
                return self.__get_item_by_number(driver, webelement)
        else:
            raise ValueError('Не переданы параметры для поиска в Item в CustomList')
        return method

    def __get_item_by_number(self, driver: WebDriver, webelement: WebElement) -> List[WebElement]:
        """Возвращает WebElement элемента списка с заданным порядковым номером
        :param driver: драйвер
        :param webelement: webelement в котором ищем
        """

        def func() -> List[WebElement]:
            return custom_list(driver=driver, webelement=webelement)

        if not isinstance(self.item_number, int):
            raise TypeError('item_number должен быть числом!')
        if self.item_number == 0:
            raise ValueError('Item начинается с 1, а не с нуля!')
        custom_list = FindElements(self.how, self.locator)
        result = _wait(lambda: len(func()) >= self.item_number)
        if not result:
            raise NoSuchElementException(f'Не найден элемент №{self.item_number} в списке')
        return [func()[self.item_number - 1], ]  # для совместимости

    @property
    def position(self) -> Optional[int]:
        """Позиция элемента в списке"""

        webelement = self._exec(self.webelement, 0)  # вычисляем текущий элемент
        elements_list = self._exec(lambda: self._custom_list.webelement(return_list=True), 0)
        for i, v in enumerate(elements_list):
            if v.id == webelement.id:  # при совпадении id элемента выходим
                return i + 1
        return None


class BaseCustomList(BaseElement, ABC):
    """Класс для работы с разнообразными списками

    Для того, что бы задать список в locators нужно указать локатор,
    по которому будут находиться все элементы списка
    """

    def __str__(self) -> str:
        return 'произвольный список'

    def __iter__(self):
        return ListIterator(self, self.size)

    def __contains__(self, text: str) -> bool:
        """Вхождение текста"""

        return self.item(contains_text=text).is_displayed

    @staticmethod
    def _create_item_with_type(item: 'BaseItemCustomList', item_type: Type[ElementType], **kwargs):
        instance_element = item_type(item.how, item.locator, item.rus_name, **kwargs)
        instance_element.copy_from(item, logging=True)
        return instance_element

    def item(self, item_number: int = 0, with_text: str = '', contains_text: str = '',
             **kwargs) -> Union[ElementType, BaseItemCustomList]:
        """Возвращает экземпляр класса Item или Control"""

        if not any((item_number, with_text, contains_text)):
            raise ValueError('Не переданы обязательные параметры')
        elif item_number == 0:
            ValueError('Список в CustomList начинается с 1 не с 0!')

        item = BaseItemCustomList(self.how, self.locator, self.rus_name, self, item_number, with_text,
                                  contains_text, driver=self.driver)
        return item

    @property
    def size(self) -> int:
        """Возвращает размер списка"""

        return self.count_elements


class Item(BaseItemCustomList, Element):

    def __str__(self) -> str:
        base_name = 'элемент списка'
        if self.item_number:
            element_name = f"{base_name} №{self.item_number}"
        elif self.with_text:
            element_name = f"{base_name} с текстом \"{self.with_text}\""
        elif self.contains_text:
            element_name = f"{base_name} содержащий текст \"{self.contains_text}\""
        elif self.contains_text_ignoring_case:
            element_name = f"{base_name} содержащему текст \"{self.contains_text_ignoring_case}\" БЕЗ учета регистра"
        elif self.match_regex:
            element_name = f"{base_name} соответствующему регулярному выражению текст \"{self.match_regex}\""
        else:
            element_name = base_name
        return element_name

    def __init__(self, how: str, locator: str, rus_name: str, custom_list,
                 item_number: int = 0, with_text: str = '', contains_text: str = '',
                 contains_text_ignoring_case: str = '', match_regex: Any = None, **kwargs):
        super().__init__(how, locator, rus_name, custom_list=custom_list,
                         item_number=item_number, with_text=with_text, contains_text=contains_text,
                         contains_text_ignoring_case=contains_text_ignoring_case, match_regex=match_regex, **kwargs)
        self.match_regex: Any = match_regex

    def _convert_to_jquery(self) -> None:
        """Конвертируем в jquery"""

        self.how = 'jquery'
        self.locator: str = self.locator.strip()
        text_selector: str = self.contains_text or self.with_text or self.contains_text_ignoring_case
        text_selector = text_selector.replace("\\", "\\\\\\\\").replace("'", "\\'").replace('"', '\"')
        if self.contains_text_ignoring_case:
            func = 'containsIgnoreCase'
        elif self.with_text:
            func = 'exact'
        else:
            func = 'contains'
        quotes = "\\'" if '"' in text_selector else '\"'
        text_selector = ":{0}({2}{1}{2})".format(func, text_selector, quotes)
        self.locator = ','.join([part + text_selector for part in self.locator.split(',')])

    def _get_item_by_locator_and_text(self) -> Callable:
        """Возвращает WebElement элемента списка"""

        if not self._patch_locator:
            if self.how == By.CSS_SELECTOR or self.how == 'jquery':
                self._convert_to_jquery()
            elif self.how == By.XPATH:
                self._convert_to_xpath()
            else:
                self.how, self.locator = convert_to_css(self.how, self.locator)
                self._convert_to_jquery()
            self._patch_locator = True
        return FindElements(self.how, self.locator)

    def _get_search_strategy(self) -> Callable:
        """Возвращает WebElement указанного элемента списка"""

        if self._find_by_selector:
            method = FindElements(self.how, self.locator)
        # для contains_text мы можем сконвертировать локаторы и будет работать с любой стратегией поиска
        elif self.contains_text or self.contains_text_ignoring_case or self.with_text:
            method = self._get_item_by_locator_and_text()
        elif self.match_regex:
            def method(driver: WebDriver, webelement: WebElement) -> List[WebElement]:
                return self.__get_item_by_match_regex(self.match_regex, driver, webelement)
        elif self.item_number:
            def method(driver: WebDriver, webelement: WebElement) -> List[WebElement]:
                return self.__get_item_by_number(driver, webelement)
        else:
            raise ValueError('Не переданы параметры для поиска в Item в CustomList')
        return method

    def __get_item_by_number(self, driver: WebDriver, webelement: WebElement) -> List[WebElement]:
        """Возвращает WebElement элемента списка с заданным порядковым номером
        :param driver: драйвер
        :param webelement: webelement в котором ищем
        """

        def func() -> List[WebElement]:
            return custom_list(driver=driver, webelement=webelement)

        if not isinstance(self.item_number, int):
            raise TypeError('item_number должен быть числом!')
        if self.item_number == 0:
            raise ValueError('Item начинается с 1, а не с нуля!')
        if self.how != By.XPATH:
            self.how, self.locator = convert_to_css(self.how, self.locator)
            self.how = 'jquery'
        custom_list = FindElements(self.how, self.locator)
        result = _wait(lambda: len(func()) >= self.item_number)
        if not result:
            raise NoSuchElementException(f'Не найден элемент №{self.item_number} в списке')
        return [func()[self.item_number - 1], ]  # для совместимости

    def _convert_to_xpath(self) -> None:
        """Конвертируем в xpath"""

        text_selector = self.contains_text or self.with_text or self.contains_text_ignoring_case
        self.locator = self.locator.replace("'", '"')

        if self.contains_text:
            text_selector = "contains(.,{0})".format(escape_text(self.contains_text))
        elif self.contains_text_ignoring_case:
            text_selector = 'contains({0})'.format(ignore_text_case(text_selector))
        elif self.with_text:
            text_selector = ".={0}".format(escape_text(self.with_text))
        else:
            raise ValueError('Не переданы обязательные параметры')
        self.locator += "[{0}]".format(text_selector)

    def __get_item_by_match_regex(self, match_regex: Any,
                                  driver: WebDriver, webelement: WebElement) -> List[WebElement]:
        """Возвращает WebElement элемента списка с точным совпадением текста
        :param match_regex: точное совпадение текста
        """

        def func() -> List[WebElement]:
            return custom_list(driver=driver, webelement=webelement)

        custom_list = FindElements(self.how, self.locator)

        elements: List[WebElement] = []
        for index, element in enumerate(func()):
            try:
                text = driver.execute_script('return arguments[0].textContent', element)
            except WebDriverException:
                break
            if re.search(match_regex, text):
                if not elements:
                    self.item_number = index + 1
                elements.append(element)
        return elements


class CustomList(BaseCustomList, Element):

    def item(self, item_number: int = 0, with_text: str = '', contains_text: str = '',
             contains_text_ignoring_case: str = '', match_regex: Any = None,
             element_type: Optional[Type[ElementType]] = None, **kwargs) -> Union[ElementType, Item]:
        """Возвращает экземпляр класса Item или Control"""

        if not any((item_number, with_text, contains_text, contains_text_ignoring_case, match_regex)):
            raise ValueError('Не переданы обязательные параметры')
        elif item_number == 0:
            ValueError('Список в CustomList начинается с 1 не с 0!')

        item = Item(self.how, self.locator, self.rus_name, self, item_number, with_text,
                    contains_text, contains_text_ignoring_case, match_regex, driver=self.driver)

        if element_type:
            return self._create_item_with_type(item=item, item_type=element_type, **kwargs)
        else:
            return item

    def find_item(self, how: str, locator: str, element_type: Optional[Type[ElementType]] = None,
                  **kwargs) -> Union[ElementType, Item]:
        """Поиск item внутри CustomList по css селектору,
        поддерживаются стратегии поиска CustomList: css, id, name, class, data-qa, templatename"""

        how_p, locator_p = convert_to_css(self.how, self.locator)
        how, locator = convert_to_css(how, locator)
        assert how_p == how, 'Стратегии поиска CustomList и Item не совпадают'
        assert how_p == By.CSS_SELECTOR, 'Стратегия поиска CustomList не поддерживается'
        assert how == By.CSS_SELECTOR, 'Стратегия поиска Item не поддерживается'

        locator = locator_p + locator
        item = Item(how, locator, self.rus_name, custom_list=self,
                    driver=self.driver, item_how=how, find_by_selector=True)

        if element_type:
            return self._create_item_with_type(item=item, item_type=element_type, **kwargs)
        else:
            return item

    def match_regex(self, regex: Any) -> bool:
        """Соответствие регулярному выражению (Нужен для MatchRegex)"""

        for element in self.webelement(return_list=True):
            try:
                element_text = self.driver.execute_script(
                    'return arguments[0].textContent', element
                )
            except WebDriverException:
                break
            if re.search(regex, element_text) and element.is_displayed():
                return True
        return False
