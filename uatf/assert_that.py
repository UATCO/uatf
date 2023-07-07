"""
Модуль для работы с ассертами
"""
import difflib
import time
from copy import deepcopy
from typing import Any, Tuple, Union, Iterable, Callable
from xml.etree import ElementTree

from .logfactory import log
from .config import Config
from .exceptions import ElementException

__all__ = ('assert_that', 'instance_of', 'equal_to', 'equal_to_ignoring_case', 'is_not_in', 'and_wait',
           'not_equal', 'is_not', 'is_', 'is_in', 'is_in_ignoring_case',
           'less_than', 'less_than_or_equal_to', 'greater_than', 'greater_than_or_equal_to', 'equal_to_xml',
           'is_in_xml')

config = Config()


class WaitTime:
    """Класс создан для проверки написания ассерта
    Чтобы не писали так: assert_that(elm, is_displayed(), "Ошибка", and_wait(5))
    """

    def __init__(self, wait_time: Any, period: float):
        self.period = period
        if wait_time is True:
            self.wait_time = config.get('WAIT_ELEMENT_LOAD', 'GENERAL')
        elif isinstance(wait_time, (int, float)):
            self.wait_time = wait_time
        else:
            self.wait_time = 0


class BaseMatcher:
    max_length = 120

    def _matches(self, item: Any) -> Any:
        raise NotImplementedError('_matches')

    def matches(self, item: Any) -> Any:
        match_result = self._matches(item)
        return match_result

    def cut(self, value: str) -> str:
        """Урезаем вывод строки"""

        value = str(value)
        if config.get('TRUNCATE_ASSERT_LOGS', 'GENERAL') and len(value) > self.max_length:
            value = value[:self.max_length] + '...'
        return value

    @staticmethod
    def calc(value: Any) -> Any:
        """Вычисление значения"""

        if callable(value):
            value = value()
        return value


def check_args(arg1: Any, arg2: Any, desc: str, wait_time: Any) -> None:
    # второй аргумент всегда должен быть матчером
    if not isinstance(arg2, BaseMatcher):
        raise Exception('Не верное использование assert_that! '
                        'Второй агрумент должен быть матчером!')

    if not isinstance(desc, str):
        raise Exception('Не верное описание ошибки. '
                        'Описание должно быть строкой!')

    # проверка, что всегда пишется and_wait() или and_wait(5)
    if wait_time and not isinstance(wait_time, WaitTime):
        raise Exception('Не верное написание ассерта! '
                        'Допутимо указание ожидание только в функции and_wait')


try:
    from .ui.elements.base_element import BaseElement

    _check_args = check_args


    def check_args(arg1: Any, arg2: Any, desc: str, wait_time: Any) -> None:
        """Проверка соответствует ли вызов ассерта всем стандартам"""

        _check_args(arg1, arg2, desc, wait_time)

        if wait_time:
            if not isinstance(arg1, BaseElement) and not callable(arg1):
                if hasattr(arg2, 'item2'):
                    if not callable(arg2.item2):
                        raise Exception('Wait в assert_that не работает! '
                                        'Проверьте правильность написания assert')
except ImportError:
    pass


class GreaterThan(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2
        self.result = False
        self.description = ''

    def _matches(self, item1: Any) -> list:
        item2 = self.calc(self.item2)
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('item1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('item2 (%s) = %s' % (type2, item2))
        if type(item1) == type(item2):
            self.result = item1 > item2
            self.description = '\nСравнивали item1 > item2:\n{0}\n{1}'.format(arg1, arg2)
        else:
            self.description = '\nСравниваемые значения должны быть одного типа'
        return [self.result, self.description]


class GreaterThanOrEqualTo(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2
        self.result = False
        self.description = ''

    def _matches(self, item1: Any) -> list:
        item2 = self.calc(self.item2)
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('item1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('item2 (%s) = %s' % (type2, item2))
        if type(item1) == type(item2):
            self.result = item1 >= item2
            self.description = '\nСравнивали item1 >= item2:\n{0}\n{1}'.format(arg1, arg2)
        else:
            self.description = '\nСравниваемые значения должны быть одного типа'
        return [self.result, self.description]


class LessThan(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2
        self.result = False
        self.description = ''

    def _matches(self, item1: Any) -> list:
        item2 = self.calc(self.item2)
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('item1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('item2 (%s) = %s' % (type2, item2))
        if type(item1) == type(item2):
            self.result = item1 < item2
            self.description = '\nСравнивали item1 < item2:\n{0}\n{1}'.format(arg1, arg2)
        else:
            self.description = '\nСравниваемые значения должны быть одного типа'
        return [self.result, self.description]


class LessThanOrEqualTo(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2
        self.result = False
        self.description = ''

    def _matches(self, item1: Any) -> list:
        item2 = self.calc(self.item2)
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('item1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('item2 (%s) = %s' % (type2, item2))
        if type(item1) == type(item2):
            self.result = item1 <= item2
            self.description = '\nСравнивали item1 <= item2:\n{0}\n{1}'.format(arg1, arg2)
        else:
            self.description = '\nСравниваемые значения должны быть одного типа'
        return [self.result, self.description]


class EqualTo(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2

    def _matches(self, item1: Any) -> list:
        item2 = self.calc(self.item2)
        result = item1 == item2
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('arg1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('arg2 (%s) = %s' % (type2, item2))
        description = '\nСравнивались на равенство: \n%s\n%s' % (arg1, arg2)
        return [result, description]


class EqualToIgnoringCase(BaseMatcher):

    def __init__(self, item2: str):
        self.item2 = item2

    def _matches(self, item1: str) -> list:
        item2 = self.calc(self.item2)
        if not type(item1) == type(item2) == str:
            raise TypeError('Матчер equal_to_ignoring_case предназначен для строк')
        result = item1.lower() == item2.lower()
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('arg1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('arg2 (%s) = %s' % (type2, item2))
        description = '\nСравнивались на равенство БЕЗ учета регистра: ' \
                      '\n%s\n%s' % (arg1, arg2)
        return [result, description]


class IsInXML(BaseMatcher):

    def __init__(self, item2: Any, encoding: str = "utf-8", method: str = "xml"):
        self.encoding = encoding
        self.method = method
        if isinstance(item2, str):
            parser = ElementTree.XMLParser(encoding=encoding)
            root = ElementTree.fromstring(item2, parser=parser)
            self.item2 = root
        elif isinstance(item2, ElementTree.ElementTree):
            root = item2.getroot()
            self.item2 = root
        else:
            raise ValueError('Передан неверный тип {}'.format(type(item2)))

    def _matches(self, item1: Any) -> list:
        if isinstance(item1, str):
            parser = ElementTree.XMLParser(encoding=self.encoding)
            item1 = ElementTree.fromstring(item1, parser=parser)
        elif isinstance(item1, ElementTree.ElementTree):
            item1 = item1.getroot()

        item2 = self.item2
        item1, item2_copy = _delete_attribute_xml(item1, item2)

        # выравниваем xml
        prettify_xml(item1)
        prettify_xml(item2)

        str_item1: str = ElementTree.tostring(item1, encoding=self.encoding,
                                              method=self.method).decode(encoding=self.encoding)
        str_item2: str = ElementTree.tostring(item2, encoding=self.encoding,
                                              method=self.method).decode(encoding=self.encoding)

        result = str_item1 == str_item2
        if not result:
            diff = difflib.ndiff(str_item1.splitlines(True), str_item2.splitlines(True))
            diff_str = ''.join(diff)
        else:
            diff_str = ''
        description = '\nxml не равны: \n%s' % diff_str
        return [result, description]


def prettify_xml(element: Any, indent: int = 4) -> None:
    queue = [(0, element)]  # (level, element)
    str_indent: str = " " * indent
    while queue:
        level, element = queue.pop(0)
        element.attrib = dict(sorted(element.items()))
        children = []
        for child in list(element):
            child.attrib = dict(sorted(child.items()))
            children.append((level + 1, child))

        if children:
            element.text = '\n%s' % str_indent * (level + 1)  # for child open
        if queue:
            element.tail = '\n%s' % str_indent * queue[0][0]  # for sibling open
        else:
            element.tail = '\n%s' % str_indent * (level - 1)  # for parent close
        queue[0:0] = children  # prepend so children come before siblings


def _delete_attribute_xml(xml_1: Any, xml_2: Any, ignore_only: bool = False) -> Tuple[Any, Any]:
    """Удаляет игрнорируемые теги и чистит атрибуты зничения которых ignore
    :param xml_2: эталонный xml
    :param xml_1: сравниваемый xml
    :param ignore_only: удалить только игнорируемые теги
    """

    ignore_values = ('ignore',)  # значения в xml которые игнорируются при сравнении
    ignore_tags = ('ignore',)  # тэги в xml которые игнорируются при сравнении

    def delete_ignore_tags_in_list(tmp_xml_1: Any, tmp_xml_2: Any) -> Tuple[Any, Any]:
        """"""
        list1 = list(tmp_xml_1)
        list2 = list(tmp_xml_2)
        for index, value in enumerate(list2):
            try:
                delete_ignore_attribute_tag(list1[index], list2[index])
                if list(value):
                    _delete_attribute_xml(list1[index], list2[index], ignore_only)
                else:
                    delete_ignore_attribute_tag(list1[index], list2[index])
            except IndexError:
                pass
        return tmp_xml_1, tmp_xml_2

    def delete_value_in_list(tmp_xml_1: Any, tmp_xml_2: Any) -> Tuple[Any, Any]:
        list1 = list(tmp_xml_1)
        list2 = list(tmp_xml_2)
        for index, value in enumerate(list2):
            try:
                if value.tag in ignore_tags:
                    list1[index].clear()
                    list1[index].tag = "ignore"
                    list2[index].clear()
                elif list(value):
                    _delete_attribute_xml(list1[index], list2[index], ignore_only)
            except IndexError:
                pass
        return tmp_xml_1, tmp_xml_2

    def delete_ignore_attribute_tag(tag_1: Any, tag_2: Any) -> None:
        """Удаляет атрибуты значение которых ignore
        tag_2 - это эталон"""
        try:
            if tag_2.text.strip() == "ignore":
                tag_2.text = ""
                tag_1.text = ""
        except AttributeError:
            pass
        tmp_tag_2 = deepcopy(tag_2)
        for key, value in tmp_tag_2.items():
            if key in tag_1.keys():
                if key in ignore_tags or value in ignore_values:
                    tag_1.attrib.pop(key, None)
                    tag_2.attrib.pop(key, None)

    def delete_attribute_tag(tag_1: Any, tag_2: Any) -> None:
        """Удаляет атрибуты отсутствующие в теге эталона"""
        tmp_tag_1 = deepcopy(tag_1)
        for key, value in tmp_tag_1.items():
            if key not in tag_2.keys():
                tag_1.attrib.pop(key, None)

    if list(xml_1):  # есть ли дочерние элементы
        delete_ignore_attribute_tag(xml_1, xml_2)
        xml_1, xml_2 = delete_ignore_tags_in_list(xml_1, xml_2)
        if not ignore_only:
            delete_attribute_tag(xml_1, xml_2)
            delete_value_in_list(xml_1, xml_2)
    else:
        # дочерних элементов нет - затираем атрибуты значение которых ignore
        delete_ignore_attribute_tag(xml_1, xml_2)
        if not ignore_only:
            # удаляем все лишние атрибуты(оставляем только те, которые есть в эталоне)
            delete_attribute_tag(xml_1, xml_2)
    return xml_1, xml_2


class EqualToXML(BaseMatcher):

    def __init__(self, item2: Any, encoding: str = "utf-8", method: str = "xml"):
        self.encoding = encoding
        self.method = method
        if isinstance(item2, str):
            parser = ElementTree.XMLParser(encoding=encoding)
            root = ElementTree.fromstring(item2, parser=parser)
            self.item2 = root
        elif isinstance(item2, ElementTree.ElementTree):
            root = item2.getroot()
            self.item2 = root
        else:
            raise ValueError('Передан неверный тип {}'.format(type(item2)))

    def _matches(self, item1: Any) -> list:
        if isinstance(item1, str):
            parser = ElementTree.XMLParser(encoding=self.encoding)
            item1 = ElementTree.fromstring(item1, parser=parser)
        elif isinstance(item1, ElementTree.ElementTree):
            item1 = item1.getroot()

        item2 = self.item2
        item1, item2 = _delete_attribute_xml(item1, item2, True)

        # выравниваем xml
        prettify_xml(item1)
        prettify_xml(item2)

        str_item1: str = ElementTree.tostring(item1, encoding=self.encoding,
                                              method=self.method).decode(encoding=self.encoding)
        str_item2: str = ElementTree.tostring(item2, encoding=self.encoding,
                                              method=self.method).decode(encoding=self.encoding)
        result = str_item1 == str_item2
        if not result:
            diff = difflib.ndiff(str_item1.splitlines(True), str_item2.splitlines(True))
            diff_str = ''.join(diff)
        else:
            diff_str = ''
        description = '\nxml не равны: \n%s' % diff_str
        return [result, description]


class NotEqual(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2

    def _matches(self, item1: Any) -> list:
        item2 = self.calc(self.item2)
        result = item1 != item2
        type1 = type(item1)
        type2 = type(item2)
        arg1 = self.cut('arg1 (%s) = %s' % (type1, item1))
        arg2 = self.cut('arg2 (%s) = %s' % (type2, item2))
        description = '\nПроверялось НЕравенство: \n%s\n%s' % (arg1, arg2)
        return [result, description]


class Is(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2

    def _matches(self, item1: Any) -> Any:
        return self.item2.matches(item1)


class IsNot(BaseMatcher):

    def __init__(self, item2: Any):
        self.item2 = item2

    def _matches(self, item1: Any) -> Any:
        result = self.item2.matches(item1)
        if isinstance(result, list):
            result[0] = not result[0]
            return result
        else:
            return not result


def is_matchable_type(expected_type: Any) -> bool:
    if isinstance(expected_type, type):
        return True
    return False


class IsInstanceOf(BaseMatcher):

    def __init__(self, item2: Any):
        if not is_matchable_type(item2):
            raise TypeError('IsInstanceOf requires type')
        self.item2 = item2

    def _matches(self, item1: Any) -> bool:
        return isinstance(item1, self.item2)


class IsIn(BaseMatcher):

    def __init__(self, item2: Union[Iterable, Callable]):
        self.item2 = item2

    def _matches(self, item: Any) -> list:
        item2 = self.calc(self.item2)
        result = item in item2
        type1 = type(item)
        type2 = type(item2)
        arg1 = self.cut('arg1 (%s) = %s\n' % (type1, item))
        arg2 = self.cut('arg2 (%s) = %s\n' % (type2, item2))
        description = '\nПроверка вхождения arg1 в arg2:\n%s%s' % (arg1, arg2)
        return [result, description]


class IsInIgnoringCase(BaseMatcher):

    def __init__(self, item2: Iterable):
        self.item2 = item2

    def _matches(self, item: str) -> list:
        item2 = self.calc(self.item2)
        if type(item) == type(item2) == str:
            result = item.lower() in item2.lower()
            item = self.cut(item)
            item2 = self.cut(item2)
            description = '\nПроверка вхождения текста БЕЗ учета ' \
                          'регистра arg1:\n%s\nв arg2:\n%s' % (item, item2)
        elif type(item) == str and hasattr(item2, 'contains_text_ignoring_case'):
            result = item2.contains_text_ignoring_case(item)
            description = '\nПроверка вхождения текста в таблицу БЕЗ ' \
                          'учета регистра arg1 в arg2:\n%s%s' % (item, item2)
        else:
            raise TypeError('Матчер is_in_ignoring_case предназначен для строк или Table')
        return [result, description]


class IsNotIn(BaseMatcher):

    def __init__(self, item2: Iterable):
        self.item2 = item2

    def _matches(self, item: Any) -> list:
        item2 = self.calc(self.item2)
        result = item not in item2
        type1 = type(item)
        type2 = type(item2)
        arg1 = self.cut('arg1 (%s) = %s\n' % (type1, item))
        arg2 = self.cut('arg2 (%s) = %s\n' % (type2, item2))
        description = '\nПроверка отсутствия вхождения arg1 в arg2:\n%s%s' % (arg1, arg2)
        return [result, description]


def assert_that(arg1: Any, arg2: Any, desc: str, wait_time: Any = 0) -> None:
    """Комплексные ассерты
    :param arg1: первый аргумент сравнения (что сравниваем)
    :param arg2: второй аргумент сравнения (с чем сравниваем)
    :param desc: текстовое описание ошибки
    :param wait_time:  разрешено только передавать and_wait()/and_wait(5)

    """
    waiting_time = wait_time
    try:
        check_args(arg1, arg2, desc, wait_time)
    except ImportError:
        pass

    if wait_time and isinstance(wait_time, WaitTime):
        waiting_time = time.time() + wait_time.wait_time

    while True:
        error = None
        try:
            item = arg1
            if callable(item):
                item = item()

            _assert_match(actual=item, matcher=arg2, reason=desc)
            break
        except Exception as err:
            error = err
            if time.time() > waiting_time:
                break

            if wait_time and isinstance(wait_time, WaitTime):
                time.sleep(wait_time.period)

    if error:
        # патчим exception для UI
        try:
            from .ui.elements import Element
            if isinstance(arg1, Element):
                error = ElementException(error.args[0], element=arg1)
        except ImportError:
            pass
        raise error

    log('Проверка пройдена: %s' % desc, '[ch]')


def _assert_match(actual: Any, matcher: BaseMatcher, reason: str) -> None:
    rslt = matcher.matches(actual)

    if isinstance(rslt, bool):
        if not rslt:
            raise AssertionError(reason + "\n")
    elif not rslt[0]:
        msg = reason + "\n" + rslt[1].strip()
        raise AssertionError(msg)


def instance_of(atype: Any) -> IsInstanceOf:
    return IsInstanceOf(atype)


def wrap_matcher(x: Any) -> BaseMatcher:
    if isinstance(x, BaseMatcher):
        return x
    else:
        return equal_to(x)


def equal_to(obj: Any) -> EqualTo:
    """Сравнение двух объектов на равенство

    :param obj: объект для сравнения

    Примеры::

        a = 5
        b = 6
        assert_that(a, equal_to(b), 'Текстовое описание ошибки') # упадет
        assert_that(a, equal_to(5), 'Текстовое описание ошибки') # не упадет

        a = {'width':1, 'left':1, 'height':2}
        b = {'width':1, 'height':2, 'left':1}
        assert_that(a, equal_to(b), 'Текстовое описание ошибки') # не упадет
        b = {'width':1, 'height':2, 'left':2}
        assert_that(a, equal_to(b), 'Текстовое описание ошибки') # упадет
    """
    return EqualTo(obj)


def wrap_value_or_type(x: Any) -> BaseMatcher:
    if is_matchable_type(x):
        return instance_of(x)
    else:
        return wrap_matcher(x)


def equal_to_ignoring_case(obj: str) -> EqualToIgnoringCase:
    """Сравнение двух объектов на равенство

    :param obj: объект для сравнения
    """
    return EqualToIgnoringCase(obj)


def equal_to_xml(obj: Any) -> EqualToXML:
    """Сравнение два XML на равенство
    **
    :param obj: объект для сравнения
    """
    return EqualToXML(obj)


def is_in_xml(obj: Any) -> IsInXML:
    """Сравнение два XML на вхождение эталонного в тестируемый

    :param obj: объект для сравнения
    """
    return IsInXML(obj)


def not_equal(obj: Any) -> NotEqual:
    """Сравнение двух объектов на неравенство

    :param obj: объект для сравнения

    Примеры::

        a = 5
        b = 6
        assert_that(a, not_equal(b), 'Текстовое описание ошибки') # не упадет
        assert_that(a, not_equal(5), 'Текстовое описание ошибки') # упадет

        a = {'width':1, 'left':1, 'height':2}
        b = {'width':1, 'height':2, 'left':1}
        assert_that(a, not_equal(b), 'Текстовое описание ошибки') # упадет
        b = {'width':1, 'height':2, 'left':2}
        assert_that(a, not_equal(b), 'Текстовое описание ошибки') # не упадет
    """
    return NotEqual(obj)


def is_not(x: Any) -> IsNot:
    """Сравнение объекта и логического отрицания x

    :param x: объект для сравнения (обычно это True или False)

    Примеры::

        a = True
        b = False
        assert_that(a, is_not(b), 'Текстовое описание ошибки') # не упадет
        b = True
        assert_that(a, is_not(b), 'Текстовое описание ошибки') # упадет
    """
    return IsNot(wrap_value_or_type(x))


def is_(x: Any) -> Is:
    """Сравнение объекта и x

    :param x: объект для сравнения (обычно это True или False)
    """
    return Is(wrap_value_or_type(x))


def is_in(sequence: Union[Iterable, Callable]) -> IsIn:
    """Проверка вхождения объекта в sequence

    :param sequence: объект для сравнения

    Примеры::

        a = 'очная'
        b = 'проверочная строка'
        assert_that(a, is_in(b), 'Текстовое описание ошибки') # не упадет
        a = 'очная1'
        assert_that(a, is_in(b), 'Текстовое описание ошибки') # упадет
    """
    return IsIn(sequence)


def is_in_ignoring_case(sequence: str) -> IsInIgnoringCase:
    """Проверка вхождения объекта в sequence

    :param sequence: объект для сравнения
    """
    return IsInIgnoringCase(sequence)


def is_not_in(sequence: Any) -> IsNotIn:
    """Проверка отсутствия вхождения объекта в sequence

    :param sequence: объект для сравнения

    Пример::

        a = 'очная'
        b = 'проверочная строка'
        assert_that(a, is_not_in(b), 'Текстовое описание ошибки') # упадет
        a = 'очная1'
        assert_that(a, is_not_in(b), 'Текстовое описание ошибки') # не упадет
    """
    return IsNotIn(sequence)


def greater_than(obj: Any) -> GreaterThan:
    """item1 > item2

    :param obj: объект для сравнения

    Примеры::

        a = 5
        b = 6
        assert_that(a, more_than(4), 'Текстовое описание ошибки') # не упадет
        assert_that(a, more_than(b), 'Текстовое описание ошибки') # упадет

        a = '55'
        assert_that(a, more_than('b'), 'Текстовое описание ошибки') # не упадет
        assert_that(a, more_than('aaa'), 'Текстовое описание ошибки') # упадет
    """
    return GreaterThan(obj)


def greater_than_or_equal_to(obj: Any) -> GreaterThanOrEqualTo:
    """item1 >= item2

    :param obj: объект для сравнения

    Примеры::

        a = 5
        b = 6
        assert_that(a, more_than_strict(4), 'Текстовое описание ошибки') # не упадет
        assert_that(a, more_than_strict(b), 'Текстовое описание ошибки') # упадет

        a = '5'
        assert_that(a, more_than_strict('b'), 'Текстовое описание ошибки') # не упадет
        assert_that('55', more_than_strict('a'), 'Текстовое описание ошибки') # упадет
    """
    return GreaterThanOrEqualTo(obj)


def less_than(obj: Any) -> LessThan:
    """item1 < item2

    :param obj: объект для сравнения

    Примеры::

        a = 5
        b = 6
        assert_that(a, less_than(4), 'Текстовое описание ошибки') # упадет
        assert_that(a, less_than(b), 'Текстовое описание ошибки') # не упадет

        a = '55'
        assert_that(a, less_than('b'), 'Текстовое описание ошибки') # упадет
        assert_that(a, less_than('aaa'), 'Текстовое описание ошибки') # не упадет
    """
    return LessThan(obj)


def less_than_or_equal_to(obj: Any) -> LessThanOrEqualTo:
    """item1 <= item2

    :param obj: объект для сравнения

    Примеры::

        a = 5
        b = 6
        assert_that(a, less_than_strict(4), 'Текстовое описание ошибки') # упадет
        assert_that(a, less_than_strict(b), 'Текстовое описание ошибки') # не упадет

        a = '5'
        assert_that(a, less_than_strict('b'), 'Текстовое описание ошибки') # упадет
        assert_that('55', less_than_strict('a'), 'Текстовое описание ошибки') # не упадет
    """
    return LessThanOrEqualTo(obj)


def and_wait(wait_time: Any = True, period: float = 0.2) -> WaitTime:
    """Использовать ли в AssertThat wait

    :param wait_time:   время в сек. в течении которого присходит сравнение. Если не указано или True, то значение
                        ожидания берется из параметра WAIT_ELEMENT_LOAD файла настроек config.ini
    :param period:      время в сек. Период, с которым выполняется проверка assert (например кажую секунду)
    """
    return WaitTime(wait_time, period)
