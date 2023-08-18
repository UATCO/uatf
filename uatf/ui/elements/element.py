import os
import time
from hashlib import md5
from typing import TypeVar, Dict, Any, Optional, Callable, Union, Type

from selenium.common import WebDriverException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from .base_element import BaseElement, before_after
from ..actions_chains import ActionChainsUATF
from ...logfactory import log
from ...assert_that import *
from ...config import Config
from selenium.webdriver.remote.command import Command
from selenium.webdriver.common.utils import keys_to_typing

from ...helper import _wait

__all__ = ['Element', 'BaseElement']


CONFIG = Config()
HIGHLIGHT = CONFIG.get('HIGHLIGHT_ACTION', 'GENERAL')
LAST_RUN = not CONFIG.get('RESTART_AFTER_BUILD_MODE', 'GENERAL')

TypeElement = TypeVar('TypeElement', bound='Element')
TypeSelf = TypeVar('TypeSelf', bound='Element')


def format_locator(locator: str) -> str:
    """Форматирование локатора для мобильных проектов"""

    if CONFIG.get('BUNDLE_ID') and '{bundle_id}' in locator:
        locator = locator.format(bundle_id=CONFIG.get('BUNDLE_ID') + ':id/')
    return locator

class Element(BaseElement):
    """Базовый класс для всех элементов

    | Содержит в себе методы, которые актуальны для большинства наследников.
    | При этом сам может быть использован для моделирования в коде объектов,
    | которые не подходят ни под одного наследника. Типичные примеры:

    * блок страницы с картинкой
    * div, появления которого нужно просто дождаться
    """

    @property
    def is_readonly(self) -> bool:
        """Возвращает True, если элемент находится в режиме чтения"""

        result = self.get_attribute('readonly') == 'true'
        return result

    @property
    def text(self) -> str:
        """Возвращает текст, который содержит webelement"""

        result = super().text
        return result

    @property
    def coordinates(self) -> Dict[str, int]:
        """Возвращаем координаты webelement"""

        result = super().coordinates
        return result

    @property
    def size(self) -> Dict[str, float]:
        """Возвращаем высоту и ширину объекта"""

        result = super().size
        return result

    @property
    def rect(self) -> Dict[str, float]:
        """Возвращаем координаты, высоту и ширину объекта"""

        result = super().rect
        return result

    @property
    def location_once_scrolled_into_view(self) -> Dict[str, float]:
        """Возвращаем координаты webelement когда он будет видимый.

        Так же при получении этих координат происходит scroll
        элемента в видимую область
        """

        result = self._exec(lambda: self.webelement().location_once_scrolled_into_view, wait_time=0)
        if not result:
            result = {'x': 0, 'y': 0}
        return result

    @property
    def css_class(self) -> str:
        """Возвращает строку с css классами элемента"""

        return self.get_attribute('class')

    @property
    def inner_html(self) -> str:
        """Метод получает html код лежащий внутри webelement"""

        return self.get_attribute('innerHTML')

    @before_after
    def mouse_click(self: TypeSelf):
        """Производим клик по элементу (Элементу посылаем событие mouseDown)

        Если клик не удался, то пытается сделать его self._wait_max секунд
        """

        def action() -> None:
            """Нужен, для того, чтобы не возникало State Element Exception"""

            chain = ActionChainsUATF(self.driver)
            chain.click_and_hold(self).pause().release().perform()

        self._exec(action)
        log("Клик по %s" % self.name_output(), "[a]")
        return self

    @before_after
    def js_click(self: TypeSelf):
        """Клик через JS с игнорированием всех проверок"""

        self._exec(lambda: self.driver.execute_script("arguments[0].click()", self.webelement()))
        return self

    @before_after
    def middle_button_click(self: TypeSelf):
        """Производим клик по элементу средней кнопкой мыши"""

        def action() -> None:
            chain = ActionChainsUATF(self.driver)
            chain.middle_button_click(self).perform()

        self._exec(action)
        log(f"Клик средней кнопкой мыши по {self.name_output()}", "[a]")
        return self

    @before_after
    def clear(self: TypeSelf, human: bool = False):
        """Метод для очистки поля"""

        def action():
            webelement = self.webelement()
            webelement.send_keys(Keys.CONTROL, 'a')
            webelement.send_keys(Keys.DELETE)

        if not human:
            self._exec(lambda: self.webelement().clear())
        else:
            self._exec(lambda: action())
        log('Удален текст из %s' % self.name_output(), "[a]")
        return self

    @before_after
    def type_in(self: TypeSelf, tmp_str: str, clear_txt=False, human=False):
        """Вводит текст в webelement, поле не очищается перед вводом

        :param tmp_str: тест для ввода
        :param clear_txt: очищать ли поле перед вводом текста
        :param human посимвольный ввод
        """
        if clear_txt:
            self.clear(human)

        if human and type(human) == bool:
            human = 0.05

        hot_keys = dict()
        for hot_key, value in Keys.__dict__.items():
            if not hot_key.startswith('__'):
                hot_keys[hot_key] = value

        if tmp_str:
            if not human:
                self._exec(lambda: self.webelement().send_keys(tmp_str))
            else:
                # ожидание для ввода 1 символа, т.к. поле может быть недоступно, потом без ожидания
                webelement = self.webelement()  # потенциально опасно, если во время ввода изменится страница
                self._exec(lambda: webelement.send_keys(tmp_str[0]))
                if len(tmp_str) > 1:
                    for sym in tmp_str[1:]:
                        time.sleep(human)
                        self._exec(lambda: webelement.send_keys(sym))

            if not (str(tmp_str)).isprintable():
                for hot_key, value in hot_keys.items():
                    if value in tmp_str:
                        tmp_str = tmp_str.replace(value, f' [hotkey] "{hot_key}" ')

        log(f'Текст "{tmp_str}" введен  в элемент {self.name_output()}', "[a]")
        return self

    @before_after
    def paste(self: TypeSelf):
        """Метод для вставки текста в поле из буффера через +v"""

        self._send_keys_wrapper(Keys.CONTROL, 'v')
        log(f'Текст вставлен в {self.name_output()}', "[a]")
        return self

    @before_after
    def insert(self: TypeSelf):
        """Метод для вставки текста в поле из буффера через Insert"""

        self._send_keys_wrapper(Keys.SHIFT, Keys.INSERT)
        log(f'Текст вставлен в {self.name_output()}', "[a]")
        return self

    @before_after
    def copy_to_clipboard(self: TypeSelf):
        """Метод для копирования текста из поля в буффер"""

        self._send_keys_wrapper(Keys.CONTROL, 'c', to_element=False)
        log(f'Текст из {self.name_output()} скопировали в буфер обмена', "[a]")
        return self

    @before_after
    def select_to_the_left(self: TypeSelf):
        """Метод для выделения текста слева от каретки"""

        self._send_keys_wrapper(Keys.SHIFT, Keys.HOME)
        log(f'Текст левее каретки в {self.name_output()} выделен', "[a]")
        return self

    @before_after
    def select_all_text(self: TypeSelf):
        """Метод для выделения текста в элементе"""

        self._send_keys_wrapper(Keys.CONTROL, 'a')
        log(f'Текст в элементе {self.name_output()} выделен', "[a]")
        return self

    @before_after
    def delete_line(self: TypeSelf):
        """Метод для удаления текста в строке"""

        self._send_keys_wrapper(Keys.HOME, Keys.SHIFT, Keys.END, Keys.DELETE)
        log(f'Текст в строке {self.name_output()} удален', "[a]")
        return self

    @before_after
    def upload_file(self: TypeSelf, file_path: str):
        """Загрузка файла в поле"""

        def _convert(path):
            if os.sep == '\\':
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')
            return path

        # для запуска тестов на разных платформах и чтобы не править пути в конфигах
        file_path = _convert(file_path)

        element = self.webelement()
        remote_upload = False

        # чтобы загрузить >1 файла в docker, код взят из selenium 4.0
        if element.parent._is_remote:
            local_files = []
            for keys_to_send in file_path.split('\n'):
                local_files.append(element.parent.file_detector.is_local_file(str(keys_to_send)))

            if None not in local_files:
                remote_upload = True

                remote_files = []
                for file in local_files:
                    remote_files.append(element._upload(file))

                value = '\n'.join(remote_files)

                def exec_command():
                    self.webelement()._execute(Command.SEND_KEYS_TO_ELEMENT,
                                               {'text': "".join(keys_to_typing(value)), 'value': keys_to_typing(value)})

                self._exec(exec_command)

        if not remote_upload:
            self._exec(lambda: self.webelement().send_keys(file_path))
        log('Загрузили файл {0} в поле {1}'.format(file_path, self.name_output()), '[a]')
        return self

    @before_after
    def mouse_over(self: TypeSelf):
        """Наводит указатель мыши на webelement"""

        if not CONFIG.get('BROWSER', 'GENERAL'):
            def action() -> None:
                """Нужен, для того, чтобы не возникало State Element Exception"""

                chain = ActionChainsUATF(self.driver)
                chain.move_to_element(self).perform()

            self._exec(action)
        else:
            self.mouse_over_with_offset()
        return self

    @before_after
    def mouse_over_with_offset(self: TypeSelf, x: int = 1, y: int = 1):
        """Наводит указатель мыши на webelement"""

        def action() -> None:
            """Нужен, для того, чтобы не возникало State Element Exception"""

            chain = ActionChainsUATF(self.driver)
            chain.move_to_element(self).move_by_offset(x, y).perform()

        self._exec(action)
        return self

    @before_after
    def double_click(self: TypeSelf):
        """Делает даблклик по webelement"""

        chain = ActionChainsUATF(self.driver)
        self._exec(chain.double_click(self).perform)

        return self

    @before_after
    def context_click(self: TypeSelf):
        """ Клик правой кнопкой мыши по элементу"""

        chain = ActionChainsUATF(self.driver)
        self._exec(chain.move_to_element(self).context_click().perform)
        return self

    def scroll_into_view(self) -> 'Element':
        """Скроллит страницу делая элемент видимым
        """

        chain = ActionChainsUATF(self.driver)
        chain.chain.scroll_to_element(self.webelement())
        return self

    def mouse_scroll(self, direction: int) -> 'Element':
        """Делает скролл внутри webelement.
        Особое событие DOMMouseScroll. Применяется пока только .ws-date-range-menu-block

        :param direction - направление 1 - вверх, -1 вниз
        """
        js_script = "var evt = document.createEvent('MouseEvents'); " \
                    "evt.initMouseEvent('DOMMouseScroll', true, true, window, %s, 0, 0, 0, 0, 0, 0, 0, 0, 0, null); " \
                    "arguments[0].dispatchEvent(evt);" % direction
        self._exec(lambda: self.driver.execute_script(js_script, self.webelement()))
        log("Сделали scroll внутри элемента %s" % self.name_output(), "[a]")
        return self

    def has_css_class(self, css_class: str, search_up=True) -> bool:
        """Проверяет наличие css класса у элемента и его родителей или дочерних

        :param
        :css_class - класс, который ищем
        :dom_up    - стратегия поиска
            :True  - ищет у родителей и элемента
            :False - ищет у дочерних и элемента
        """

        # локатор ищет классы в текущем элементе и в родителях  - if
        # локатор ищет классы в текущем элементе и в дочерних   - else
        if search_up:
            locator = './ancestor-or-self::*[contains(@class, "%s")]' % css_class
        else:
            locator = './descendant-or-self::*[contains(@class, "%s")]' % css_class
        result = self._exec(lambda: self.webelement().find_elements(By.XPATH, locator))
        if len(result) > 0:
            result = True
        else:
            result = False
        return result

    def css_of_property(self, value: str) -> str:
        """Получает зачение css свойства webelement

        :param value: css свойство
        """
        return self._exec(lambda: self.webelement().value_of_css_property(value))

    @before_after
    def set_coordinates(self, top: float = 0, left: float = 0) -> None:
        """Получаем смещение элемента относительно экрана

        :param top: Верхняя координата смещения элемента
        :param left: Левая координата смещения элемента
        """

        log("Меняем координаты элемента с локатором {0} на экране".format(self.locator), "[a]")
        el = self.webelement()
        start_coord = self.coordinates
        coordinates = "{" + "'top':{0}, 'left':{1}".format(top, left) + "}"
        tmp_script = """jQuery(arguments[0]).offset({0})""".format(coordinates)
        self._exec(lambda: self.driver.execute_script(tmp_script, el))
        assert_that(lambda: self.coordinates, not_equal(start_coord),
                    "Не смогли изменить координаты элемента", and_wait(2))

    def get_node_bottom(self) -> Any:
        """Возвращает значение bottom элемента"""

        webelement = self.webelement()
        result = self.driver.execute_script(
            "return arguments[0].getClientRects()[0].bottom;", webelement
        )
        return result

    @before_after
    def click_with_ctrl(self: TypeSelf):
        """Клик с зажатым ctrl по webelement"""

        ctrl = Keys.CONTROL
        chain = ActionChainsUATF(self.driver)
        self._exec(chain.key_down(ctrl).click(self).key_up(ctrl).perform)
        log("Сделали клик с зажатым ctrl по элементу %s" % self.name_output(), "[a]")
        return self

    @before_after
    def drag_and_drop(self: TypeSelf, to_element: 'Element'):
        """Перетаскиваем webelement на указанный элемент.

        :param to_element: элемент на который перетаскиваем
        """

        chain = ActionChainsUATF(self.driver)
        self._exec(chain.drag_and_drop(self, to_element).perform)
        return self

    @before_after
    def drag_and_drop_by_offset(self: TypeSelf, x: int, y: int):
        """Перетаскиваем webelement на указанные координаты

        :param x: координата по оси x
        :param y: координата по оси y

        """
        chain = ActionChainsUATF(self.driver)

        def action() -> Any:
            return chain.click_and_hold(self).move_by_offset(x, y).release().perform()

        self._exec(action)
        return self

    @before_after
    def drag_and_drop_to_element_by_offset(self: TypeSelf, to_element: 'Element', x: int, y: int):
        """Перетаскиваем webelement на указанные координаты относительно другого элемента

        :param x: координата по оси x
        :param y: координата по оси y
        :param to_element: элемент, относительно которого пермещаем
        """

        def action() -> Any:
            chain_atf = ActionChainsUATF(self.driver)
            return chain_atf.click_and_hold(self).move_to_element(to_element). \
                move_to_element_corner_with_offset(to_element, x, y).release().perform()

        self._exec(action)
        return self

    @before_after
    def move_to_element_with_offset(self: TypeSelf, x: int, y: int):
        """Переместить курсор мыши на смещение относительно левого верхнего угла элемента

        :param x смещение по оси X
        :param y смещение по оси Y
        """

        def action() -> Any:
            chain_atf = ActionChainsUATF(self.driver)
            return chain_atf.move_to_element_with_offset(self, x, y).perform()

        self._exec(action)
        return self

    @before_after
    def move_to_element_corner_with_offset(self: TypeSelf, x: int, y: int):
        """Переместить курсор мыши на смещение относительно левого верхнего угла элемента
        * для перехода на selenium 4

        :param x смещение по оси X
        :param y смещение по оси Y
        """

        def action() -> Any:
            chain_atf = ActionChainsUATF(self.driver)
            return chain_atf.move_to_element_corner_with_offset(self, x, y).perform()

        self._exec(action)
        return self

    @property
    def tag_name(self) -> str:
        """Получение tag"""

        result = self._exec(lambda: self.webelement().tag_name, wait_time=0)
        if not result:
            result = ''
        return result

    @property
    def is_active(self) -> bool:
        """Проверка сфокусирован ли элемент
        https://developer.mozilla.org/ru/docs/Web/API/Document/activeElement
        """
        return self.webelement() == self.driver.switch_to.active_element

    def execute_js_script_on_control(self, script: str, return_result: bool = True) -> Any:
        """Вызов js кода у контрола
        Метод сам сделает jQuery(localor).wsControl().%ваш script%

        :param return_result: возвращать результат
        :param script: js script
        """

        locator = self.locator.replace("'", '"')
        script = script.replace("'", '"')
        if self.how != By.XPATH:
            executed_script = "$(\' {0} \' ).wsControl().{1}".format(locator, script)
        else:
            executed_script = "$x(\' {0} \' ).wsControl().{1}".format(locator, script)

        if _wait(lambda: self.is_present, 1) is True:
            try:
                _return = "return " if return_result else ""
                result = self.driver.execute_script(
                    "{0}jQuery(arguments[0]).wsControl().{1}".format(_return, script), self.webelement()
                )
                log('Выполнили js код: \n%s' % executed_script, "[a]")
                return result
            except WebDriverException as error:
                raise WebDriverException('Не смогли вызвать js скрипт у контрола\nScript: {0}\nException: {1}'.format(
                    executed_script, error.msg)
                )
        else:
            raise NoSuchElementException('Не найден элемент {0} в DOM дереве'.format(self.name_output()))

    def highlight(self) -> 'Element':
        """Подсветка конткретного элемента
        Метод создан для отладки
        """
        self.driver.execute_script("arguments[0].style.border = '5px solid red'", self.webelement())
        return self

    @staticmethod
    def convert_keys_string(*args: str) -> str:
        """Метод нужен для преобразования ЗНАЧЕНИЯ Keys.ЧТО_ТО в СТРОКУ Keys.ЧТО_ТО"""

        actions = {v: k for k, v in Keys.__dict__.items()}
        output = []
        for key in args:
            if key in actions:
                output.append('Keys.%s' % actions[key])
            else:
                output.append(str(key))
        return ' + '.join(output)

    def _send_keys_wrapper(self, *args: str, to_element: bool = True, action_chain=True):
        """Базовый метод по вводу без логирования
        :param args: Вводимые символы
        :param to_element: вводить в элемент, иногда может мешать, т.к. кликает в него
        :param action_chain делать цепочку или просто ввести
        """
        action_keys = (Keys.SHIFT, Keys.CONTROL, Keys.ALT, Keys.COMMAND)

        if action_chain:
            action_atf = ActionChainsUATF(self.driver)
            for key in args:
                if key in action_keys:
                    action_atf.key_down(key)
                else:
                    if to_element:
                        action_atf.send_keys_to_element(self, key)
                    else:
                        action_atf.send_keys(key)
            for key in args[::-1]:
                if key in action_keys:
                    action_atf.key_up(key)
            self._exec(action_atf.perform)
        else:
            self._exec(lambda: self.webelement().send_keys(*args))

    def send_keys(self: TypeSelf, *args: str, to_element: bool = True):
        """Ввод комбинации клавиш, например, CTRL+a/CTRL+c
        :param args: Вводимые элементы
        :param to_element: вводить в элемент, иногда может мешать, т.к. кликает в него
        """

        self._send_keys_wrapper(*args, to_element=to_element)
        log(f"Ввели '{self.convert_keys_string(*args)}' в поле редактора")
        return self

    @property
    def hash_inner_html(self) -> str:
        """Возвращает хэш текущего состояния списка"""
        return md5(self.inner_html.encode('utf-8')).hexdigest()

    def check_change(self: TypeSelf, action: Optional[Callable] = None, wait_time=True):
        """ Проверка изменения списка

            :param action: действие, выполняемое для изменения списка
            :param wait_time: Ожидание загрузки списка, если True, то ждет WAIT_ELEMENT_LOAD
        """

        hash_inner_html_before = self.hash_inner_html
        is_loading = getattr(self, '_is_loading', None)

        if action is not None:
            action()
            if is_loading:
                # True loading  / None not have data source
                _wait(lambda: is_loading() is not False, 1)

        self.check_load(wait_time)
        assert_that(lambda: self.hash_inner_html, not_equal(hash_inner_html_before),
                    f'Элемент "{self.name_output()}" не изменился', and_wait(wait_time))
        return self

    def check_not_change(self: TypeSelf, action: Optional[Callable] = None):
        """ Проверка неизменяемости списка

            :param action: выполняемое действие
        """

        hash_inner_html_before = self.hash_inner_html

        if action is not None:
            action()

        self.check_load(True)
        assert_that(self.hash_inner_html, equal_to(hash_inner_html_before),
                    f'Элемент "{self.name_output()}" не должен был измениться')
        return self

    def highlight_action(self, type_of_action=None, args=None) -> None:
        """Подсветка элемента

        :param type_of_action: Тип подсвечиваемого действия
        :param args: Аргументы действия (например, для ввода текста - сам текст)
        """
        from ...ui.screen_capture import make_screen_for_gif
        try:
            self.driver.execute_script(
                "function setProperty(element, color) {element.style.outline = color};"
                "setProperty(arguments[0], '2px solid red');"
                "setTimeout(setProperty, 400, arguments[0], '')", self.webelement()
            )
            if CONFIG.get('SCREEN_CAPTURE', 'GENERAL'):
                make_screen_for_gif(driver=self.driver, element=self, type_of_action=type_of_action, data=args)

            value = CONFIG.get('DELAY_ACTION', 'GENERAL')
            if value:
                time.sleep(value)
                del value
        except WebDriverException:
            pass

    def element(self, how: str, locator: Optional[str] = None,
                element_type: Optional[Union[Type[TypeElement], Type['Element']]] = None, **kwargs) \
            -> Union['TypeElement', 'Element']:
        """Метод находит вложенный элемент в родительский элемент

        | Возможнен вызов метода с 1 параметром: element('ws-icon16')
        | Тогда стратегия поиска будет css selector
        """
        if element_type is None:
            element_type = Element
        return super().element(how=how, locator=locator, element_type=element_type, **kwargs)

    @before_after
    def swipe(self: TypeSelf):
        """Сделать свайп (мобильная адаптация)"""

        def action() -> Any:
            chain = ActionChainsUATF(self.driver)
            return chain.swipe(self).perform()

        self._exec(action)
        return self
