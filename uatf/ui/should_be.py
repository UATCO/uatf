import re
import time
from abc import abstractmethod
from string import Template
from typing import Optional, Union, Type, Tuple
from selenium.common.exceptions import NoSuchElementException
from ..exceptions import ElementException, BrowserException
from ..config import Config

from ..logfactory import log


class Condition:
    """Класс для состояний"""
    is_element_present: Optional[bool] = None
    add_msg = True  # добавлять ли автосгенерированное сообщение в тело переданного сообщения

    def __init__(self):
        self.result = True  # для генерации правильного сообщения при отрицании
        self.positive_template = ''
        self.negative_template = ''

    @staticmethod
    @abstractmethod
    def match(value):
        pass


class Not(Condition):

    def __init__(self, condition: Union[Condition, type]):
        super().__init__()
        if hasattr(condition, 'result'):
            condition.result = False
        self.condition = condition

    @property
    def positive_template(self):
        return self.condition.positive_template

    @positive_template.setter
    def positive_template(self, value):
        pass

    @property
    def negative_template(self):
        return self.condition.negative_template

    @negative_template.setter
    def negative_template(self, value):
        pass

    def match(self, value):
        return not self.condition.match(value)


class CountWindows(Condition):
    """Проверяет количество открытых окон браузера"""

    def __init__(self, count):
        super().__init__()

        if type(count) != int:
            raise TypeError('Неверный тип, должен быть int')

        self.count = count
        self.msg = 'количество открытых окно'

        self.positive_template = Template('количество открытых окон браузера '
                                          'должно быть равно ${count}').safe_substitute(count=count)
        self.negative_template = Template('количество открытых окон браузера '
                                          'НЕ должно быть равно ${count}').safe_substitute(count=count)

    def match(self, element):
        if hasattr(element, 'count_windows'):
            current_count = element.count_windows
            current_result = current_count == self.count
            if self.result != current_result:
                self.positive_template = Template('Неверное количество открытых окон браузера\n'
                                                  'Эталон:  ${count}\n'
                                                  'Текущее: ${current_count}'). \
                    safe_substitute(current_count=current_count, count=self.count)
                self.negative_template = Template('Неверное количество открытых окон браузера\n'
                                                  'Должно быть НЕ РАВНО ${count}').safe_substitute(count=self.count)
            return current_result
        else:
            raise TypeError('Состояние предназначено для класса Browser')


class CountFrames(Condition):
    """Проверяет количество фреймов текущего окна"""

    def __init__(self, count):
        super().__init__()

        if type(count) != int:
            raise TypeError('Неверный тип, должен быть int')

        self.count = count
        self.positive_template = Template('количество фреймов '
                                          'должно быть равно ${count}').safe_substitute(count=count)
        self.negative_template = Template('количество фреймов '
                                          'НЕ должно быть равно ${count}').safe_substitute(count=count)

    def match(self, element):
        if hasattr(element, 'count_frames'):
            current_count = element.count_frames
            current_result = current_count == self.count
            if self.result != current_result:
                self.positive_template = Template('Неверное количество фреймов текущего окна\n'
                                                  'Эталон:  ${count}\n'
                                                  'Текущее: ${current_count}'). \
                    safe_substitute(current_count=current_count, count=self.count)
                self.negative_template = Template('Неверное количество количество фреймов текущего окна\n'
                                                  'Должно быть НЕ РАВНО ${count}').safe_substitute(count=self.count)
            return current_result
        else:
            raise TypeError('Состояние предназначено для класса Browser')


class UrlExact(Condition):
    """Проверяет точное совпадение эталонного текста и url текущего окна"""

    def __init__(self, text):
        super().__init__()

        self.text = text
        self.positive_template = Template('текущая ссылка должна иметь адрес ${text}').safe_substitute(
            text=self.text
        )
        self.negative_template = Template('текущая ссылка НЕ должна иметь адрес ${text}').safe_substitute(
            text=self.text
        )

    def match(self, element):
        if hasattr(element, 'current_url'):
            current_url = element.current_url
            current_result = current_url == self.text
            if self.result != current_result:
                self.positive_template = Template('Неверная ссылка в активной вкладке\n'
                                                  'Эталон:  ${text}\n'
                                                  'Текущая: ${current_url}'). \
                    safe_substitute(current_url=current_url, text=self.text)
                self.negative_template = Template('Неверная ссылка в активной вкладке\n'
                                                  'Ссылка НЕ должна быть равна ${count}'). \
                    safe_substitute(count=self.text)
            return current_result
        else:
            raise TypeError('Состояние предназначено для класса Browser')


class UrlContains(Condition):
    """Проверяет вхождение эталонного текста в url текущего окна"""

    def __init__(self, text):
        super().__init__()

        self.text = text
        self.positive_template = Template('текущая ссылка должна содержать текст ${text}').safe_substitute(
            text=self.text
        )
        self.negative_template = Template('текущая ссылка НЕ должна содержать текст ${text}').safe_substitute(
            text=self.text
        )

    def match(self, element):
        if hasattr(element, 'current_url'):
            current_url = element.current_url
            current_result = self.text in current_url
            if self.result != current_result:
                self.positive_template = Template('Неверная ссылка в активной вкладке\n'
                                                  'Эталон:  ${text}\n'
                                                  'Текущая: ${current_url}'). \
                    safe_substitute(current_url=current_url, text=self.text)
                self.negative_template = Template('Неверная ссылка в активной вкладке\n'
                                                  'НЕ должна содержать: ${text}\n'
                                                  'Текущая: ${current_url}'). \
                    safe_substitute(current_url=current_url, text=self.text)
            return current_result
        else:
            raise TypeError('Состояние предназначено для класса Browser')


class TitleExact(Condition):
    """Проверяет точное совпадение эталонного текста и title текущего окна"""

    def __init__(self, text):
        super().__init__()

        self.text = text
        self.positive_template = Template('активная вкладка должна иметь title ${text}').safe_substitute(
            text=self.text
        )
        self.negative_template = Template('активная вкладка НЕ должна иметь title ${text}').safe_substitute(
            text=self.text
        )

    def match(self, element):
        if hasattr(element, 'current_title'):
            current_title = element.current_title
            current_result = current_title == self.text
            if self.result != current_result:
                self.positive_template = Template('Неверный title активной вкладки\n'
                                                  'Эталон:  ${text}\n'
                                                  'Текущий: ${current_title}'). \
                    safe_substitute(current_title=current_title, text=self.text)
                self.negative_template = Template('Неверный title активной вкладки\n'
                                                  'Должен быть: ${text}'). \
                    safe_substitute(count=self.text)
            return current_result
        else:
            raise TypeError('Состояние предназначено для класса Browser')


class TitleContains(Condition):
    """Проверяет вхождение эталонного текста в title текущего окна"""

    def __init__(self, text):
        super().__init__()

        self.text = text
        self.positive_template = Template('title активной вкладки должен содержать текст ${text}').safe_substitute(
            text=self.text
        )
        self.negative_template = Template('title активной вкладки НЕ должен содержать текст ${text}').safe_substitute(
            text=self.text
        )

    def match(self, element):
        if hasattr(element, 'current_title'):
            current_title = element.current_title
            current_result = self.text in current_title
            if self.result != current_result:
                self.positive_template = Template('Неверный title активной вкладки\n'
                                                  'Эталон:  ${text}\n'
                                                  'Текущий: ${current_title}'). \
                    safe_substitute(current_title=current_title, text=self.text)
                self.negative_template = Template('Неверный title активной вкладки\n'
                                                  'НЕ должна содержать: ${text}\n'
                                                  'Текущая: ${current_title}'). \
                    safe_substitute(current_title=current_title, text=self.text)
            return current_result
        else:
            raise TypeError('Состояние предназначено для класса Browser')


class Options(Condition):
    """Проверяем все ли опции из списка есть в опциях элемента"""

    def __init__(self, options):
        super().__init__()

        self.options = options
        self.template = ''
        self.positive_template = Template(' ${element} должен иметь опции: ${options}').safe_substitute(
            options=str(options)
        )
        self.negative_template = Template(' ${element} НЕ должен иметь опции: ${options}').safe_substitute(
            options=str(options)
        )

    def match(self, element):
        try:
            options = element.get_options()
        except AttributeError:
            raise AttributeError('Вы используете состояние неправильно! У элемента нет метода get_options')
        for option in self.options:
            if (option in options) != self.result:
                self.positive_template = Template('У ${element} НЕТ опции: ${option}\n'
                                                  'В списке опций: ${options}').safe_substitute(option=option,
                                                                                                options=str(options))
                self.negative_template = Template('У ${element} НЕ должно быть опции: ${option}\n'
                                                  'В списке опций: ${options}').safe_substitute(option=option,
                                                                                                options=str(options))
                return False
        else:
            return True


class Attribute(Condition):
    """Проверяем наличие атрибутов у элемента"""

    def __init__(self, **kwargs):
        super().__init__()

        self.kwargs = kwargs
        self.positive_template = Template(' ${element} должен иметь атрибуты: ${attr}'). \
            safe_substitute(attr=str(self.kwargs))
        self.negative_template = Template(' ${element} НЕ должен иметь атрибуты: ${attr}'). \
            safe_substitute(attr=str(self.kwargs))

    def match(self, element):
        for key, value in self.kwargs.items():
            current_value = element.get_attribute(key)
            current_result = current_value == self.kwargs.get(key)
            if current_result != self.result:
                self.positive_template = Template('У ${element} НЕ верное значение атрибута:\n'
                                                  'Эталон:  ${key} = ${value}\n'
                                                  'Текущее: ${key} = ${current_value}'). \
                    safe_substitute(key=key, value=value, current_value=current_value)
                self.negative_template = Template('У ${element} НЕ верное значение атрибута:\n'
                                                  'Должно быть: ${key} НЕ равно ${value}\n'
                                                  'Сейчас: ${key} = ${current_value}'). \
                    safe_substitute(key=key, value=value, current_value=current_value)
                return current_result
        else:
            return self.result


class CssClass(Condition):
    """Проверяем наличие класса у элемента"""

    def __init__(self, css_class):
        super().__init__()

        self.css_class = css_class
        self.positive_template = Template(' ${element} должен иметь css class "${css_class}"'). \
            safe_substitute(css_class=self.css_class)
        self.negative_template = Template(' ${element} НЕ должен иметь css class "${css_class}"'). \
            safe_substitute(css_class=self.css_class)

    def match(self, element):
        current_class_str = element.css_class
        current_class_lst = current_class_str.split()
        current_result = any((self.css_class == current_class.strip() for current_class in current_class_lst))
        if self.result != current_result:
            self.positive_template = Template('У ${element} НЕТ css class ${css_class}\n'
                                              'Текущие: ${current_class} '). \
                safe_substitute(css_class=self.css_class, current_class=current_class_str)
            self.negative_template = Template('У ${element} НЕ должно быть css class ${css_class}\n'
                                              'Текущие css class: ${current_class} '). \
                safe_substitute(css_class=self.css_class, current_class=current_class_str)
        return current_result


class ExactTextIgnoringCase(Condition):
    """Проверяем точное совпадение текста элемента с эталонным без учета регистра"""

    def __init__(self, text):
        super().__init__()

        self.text = text.lower()
        self.positive_template = Template(' ${element} должен иметь текст ${text} (ignore case)'). \
            safe_substitute(text=self.text)
        self.negative_template = Template(' ${element} НЕ должен иметь текст ${text} (ignore case)'). \
            safe_substitute(text=self.text)

    def match(self, element):
        element_text = _get_text_element(element).lower()
        current_result = self.text == element_text
        if current_result != self.result:
            self.positive_template = Template('У ${element} текст НЕ равен эталонному (case ignore)\n'
                                              'Эталонный: ${text}\n'
                                              'Текущий:   ${element_text}'). \
                safe_substitute(text=self.text, element_text=element_text)
            self.negative_template = Template('У ${element} текст должен быть НЕ равен эталонному '
                                              '(case ignore)\nЭталонный: ${text}\nТекущий: ${element_text}'). \
                safe_substitute(text=self.text, element_text=element_text)
        return current_result


def _get_text_element(element):
    if hasattr(element, 'current_text'):
        element_text = element.current_text
    else:
        element_text = element.text
    return element_text


class TextIgnoringCase(Condition):
    """Проверяем вхождение эталонного текста в текст элемента без учета регистра"""

    def __init__(self, text):
        super().__init__()

        self.text = text.lower()
        self.positive_template = Template(' ${element} должен иметь текст ${text}').safe_substitute(text=text)
        self.negative_template = Template(' ${element} НЕ должен иметь текст ${text}').safe_substitute(text=text)

    def match(self, element):
        element_text = _get_text_element(element).lower()
        current_result = self.text in element_text
        if current_result != self.result:
            self.positive_template = Template('У ${element} эталонный текст не найден (case ignore)\n'
                                              'Эталонный: ${text}\nТекущий: ${element_text}'). \
                safe_substitute(text=self.text, element_text=element_text)
            self.negative_template = Template('У ${element} НЕ должно быть текста (case ignore)\n'
                                              'Эталонный: ${text}\nТекущий: ${element_text}'). \
                safe_substitute(text=self.text, element_text=element_text)
        return current_result


class ExactText(Condition):
    """Проверяет точное совпадение эталонного текста и текста элемента"""

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.positive_template = Template(' ${element} должен иметь текст "${text}"').safe_substitute(
            text=self.text
        )
        self.negative_template = Template(' ${element} НЕ должен иметь текст "${text}"').safe_substitute(
            text=self.text
        )

    def match(self, element):
        element_text = _get_text_element(element)
        current_result = self.text == element_text

        if current_result != self.result:
            self.positive_template = Template('У ${element} эталонный текст НЕ равен текущему\n'
                                              'Эталонный: ${text}\n'
                                              'Текущий:   ${element_text}').safe_substitute(text=self.text,
                                                                                            element_text=element_text)
            self.negative_template = Template('У ${element} текст должен быть НЕ равен эталонному\n'
                                              'Эталонный: ${text}\n'
                                              'Текущий:   ${element_text}').safe_substitute(text=self.text,
                                                                                            element_text=element_text)
        return current_result


class ContainsText(Condition):
    """Проверяет вхождение эталонного текста в текст элемента"""

    def __init__(self, text):
        super().__init__()
        if not text:
            raise ValueError('Нет смысла проверять вхождение пустого текста в строку!')

        self.text = text
        self.positive_template = Template(' ${element} должен содержать текст "${text}"').safe_substitute(text=text)
        self.negative_template = Template(' ${element} НЕ должен содержать текст "${text}"').safe_substitute(text=text)

    def match(self, element):
        if hasattr(element, '__contains__'):
            current_result = self.text in element
            if current_result != self.result:
                self.positive_template = Template('В ${element} не найден текст ${text}').safe_substitute(
                    text=self.text
                )
                self.negative_template = Template('В ${element} НЕ должно быть '
                                                  'текста ${text}').safe_substitute(text=self.text)
        else:
            element_text = _get_text_element(element)
            current_result = self.text in element_text
            if current_result != self.result:
                tmp = Template('У ${element} эталонный текст не найден\nЭталонный: ${text}\nТекущий:   ${element_text}')
                self.positive_template = tmp.safe_substitute(element_text=element_text, text=self.text)
                self.negative_template = Template('У ${element} НЕ должно быть текста\n'
                                                  'Эталонный: ${text}\n'
                                                  'Текущий: ${element_text}').safe_substitute(element_text=element_text,
                                                                                              text=self.text)
        return current_result


class MatchRegex(Condition):
    """Проверяет соответствие текста элемента регулярному выражению"""

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.positive_template = Template('текст элемента ${element} должен соответствовать '
                                          'регулярному выражению "${text}"'). \
            safe_substitute(text=text)
        self.negative_template = Template('текст элемента ${element} НЕ должен соответствовать '
                                          'регулярному выражению "${text}"'). \
            safe_substitute(text=text)

    def match(self, element):
        element_text = _get_text_element(element)
        current_result = True if re.search(self.text, element_text) else False
        if current_result:
            self.positive_template = Template('Текст элемента ${element} не соответствует регулярному выражению\n'
                                              'Текущий: ${element_text}\n'
                                              'Шаблон regex: ${text}').safe_substitute(element_text=element_text,
                                                                                       text=self.text)
            self.negative_template = Template('Текст элемента ${element} НЕ должен соответствовать '
                                              'регулярному выражению\n'
                                              'Текущий: ${element_text}\n'
                                              'Шаблон regex: ${text}').safe_substitute(element_text=element_text,
                                                                                       text=self.text)
        return current_result


class Disabled(Condition):
    """Проверяем, что элемент недоступен для взаимодействия"""

    positive_template = ' ${element} должен быть disabled (недоступен для взаимодействия)'
    negative_template = ' ${element} НЕ должен быть disabled (недоступен для взаимодействия)'
    add_msg = False

    @staticmethod
    def match(value):
        return not value.is_enabled


class Enabled(Condition):
    """Проверяем, что элемент доступен для взаимодействия"""

    positive_template = ' ${element} должен быть enabled (доступен для взаимодействия)'
    negative_template = ' ${element} НЕ должен быть enabled (доступен для взаимодействия)'
    is_element_present = True

    @staticmethod
    def match(element):
        return element.is_enabled


class Readonly(Condition):
    """Проверяет, что элемент доступен только на просмотр (редактирование запрещено)"""

    positive_template = ' ${element} должен быть readonly (недоступен для редактирования)'
    negative_template = ' ${element} НЕ должен быть readonly (недоступен для редактирования)'
    add_msg = False

    @staticmethod
    def match(element):
        return element.is_readonly


class Empty(Condition):
    """Проверяет, что элемент пуст
    TextField, Text - текст пуст
    Table - таблица пуста
    """

    positive_template = ' ${element} должен быть пуст'
    negative_template = ' ${element} должен быть НЕ пустой'
    add_msg = False

    @staticmethod
    def match(element):
        result = element.text == ''
        return result


class Hidden(Condition):
    """Проверяет, что элемент невидимый"""

    positive_template = 'элемент ${element} НЕ должен отображаться'
    negative_template = 'элемент ${element} должен отображаться'
    is_element_present = False
    add_msg = False

    def __init__(self, element):
        super().__init__()
        self.element = element

    @staticmethod
    def match(element):
        return element.is_not_displayed


class Present(Condition):
    """Проверяет, что элемент есть в DOM дереве"""

    positive_template = ' ${element} нет в DOM дереве'
    negative_template = ' ${element} НЕ должно быть в DOM дереве'
    add_msg = False
    is_element_present = True

    def __init__(self, element):
        super().__init__()
        self.element = element

    @staticmethod
    def match(element):
        return element.is_present


class Displayed(Condition):
    """Проверяет, что элемент видимый"""

    positive_template = ' ${element} не отображается'
    negative_template = ' ${element} НЕ должен отображаться'
    is_element_present = True
    add_msg = False

    @staticmethod
    def match(element):
        return element.is_displayed


Visible = Displayed


class DisplayedMenu(Condition):
    """Проверяем, что у элемента открыто выпадающее меню"""

    positive_template = 'у ${element} должно быть открыто меню'
    negative_template = ' ${element} НЕ должно быть открыто меню'

    @staticmethod
    def match(element):
        assert hasattr(element, 'is_displayed_menu'), \
            'Вы используете состояние неправильно! У элемента НЕТ свойства is_displayed_menu'
        return element.is_displayed_menu


class Active(Condition):
    """Проверяет, что элемент активен (в фокусе)"""

    positive_template = ' ${element} не активен'
    negative_template = ' ${element} НЕ должен быть активен'
    add_msg = False

    @staticmethod
    def match(element):
        return element.is_active


class ValidationErrorMessage(Condition):
    """Проверка всплавающего текста у невалидного контрола"""

    def __init__(self, error):
        super().__init__()
        self.error = error
        self.positive_template = Template('у ${element} НЕ найдено сообщение '
                                          'валидации c текстом "${error}"').safe_substitute(error=self.error)
        self.negative_template = Template('у ${element} НЕ ДОЛЖНО быть сообщения '
                                          'валидации c текстом "${error}"').safe_substitute(error=self.error)

    def match(self, element):
        return element.validation_error_message(self.error)


class ValidationError(Condition):
    """Проверяет, что элемент невалидный"""

    positive_template = 'у ${element} НЕ найдена ошибка валидации'
    negative_template = 'у ${element} НЕ ДОЛЖНО быть ошибки валидации'
    add_msg = False

    @staticmethod
    def match(element):
        return element.validation_error


class CountElements(Condition):
    """Проверяет количество элементов в CustomList"""

    def __init__(self, count):
        super().__init__()
        if type(count) != int:
            raise TypeError('Неверный тип, должен быть int')

        self.count = count
        self.positive_template = Template('количество элементов (${element}) должно быть равно ${count}'). \
            safe_substitute(count=count)
        self.negative_template = Template('количество элементов (${element}) '
                                          'НЕ должно быть равно ${count}').safe_substitute(count=count)

    def match(self, element):
        current_count = element.count_elements
        current_result = current_count == self.count
        if self.result != current_result:
            self.positive_template = Template('Неверное количество элементов (${element})\n'
                                              'Эталон:  ${count}\n'
                                              'Текущее: ${current_count}'). \
                safe_substitute(current_count=current_count, count=self.count)
            self.negative_template = Template('Неверное количество элементов (${element})\n'
                                              'Должно быть НЕ РАВНО ${count}').safe_substitute(count=self.count)
        return current_result


class Size(Condition):
    """Проверяет размер элемента"""

    def __init__(self, width=None, height=None):
        super().__init__()
        if width is None and height is None:
            raise TypeError('Не задана высота или ширина')

        self.width = width
        self.height = height
        self.positive_template, self.negative_template = self._get_templates()

    def match(self, element):

        _size = element.size
        if self.width is not None and self.height is not None:
            current_result = (self.width, self.height) == (round(_size['width']), round(_size['height']))
        elif self.width is not None:
            current_result = self.width == round(_size['width'])
        else:
            current_result = self.height == round(_size['height'])
        if self.result != current_result:
            self.positive_template, self.negative_template = self._get_match_templates(_size)
        return current_result

    def _get_templates(self):

        if self.width is not None and self.height is not None:
            positive_t = 'Размеры элемента (${element}) должны быть равны ${width}x${height}'
            negative_t = 'Размеры элемента (${element}) НЕ должны быть равны ${width}x${height}'
        elif self.width is not None:
            positive_t = 'Ширина элемента (${element}) должна быть равна ${width}'
            negative_t = 'Ширина элемента (${element}) НЕ должна быть равна ${width}'
        else:
            positive_t = 'Высота элемента (${element}) должна быть равна ${height}'
            negative_t = 'Высота элемента (${element}) НЕ должна быть равна ${height}'
        positive = Template(positive_t).safe_substitute(width=self.width, height=self.height)
        negative = Template(negative_t).safe_substitute(width=self.width, height=self.height)
        return positive, negative

    def _get_match_templates(self, size):

        if self.width is not None and self.height is not None:
            positive_t = 'Неправильные размеры элемента (${element})\n' \
                         'Должны быть: ${width}x${height}\n' \
                         'Текущие    : ${current_width}x${current_height}'
            negative_t = 'Размеры элемента (${element}) НЕ должны быть равны ${width}x${height}'
        elif self.width is not None:
            positive_t = 'Неверная ширина элемента (${element})\n' \
                         'Должна быть: ${width}\n' \
                         'Текущая    : ${current_width}'
            negative_t = 'Ширина элемента (${element}) НЕ должна быть равна ${width}'
        else:
            positive_t = 'Неверная высота элемента (${element})\n' \
                         'Должна быть: ${height}\n' \
                         'Текущая    : ${current_height}'
            negative_t = 'Высота элемента (${element}) НЕ должна быть равна ${height}'

        data = {"width": self.width, "height": self.height,
                "current_width": int(size['width']), "current_height": int(size['height'])}
        positive = Template(positive_t).safe_substitute(**data)
        negative = Template(negative_t).safe_substitute(**data)
        return positive, negative


class Coordinates(Condition):
    """Проверяет координаты элемента"""

    def __init__(self, x=None, y=None):
        super().__init__()

        if x is None or y is None:
            raise TypeError('Не задана x или y координаты')

        self.x = x
        self.y = y
        self.positive_template, self.negative_template = self._get_templates()

    def match(self, element):

        _coordinates = element.coordinates
        if self.x is not None and self.y is not None:
            current_result = (self.x, self.y) == (_coordinates['x'], _coordinates['y'])
        elif self.x is not None:
            current_result = self.x == _coordinates['x']
        else:
            current_result = self.y == _coordinates['y']
        if self.result != current_result:
            self.positive_template, self.negative_template = self._get_match_templates(_coordinates)
        return current_result

    def _get_templates(self):

        if self.x is not None and self.y is not None:
            positive_t = 'Координаты элемента (${element}) должны быть равны ${x}x${y}'
            negative_t = 'Координаты элемента (${element}) НЕ должны быть равны ${x}x${y}'
        elif self.x is not None:
            positive_t = 'Координата элемента Х (${element}) должна быть равна ${x}'
            negative_t = 'Координата элемента Х (${element}) НЕ должна быть равна ${x}'
        else:
            positive_t = 'Координата элемента Y (${element}) должна быть равна ${y}'
            negative_t = 'Координата элемента Y (${element}) НЕ должна быть равна ${y}'

        data = {"x": self.x, "y": self.y}
        positive = Template(positive_t).safe_substitute(**data)
        negative = Template(negative_t).safe_substitute(**data)
        return positive, negative

    def _get_match_templates(self, size):

        if self.x is not None and self.y is not None:
            positive_t = 'Неправильные координаты элемента (${element})\n' \
                         'Должны быть: ${x}x${y}\n' \
                         'Текущие    : ${current_x}x${current_y}'
            negative_t = 'Координаты элемента (${element}) НЕ должны быть равны ${x}x${y}'
        elif self.x is not None:
            positive_t = 'Неверная координата X элемента (${element})\n' \
                         'Должна быть: ${x}\n' \
                         'Текущая    : ${current_x}'
            negative_t = 'Координата X элемента (${element}) НЕ должна быть равна ${width}'
        else:
            positive_t = 'Неверная координата Y элемента (${element})\n' \
                         'Должна быть: ${y}\n' \
                         'Текущая    : ${current_y}'
            negative_t = 'Координата Y элемента (${element}) НЕ должна быть равна ${height}'

        data = {"x": self.x, "y": self.y, "current_x": size['x'], "current_y": size['y']}
        positive = Template(positive_t).safe_substitute(**data)
        negative = Template(negative_t).safe_substitute(**data)
        return positive, negative


class CssProperty(Condition):
    """Проверяем наличие css-свойства у элемента"""

    def __init__(self, data=None, **kwargs):
        super().__init__()

        if not data and not kwargs:
            raise ValueError('Вы должны указать проверяемые свойства')

        self.data = data if data else {}
        if kwargs:
            self.data.update(kwargs)
        self.positive_template = ''
        self.negative_template = ''

    def match(self, element):
        miss = 0
        items = []
        for key, value in self.data.items():
            current = element.css_of_property(key)
            result = current == value
            if not result:
                miss += 1
            items.append((key, value, current))
        else:
            self._set_templates(items)
            if miss == 0:
                return True
            elif miss == len(self.data):
                return False
            else:
                return None

    def _set_templates(self, errors):
        positive = 'У элемента ${element} CSS свойства НЕ равны эталонным:\n\nСвойство: Эталон != Текущее\n'
        negative = 'У элемента ${element} CSS свойства НЕ должны быть равны эталонным:\n\nСвойство: Эталон == Текущее\n'
        positives = []
        negatives = []
        for key, value, current in errors:
            positives.append(Template('${key}: ${value} != ${current}')
                             .safe_substitute(key=key, value=value, current=current))
            negatives.append(Template('${key}: ${value} == ${current}')
                             .safe_substitute(key=key, value=value, current=current))
        self.positive_template = positive + '\n'.join(positives)
        self.negative_template = negative + '\n'.join(negatives)


def should_framework(*conditions: Union[Condition, Type[Condition]], element, error_msg='',
                     wait_time=5, eth_result=True):
    """
    Проверяет состояния, генерирует ошибки
    :param conditions: кортеж состояний
    :param element: экземпляр класса элемент
    :param error_msg: сообщение об ошибке
    :param wait_time: время ожидания
    :param eth_result: ожидаемый результат выполнения
    """

    assert conditions, 'Необходимо передать хотя бы 1 состояние!'

    if wait_time is True:
        wait_time = Config().options.get('WAIT_ELEMENT_LOAD', 'GENERAL')

    for condition in conditions:
        tmp_eth_result = eth_result

        # проверяем "Condition" ли нам скормили
        if not isinstance(condition, Condition):
            if type(condition) != type:
                raise TypeError('Вы передали should_be НЕ состояние!')
            elif not issubclass(condition, Condition):
                raise TypeError('Вы передали should_be НЕ состояние!')

        # для совместимости, т.к. работает не только с элементами теперь
        element_name = getattr(element, 'name_output', str)()

        # Считываем тут, чтобы они не изменились во время вычисления
        # Придется делать либо новые атрибуты, либо передавать, что ждем
        if tmp_eth_result:
            tmp_error_msg = Template(condition.positive_template).safe_substitute(element=element_name)
        else:
            # для случаев should_not
            tmp_error_msg = Template(condition.negative_template).safe_substitute(element=element_name)

        # вычисляем состояние
        result, exception = _execute(condition, element, tmp_eth_result, wait_time, error_msg, element_name)

        if result is not True:
            raise exception
        else:
            log('Проверка пройдена: %s' % tmp_error_msg, '[ch]')

    if error_msg.strip():
        log('Проверка пройдена: %s' % error_msg, '[ch]')


def _execute(condition: Condition, element, eth_result: bool,
             wait: int, err_msg: str, element_name: str) -> Tuple[bool, Optional[Exception]]:
    """Вычисление состояния"""

    is_wait = getattr(condition, 'wait', True)
    if not is_wait:
        # если в нашем условии нужна одна разовая проверка, то заменяем wait=0
        wait = 0
    end_time = time.time() + wait
    error = None
    while True:
        try:
            result = condition.match(element)
            if result is eth_result:
                highlight_should_be(condition, element, eth_result)
                return True, None
        except (ElementException, NoSuchElementException) as err:
            error = err
            if not eth_result:  # рейзим исключение для сохранения состояния
                return True, None
        except Exception as err:
            error = err

        if time.time() > end_time:
            break
        if wait:
            time.sleep(0.1)

    if error is None:  # если просто не дождались и не было исключений
        if eth_result:
            tmp_error_msg = Template(condition.positive_template).safe_substitute(element=element_name)
        else:
            # для случаев should_not
            tmp_error_msg = Template(condition.negative_template).safe_substitute(element=element_name)

        from .elements.element import BaseElement
        from .browser import Browser
        if condition.add_msg:
            if err_msg:
                err_msg += '\n'
            msg = (err_msg + tmp_error_msg).strip()
        else:
            msg = (err_msg or tmp_error_msg).strip()
        if isinstance(element, BaseElement):
            locator = element.locator_as_str()
            error = ElementException(f'{msg}\n{locator}', element=element)
        elif isinstance(element, Browser):
            error = BrowserException(msg)
        else:  # по идее такого быть не может, но обработать стоит
            error = AssertionError(msg)
    return False, error


CONFIG = Config()
SAVE_SUCCESSFUL_TEST_VIDEO = CONFIG.get('SCREEN_CAPTURE')


def highlight_should_be(condition, element, eth_result):
    """Декоратор выполнения действий до/после action

    """
    if SAVE_SUCCESSFUL_TEST_VIDEO == 'all':
        from .browser import Browser
        from ..screen_capture import DrawableType
        if not isinstance(element, Browser):
            condition_name = condition if type(condition) != Not else condition.condition
            action_name = None
            if (type(condition) == Not) ^ eth_result:
                action_name = DrawableType('should_be')
            else:
                if not condition_name.is_element_present:
                    action_name = DrawableType('should_not_be')
            if condition_name.is_element_present is not False and action_name:
                element.highlight_action(type_of_action=action_name, args=[condition_name, True])
