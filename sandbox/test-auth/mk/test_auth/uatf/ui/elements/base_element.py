import functools
import time
from inspect import signature
from typing import TypeVar, Callable, Any, Optional, Dict, Union, Type
from ..actions_chains import ActionChainsUATF
from selenium.common import WebDriverException, NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException, ElementClickInterceptedException, ElementNotVisibleException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from ..find_elements import FindElements
from ..should_be import Condition, should_framework
from ...logfactory import log
from ...config import Config
from ...exceptions import ElementException
from ...helper import Aggregator, _wait

__all__ = ['BaseElement', 'before_after']


CONFIG = Config()
HIGHLIGHT = CONFIG.get('HIGHLIGHT_ACTION', 'GENERAL')
LAST_RUN = not CONFIG.get('RESTART_AFTER_BUILD_MODE', 'GENERAL')
RECORD_VIDEO = CONFIG.get('SCREEN_CAPTURE', 'GENERAL')
JS_COLLECT = CONFIG.get('JS_COLLECTOR_SERVICE', 'GENERAL')

TypeElement = TypeVar('TypeElement', bound='BaseElement')
TypeSelf = TypeVar('TypeSelf', bound='BaseElement')


def check_strategy_search(how: str) -> str:
    """Проверка правильности задания стратегии поиска"""

    if how == 'css':
        how = By.CSS_SELECTOR
    return how


def get_log_element(rus_name: str = '') -> str:
    """Проверка задано русское наименование или нет"""

    output_log = CONFIG.get('ELEMENT_OUTPUT_LOG', 'GENERAL')
    if output_log == 'user_friendly':
        if not rus_name:
            raise ValueError('В PageObject обязательно задавать русское '
                             'наименование элементов\n'
                             '(ELEMENT_OUTPUT_LOG = user_friendly)')
    return rus_name


def before_after(f: Callable) -> Any:
    """Декоратор выполнения действий до/после action

    :param f: выполняемый action
    """
    if (LAST_RUN or RECORD_VIDEO == 'all') and (HIGHLIGHT or RECORD_VIDEO):
        @functools.wraps(f)
        def tmp(*args: Any, **kwargs: Any) -> Any:
            """
            :param args: список параметров метода f
            :param kwargs: словарь параметров метода f
            """
            if HIGHLIGHT or RECORD_VIDEO:
                from ...ui.screen_capture import DrawableType
                highlight_action = getattr(args[0], 'highlight_action', None)
                if highlight_action:
                    highlight_action(type_of_action=DrawableType(f.__name__), args=args)
                if JS_COLLECT:
                    Aggregator.add_errors()
            return f(*args, **kwargs)
    else:
        def tmp(*args: Any, **kwargs: Any) -> None:
            # выполнение действия
            return f(*args, **kwargs)
    return tmp


class BaseElement:
    """Базовый класс для всех элементов

    | Содержит в себе методы, которые актуальны для большинства наследников.
    | При этом сам может быть использован для моделирования в коде объектов,
    | которые не подходят ни под одного наследника. Типичные примеры:

    * блок страницы с картинкой
    * div, появления которого нужно просто дождаться

    :param how: локатор нахождения webelement
    :param locator: локатор нахождения webelement
    :param rus_name: русское наименование элемента
    """

    IGNORE_ATTRS = ('region', 'parent')

    def __str__(self) -> str:
        return 'элемент'

    def __repr__(self):
        return f'{self.__class__}\nPO path: {self.get_po_path()}\n{self.locator_as_str()}'

    def __init__(self, how: str, locator: str, rus_name: str = '', **kwargs):
        """Описание элемента

        :param how стратегия поиска
        :param locator селектор
        :param rus_name русское имя элемента
        :param absolute_position абсолютное позиционирование (ингнорирование иерархии)
        :param driver WebDriver
        """
        self.how = check_strategy_search(how)
        self.locator = locator
        kwargs.pop('name', '')
        self.rus_name = get_log_element(rus_name=rus_name)
        self._str: Optional[str] = None

        self._absolute_position = kwargs.pop('absolute_position', False)
        self.parent = kwargs.get('parent')  # родитель, subclass Element
        self.region = kwargs.get('region')  # в атрибут сохряется регион из которого зовется элемент
        self.driver: WebDriver = kwargs.pop('driver', None)

        self._find_element: Optional[Callable] = None
        self._kwargs_tuple = tuple(kwargs.items())
        if self.driver:  # когда driver передали через параметры инициализации, вне класса Region
            self.init(self.driver)

    def init(self, driver: WebDriver, parent=None, region=None) -> None:
        """Инициализация контрола не в PO
        ТОЛЬКО ДЛЯ ДИНАМИЧЕСКИХ КОНТРОЛОВ

        :param driver: драйвер
        :param parent: родитель
        :param region: экземпляр Region в котором инициализирован элемент, для получения parent
        """
        self.driver = driver
        self.region = region
        self.rus_name = get_log_element(rus_name=self.rus_name)
        if not self.absolute_position:
            # могу представить только ссылку на элемент контрола внутри pages, не хотелось бы терять родителя
            if not (self.parent and parent is None):
                self.parent = parent
                if parent and region is None:
                    self.region = parent.region

    @property
    def find_element(self) -> Callable:
        if not self._find_element:
            self._find_element = FindElements(self.how, self.locator)
        return self._find_element

    @find_element.setter
    def find_element(self, value):
        self._find_element = value

    def set_absolute_position(self, value=True):
        """Установка абсолютного позиционирования для обособленных элементов страницы
        :param value - абсолютная позиция или нет
        """
        self._absolute_position = value

    @property
    def absolute_position(self):
        return self._absolute_position

    def get_po_path(self):
        """Вернет путь до элемента внутри PO"""

        if not self.region:  # динамически инициализирован
            return

        parent = self
        while parent.parent:
            parent = parent.parent

        if parent and parent.region:
            element_name = parent.region.get_element_name(parent)
        else:
            element_name = self.region.get_element_name(self)

        if not element_name:
            return

        region = self.region
        region_name = self.region.__class__.__name__

        element_path = f'{region.__module__}.{region_name}.{element_name}'
        return element_path

    def locator_as_str(self):
        """Получение локатора в виде строки"""

        locator = ''
        locator_list = self.locator_as_list()
        if len(locator_list) > 0:
            locator = 'Locator: \n'
            locator += '\n'.join(f'  {i + 1}. {v}' for i, v in enumerate(locator_list))
        return locator

    def locator_as_list(self):
        """Получение списка локаторов"""

        localor_list = []
        for e in self.webelements:
            if isinstance(e, FindElements):
                localor_list.append(str(e))
            else:
                localor_list.append('python function')
        return localor_list

    @property
    def webelements(self):
        """Получение списка элементов"""

        from ..region import BaseRegion
        elements_list = [self.find_element]
        if not self.absolute_position:
            parent = self.parent
            while parent:
                elements_list.insert(0, parent.find_element)
                if not parent.absolute_position and parent.parent:
                    parent = parent.parent
                else:
                    break

            if not (parent and parent.absolute_position):
                if self.region and isinstance(self.region, BaseRegion):
                    # TODO возможно стоит ругаться если не Region
                    func = self.region.parent_func()
                    if func:
                        elements_list.insert(0, func)
        return elements_list

    def copy_parent_from_element(self, element: 'BaseElement'):
        """Копируем родителя и опции с элемента
        :param element элемент с которого копируем родителя
        """
        if not isinstance(element, BaseElement):
            raise TypeError('Передан не Element!')
        self.set_absolute_position(element.absolute_position)
        self.parent = element.parent
        self.region = element.region

    def copy(self, parent=None, region=None):
        """Создаст новый экзепляр элемента

        :param возможность заменить parent при копировании
        :param возможность заменить region при копировании
        """

        return self.new_instance(driver=self.driver, parent=parent, region=region, create=True)

    def new_instance(self, driver, parent=None, region=None, create=False):
        """Получение нового экземпляра элемента

        :param driver Webdriver
        :param parent parent element
        :param region Region
        :param create создать новый экземпляр и не затрагиваем старый, нужно для копирования
        """

        if self._kwargs_tuple:
            new = type(self)(self.how, self.locator, self.rus_name, **{k: v for k, v in self._kwargs_tuple})
        else:
            new = type(self)(self.how, self.locator, self.rus_name)

        new.set_absolute_position(self.absolute_position)
        new.init(driver, parent=parent or self.parent, region=region)
        if not create:
            # это нужно для того, чтобы если мы делаем ссылки внутри PageObject
            # мы понимали, что за родитель у ссылки, т.к. ссылка видит именно атрибут класса,
            # а не инициализированный экземпляр
            self.init(driver, parent=parent, region=region)
        return new

    def copy_from(self, element: 'BaseElement', logging: bool = False):
        """Copy element
        :param element элемент с которого копируем
        :param logging копировать ли лог с текущего элемента
        """

        # возможно надо еще добавить region, но вроде для такого типа элементов не надо
        self._find_element = element.find_element
        self.how = element.how
        self.locator = element.locator
        self.init(element.driver, element.parent, element.region)
        if logging:
            self._str = str(element)

    def add_child(self, *elements: 'BaseElement') -> None:
        """Добавить родителя в elements
        :param elements: uatf.element.Element
        """
        for element in elements:
            if issubclass(element.__class__, BaseElement):
                element.add_parent(self)
            else:
                raise TypeError('Можно передавать только Element!')

    def add_parent(self, parent_element: 'BaseElement') -> None:
        """Добавляет родителя к текущему элементу
        :param parent_element: uatf.element.Element
        """

        self.init(parent_element.driver, parent_element, region=parent_element.region)

    def print_locator(self):
        """Выведет в консоль локатор"""

        print(self.locator_as_str())

    def webelement(self, methods_list=None, return_list: bool = False) -> Any:
        """Вычисляем webelement по заданному локатору и стратегии поиска

        Метод пытается найти webelement self._config.WAIT_ELEMENT_LOAD секунд.
        Если webelement не найден за указанное время,
        вызовет NoSuchElementException
        :param methods_list: если передан список методов получения webelement'ов, то берем его, а не self._webelements
        :param return_list: возвращать список webelement или 1 webelement
        """
        if not methods_list:
            methods_list = self.webelements

        webelements = []  # чтобы PyCharm не ругался
        end_time = time.time() + CONFIG.get('WAIT_ELEMENT_LOAD', 'GENERAL')
        while True:
            assert self.driver, 'Не передан драйвер элементу! Проверьте правильность инициализации Page/Region'
            current_webelement = self.driver
            # перебираем всю цепочку локаторов
            for method in methods_list:
                try:  # страница может измениться и элемент пропадет
                    # для совместимости, не везде нужен driver в параметрах
                    if len(signature(method).parameters) == 2:
                        webelements = method(self.driver, current_webelement)
                    else:
                        webelements = method(current_webelement)
                    if webelements and len(webelements) > 0:
                        if len(webelements) > 1:
                            log("Найдено более одного webelement'a !", '[d]')
                        current_webelement = webelements[0]
                        continue  # если получили элемент, то идем дальше
                    else:  # если не получили, то вычисляем всю цепочку сначала
                        break
                except WebDriverException:
                    break  # если было исключение, то идем сначала
            else:
                break

            if time.time() > end_time:
                raise NoSuchElementException(f'no such element: Unable to locate element: '
                                             f'{{"method":"{self.how}","selector":"{self.locator}"}}')
        return webelements if return_list else webelements[0]

    @staticmethod
    def _return_property(action: Callable):
        """Возвращает значение свойства"""

        result = False
        error = None
        s = time.perf_counter()
        cur_wait_time = CONFIG.get('WAIT_ELEMENT_LOAD', 'GENERAL')
        CONFIG.set_option('WAIT_ELEMENT_LOAD', 0, 'GENERAL')
        while True:
            if time.perf_counter() - s > 1:
                break
            try:
                result = action()
                break
            except StaleElementReferenceException as err:
                error = err
                continue
            except Exception as err:
                error = err
                log(error, '[d]')
                break
        CONFIG.set_option('WAIT_ELEMENT_LOAD', cur_wait_time, 'GENERAL')
        return result, error

    def _exec(self, action: Callable, wait_time: Optional[int] = True):
        """Выполнения действия + патчинг исключения"""

        if wait_time == 0:
            result, exception = self._return_property(action)
            if exception:
                self._patch_exception(exception)
        else:
            result = _wait(action, wait_time=wait_time)
            self._patch_exception(result)
        return result

    def name_output(self) -> str:
        """Метод вычисляет название элементов"""

        if not self._str:
            type_str = str(self)
        else:
            type_str = self._str

        output_log = CONFIG.get('ELEMENT_OUTPUT_LOG', 'GENERAL')
        if output_log == 'locator':
            log_message = f'{type_str} c локатором "{self.locator}"'
        else:
            log_message = f'{type_str} "{self.rus_name}"'
        return log_message

    def _patch_exception(self, result: Any) -> None:
        """Метод проверяет результаты выполнения action
        :param result: результат выполнения action
        """
        if isinstance(result, Exception):
            if isinstance(result, WebDriverException):
                rus_msg = ''
                strict_msg = '\nSelenium: ' + result.msg.split('\n')[0].rstrip()
                if CONFIG.get('ELEMENT_OUTPUT_LOG', 'GENERAL') in ('user_friendly', 'name'):
                    strict_msg = f'\n{self.locator_as_str()}{strict_msg}'.rstrip()
                if isinstance(result, NoSuchElementException):
                    rus_msg = f'Не найден в DOM {self.name_output()}{strict_msg}'
                elif isinstance(result, ElementNotInteractableException):
                    rus_msg = f'{self.name_output()} НЕ доступен для взаимодействия{strict_msg}'
                elif isinstance(result, ElementClickInterceptedException):
                    rus_msg = f'{self.name_output()} перекрыт другим элементом{strict_msg}'
                elif isinstance(result, ElementNotVisibleException):
                    rus_msg = f'{self.name_output()} не отображается{strict_msg}'
                raise ElementException(msg=rus_msg or result.msg, element=self)
            raise result

    @property
    def is_present(self) -> bool:
        """Проверка наличия указанного объекта на текущей странице"""

        result, _ = self._return_property(lambda: self.webelement())
        return bool(result)

    @property
    def is_displayed(self) -> bool:
        """Воозвращает True, если webelement отображается для пользователя"""

        result, _ = self._return_property(lambda: self.webelement().is_displayed())
        return result

    @property
    def is_not_displayed(self) -> bool:
        """Отображается элемент или нет.
        Вернет True если элемент не виден пользователю
        """
        return not self.is_displayed

    @property
    def is_enabled(self) -> bool:
        """Возвращает True, если webelement доступен, False - нет"""

        return self._exec(lambda: self.webelement().is_enabled(), wait_time=0)

    @property
    def text(self) -> str:
        """Возвращает текст, который содержит webelement"""

        result = self._exec(lambda: self.webelement().text, wait_time=0)
        return result

    @property
    def coordinates(self) -> Dict[str, int]:
        """Возвращаем координаты webelement"""
        return self._exec(lambda: self.webelement().location, wait_time=0)

    @property
    def size(self) -> Dict[str, float]:
        """Возвращаем высоту и ширину объекта"""

        return self._exec(lambda: self.webelement().size, wait_time=0)

    @property
    def rect(self) -> Dict[str, float]:
        """Возвращаем координаты, высоту и ширину объекта"""

        return self._exec(lambda: self.webelement().rect, wait_time=0)

    @property
    def count_elements(self) -> int:
        """Количество элементов на странице"""

        result, _ = self._return_property(lambda: len(self.webelement(return_list=True)))
        if not result:
            result = 0
        return result

    @before_after
    def click(self: TypeSelf):
        """Производим клик по элементу
        Если клик не удался, то пытается сделать его self._wait_max секунд
        """

        self._exec(lambda: self.webelement().click())
        log("Клик по %s" % self.name_output(), "[a]")
        return self

    @before_after
    def clear(self: TypeSelf):
        """Метод для очистки поля"""

        self._exec(lambda: self.webelement().clear())
        log('Удален текст из %s' % self.name_output(), "[a]")
        return self

    def send_keys(self: TypeSelf, *args: str, action_chain=True):
        """Ввод комбинации клавиш, например, CTRL+a/CTRL+c

        :param args: Вводимые символы
        :param action_chain делать цепочку или просто ввести
        """

        if action_chain:
            action_atf = ActionChainsUATF(self.driver)
            for key in args:
                action_atf.send_keys_to_element(self, key)
            self._exec(action_atf.perform)
        else:
            self._exec(lambda: self.webelement().send_keys(*args))

        log(f"Ввели '{args}' в поле редактора")
        return self

    @before_after
    def type_in(self: TypeSelf, tmp_str: str, clear_txt=False):
        """Вводит текст в webelement, поле не очищается перед вводом

        :param tmp_str: тест для ввода
        :param clear_txt: очищать ли поле перед вводом текста
        """
        if clear_txt:
            self.clear()

        if tmp_str:
            self._exec(lambda: self.webelement().send_keys(tmp_str))
        log(f'Текст "{tmp_str}" введен  в элемент {self.name_output()}', "[a]")
        return self

    def get_attribute(self, attribute: str) -> str:
        """Возвращает значение указанного аттрибута
        :param attribute: атрибут элемента
        """

        return self._exec(lambda: self.webelement().get_attribute(attribute))

    @before_after
    def click_with_offset(self: TypeSelf, xoffset: int, yoffset: int):
        """Клик со смещением по координатам от центра элемента
        :param xoffset: смещение по оси x
        :param yoffset: смещение по оси y
        """

        action_chains = ActionChainsUATF(self.driver)

        def move_to_element(_xoffset: int, _yoffset: int) -> Any:
            """Наведение со смещением
            :param _xoffset: смещение по X
            :param _yoffset: смещение по Y
            """

            return self._exec(action_chains.move_to_element(self).move_by_offset(_xoffset, _yoffset).click().perform)

        size = self.size

        if xoffset > int(size['width'] / 2):
            move_to_element(int(size['width'] / 2 - 1), yoffset)
        elif yoffset > int(size['height'] / 2):
            move_to_element(xoffset, int(size['height'] / 2 - 1))
        else:
            move_to_element(xoffset, yoffset)

        return self

    def element(self, how: str, locator: str = None,
                element_type: Optional[Union[Type[TypeElement], Type['BaseElement']]] = None, **kwargs) \
            -> Union['TypeElement', 'BaseElement']:
        """Метод находит вложенный элемент в родительский элемент
        :param how: стратегия нахождения поиска
        :param locator: локатор
        :param element_type: тип вложенного элемента
        """
        if locator is None:
            locator = how
            how = By.CSS_SELECTOR
        if element_type is None:
            element_type = BaseElement
        child_element = element_type(how=how, locator=locator, rus_name=self.rus_name, **kwargs)
        child_element.add_parent(self)
        return child_element

    def should_be(self: TypeSelf, *conditions: Union[Condition, Type[Condition]], msg: str = '',
                  wait_time: Union[int, bool] = CONFIG.get("WAIT_SHOULD_BE_TIME", 'GENERAL')):
        """Проверка состояния элемента"""

        should_framework(
            *conditions, element=self, error_msg=msg, wait_time=wait_time
        )
        return self

    def should_not_be(self: TypeSelf, *conditions: Union[Condition, Type[Condition]], msg: str = '',
                      wait_time: Union[int, bool] = CONFIG.get("WAIT_SHOULD_BE_TIME", 'GENERAL')):
        """Проверка НЕ соответствия состояния элемента"""
        should_framework(
            *conditions, element=self, error_msg=msg, wait_time=wait_time, eth_result=False
        )
        return self

    def get_bound_with_indent(self, left=0, top=0, bottom=0, right=0):
        """Получаем границы элемента с отступом
        :param left - смещение по оси X влево
        :param top - смещение по оси Y вверх от элемента
        :param bottom - смещение по оси Y вниз от элемента
        :param right - смещение по оси X вправо от элемента
        """

        size = self.webelement().size
        coordinates = self.coordinates
        x = int(coordinates['x']) - left
        y = int(coordinates['y']) - top
        w = int(size['width']) + left + right
        h = int(size['height']) + top + bottom
        return x, y, w, h

    def get_bound_with_element(self, element, left=0, top=0, right=0, bottom=0):
        """Объединяет область двух элементов
        :param element: второй элемент
        :param left: увеличение скриншота влево
        :param top: увеличение скриншота вверх
        :param right: увеличение скриншота вправо
        :param bottom: увеличение скриншота вниз
        """

        coordinates1 = self.coordinates
        coordinates2 = element.coordinates
        size1 = self.webelement().size
        size2 = element.webelement().size

        # вычисляем правый верхний угол области скриншота
        x = int(min(coordinates1['x'], coordinates2['x']) - left)
        y = int(min(coordinates1['y'], coordinates2['y']) - top)

        # вычисляем ширину области в зависимости от того, какой элемент находится правее
        elem_1_right = coordinates1['x'] + size1['width']
        elem_2_right = coordinates2['x'] + size2['width']
        tmp_right = elem_1_right if elem_1_right >= elem_2_right else elem_2_right
        width = tmp_right - x + right

        # вычисляем высоту области в зависимости от того, какой элемент находится ниже
        elem_1_bottom = coordinates1['y'] + size1['height']
        elem_2_bottom = coordinates2['y'] + size2['height']
        tmp_bottom = elem_1_bottom if elem_1_bottom >= elem_2_bottom else elem_2_bottom
        height = tmp_bottom - y + bottom

        return {'left': x, 'top': y, 'width': width, 'height': height}

    def check_load(self, wait_time):
        """Пустышка для оверайда в других контролах, имплементирован для check_change"""
        return True

    def highlight_action(self, type_of_action=None, args=None) -> None:
        raise NotImplementedError('Необходимо имлементировать метод для унаследованного от BaseElement класса')
