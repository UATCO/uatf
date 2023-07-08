"""
Модуль, реализующий работу со списком элементов

ElementList позволяет получить результат проверки сразу по всем проверяемым элементам, а не только по первому
не прошедшему проверку.

Note:: в список элементов можно передать только экземпляр класса, унаследованный от Element
Usage::
    el = ElementList(page.some_inp, page.some_link, region.some_table, region.some_custom_list)
    el.should_be(Displayed, msg='Элементы не отобразились', wait_time=True)
    do_something()
    el.should_be(Hidden, msg='Элементы не скрылись', wait_time=30)
"""
from typing import Union, Type, List, Tuple

from .element import Element
from ..should_be import Condition


class ElementList(list):
    """Класс группирует элементы для последовательного выполнения одинаковых действий"""

    wrong_elm_msg = 'В ElementList можно передать только экземпляр класса, унаследованного от Element'

    def __str__(self):
        return 'список элементов'

    def __init__(self, *elements: Element):
        for item in elements:
            self.__validate(item)
        super().__init__(elements)
        self.exceptions = []

    def should_be(self, *conditions: Union[Condition, Type[Condition]],
                  msg: str = '', wait_time: Union[int, bool] = 5) -> 'ElementList':
        """Проверяет состояние элементов ElementList"""
        return self.__exec('should_be', *conditions, msg=msg, wait_time=wait_time)

    def should_not_be(self, *conditions: Union[Condition, Type[Condition]],
                      msg: str = '', wait_time: Union[int, bool] = 5) -> 'ElementList':
        """Проверяет НЕ соответствие состояния элементов ElementList"""
        return self.__exec('should_not_be', *conditions, msg=msg, wait_time=wait_time)

    def append(self, item: Element):
        """Добавляет элемент в конец списка ElementList"""
        self.__validate(item)
        super().append(item)

    def extend(self, items: Union[List[Element], Tuple[Element]]):
        """Расширяет список ElementList элементами из items
        :param items: список либо кортеж элементов для вставки
        """
        for item in items:
            self.__validate(item)
        super().extend(items)

    def insert(self, index: int, item: Element):
        """Вставляет элемент на указанную позицию списка ElementList
        :param index: позиция в ElementList
        :param item: элемент для вставки
        """
        self.__validate(item)
        super().insert(index, item)

    def __call(self, elm: Element, method: str, *args, **kwargs) -> Element:
        """Вызывает указанный метод у элемента и фиксирует результат
        :param elm: элемент из списка self
        :param method: вызываемый у элемента метод
        :param args, kwargs: параметры метода
        """
        try:
            return getattr(elm, method)(*args, **kwargs)
        except (AssertionError, TypeError) as exc:
            self.exceptions.append(', '.join(exc.args))
        return elm

    def __get_errors(self):
        """Выводит все полученные исключения"""
        if self.exceptions:
            msg = '\n' + ''.join(self.exceptions)
            self.exceptions.clear()
            raise AssertionError(msg)

    def __exec(self, method: str, *args, **kwargs) -> 'ElementList':
        """Последовательно вызывает указанный метод у элементов self
        :param method: вызываемый у элементов метод
        :param args, kwargs: параметры вызываемого метода
        """
        if not self.__len__():
            raise ValueError('Вы пытаетесь вызвать метод у пустого списка элементов!')

        for elm in self:
            self.__call(elm, method, *args, **kwargs)

        self.__get_errors()
        return self

    def __validate(self, item) -> Element:
        """Проверяет, что переданный элемент является экземпляром класса, унаследованным от Element"""
        if not isinstance(item, Element):
            raise ValueError(self.wrong_elm_msg)
        return item

    def __setitem__(self, index: int, item: Element):
        """Определяет поведение при присвоении значения элементу списка ElementList по индексу
        :param index: позиция в ElementList
        :param item: значение, которое необходимо присвоить
        """
        self.__validate(item)
        super().__setitem__(index, item)
