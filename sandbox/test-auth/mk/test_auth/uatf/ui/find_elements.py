"""Модуль для стратегии поиска элементов"""
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.common.exceptions import JavascriptException, WebDriverException
from ..helper import _wait
from typing import Callable, List, Any, Optional, Dict, Tuple


class FindBy(By):
    DATA_QA = "data qa"
    JQUERY = "jquery"
    JAVASCRIPT = 'javascript'


jquery_text = re.compile('(.*):(?:containsIgnoreCase|exact|contains)')


def replace_text(locator: str) -> str:
    """Преобразование текста для экранирования кавычек"""

    match = jquery_text.match(locator)
    if not match:
        locator = locator.replace("'", '"')
    else:
        locator = locator[:match.end()].replace("'", '"') + locator[match.end():]
    return locator


def load_jquery(driver: WebDriver, error: WebDriverException) -> bool:
    """Подключение jQuery"""

    script = """if (!window.jQuery) {
                var jq = document.createElement('script');
                jq.src = '/cdn/JQuery/jquery/3.3.1/jquery-min.js';
                document.getElementsByTagName('head')[0].appendChild(jq);}
                if (!jQuery.expr[':'].containsIgnoreCase) {
                jQuery.expr[':'].containsIgnoreCase = function(a, i, m) {
                return jQuery(a).text().toLowerCase().indexOf(m[3].toLowerCase()) > -1;};}
                if (!jQuery.expr[':'].exact) {
                jQuery.expr[':'].exact = function(a, i, m) {
                return jQuery(a).text().trim() == m[3];};}
    """
    errors = ("jQuery", 'unsupported pseudo', 'JavaScript error', 'Error executing JavaScript')
    msg = error.msg
    for e in errors:
        if msg and e in msg:
            _wait(lambda: driver.execute_script(script), 1)
            return True
    return False


def exec_jquery(action: Callable, driver: WebDriver) -> Optional[Any]:
    """Метод в качестве параметра получает функцию action

    Ждет wait_max время пока функция не вернет True
    Если не возвращает, то вернет в конце результат выполнения функции.

    :param driver: WebDriver
    :param action: действие которое ожиданем
    """
    try_count = 0  # чтобы была возможность загрузить jquery на страницу, если нет
    res = []
    while True:
        try:
            res = action()
            return res
        except (JavascriptException, WebDriverException) as err:
            is_load = load_jquery(driver, err)
            try_count += 1
            if is_load and try_count == 1:
                continue
            else:
                break
    return res


def find_elements_by_jquery_chrome(locator: str, driver: WebDriver, webelement: WebElement) -> List[WebElement]:
    """Поиск по jquery"""

    locator = replace_text(locator)
    if driver == webelement:
        elements = exec_jquery(lambda: driver.execute_script("return jQuery.find(\'%s\');" % locator), driver)
    else:
        elements = exec_jquery(lambda: driver.execute_script(
            "return jQuery(arguments[0]).find(\'%s\');" % locator, webelement), driver)
    return elements if isinstance(elements, list) else []


# TODO со временем сделать метод универсальным под разные браузеры
def find_elements_by_jquery(locator: str, driver: WebDriver, webelement: WebElement) -> List[WebElement]:
    """Поиск элемента по jquery
    """

    elements = find_elements_by_jquery_chrome(locator, driver, webelement)

    return elements


def find_elements(how: str, locator: str, driver: WebDriver, webelement: WebElement) -> List[WebElement]:
    """Обертка для поиска элементов в элементах

    :param how: стратегия поиска
    :param locator: локатор
    :param driver: драйвер
    :param webelement: если ищем в родительском элементе
    """
    if how == FindBy.JQUERY:
        elements = find_elements_by_jquery(locator, driver, webelement)
    elif how == FindBy.JAVASCRIPT:
        elements = driver.execute_script(locator)
    else:
        elements = webelement.find_elements(how, locator)
    return elements


_templates: Dict[str, Tuple[str, str]] = {
    By.ID: (By.CSS_SELECTOR, '[id="{0}"]'),
    By.NAME: (By.CSS_SELECTOR, '[name="{0}"]'),
    By.CLASS_NAME: (By.CSS_SELECTOR, '.{0}'),
    FindBy.DATA_QA: (By.CSS_SELECTOR, '[data-qa="{0}"]'),
}


def convert_to_css(how: str, locator: str) -> Tuple[str, str]:
    """Конвертируем в css"""

    res = _templates.get(how)
    if res:
        how, template = res
        locator = template.format(locator)
    return how, locator


class FindElements:
    """Класс для понимания, что за parent_element у элемента"""

    __slots__ = ('how', 'locator')

    def __str__(self):
        return f'{self.how}: {self.locator}'

    def __init__(self, how, locator):
        how, locator = convert_to_css(how, locator)
        self.how = how
        self.locator = locator

    def __call__(self, driver, webelement):
        if self.locator:
            return find_elements(self.how, self.locator, driver, webelement)
        else:
            return [driver, ]
