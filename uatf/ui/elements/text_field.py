# -*- coding: utf-8 -*-
"""
Модуль реализующий работу с текстовыми полями
"""
from selenium.webdriver.common.keys import Keys

from .element import Element, before_after
from ...logfactory import log
from ..should_be import Displayed, Enabled


class TextField(Element):
    """Класс реализующий работу с текстовыми полями"""

    hot_keys = Keys.__dict__

    def __str__(self):
        return 'текстовое поле'

    @before_after
    def type_in(self, string='', clear_txt=True, human=False):
        """Вводит текст в webelement, поле не очищается перед вводом

        :param string: текст для ввода
        :param clear_txt: очищать ли поле перед вводом текста
        :param human: очищать как реальный пользователь
        """
        super().type_in(string, clear_txt, human)
        return self

    def float_type_in(self, string):
        """Вводит текст в поле с точкой

        :param string: текст для ввода (например, 5 000', '5000', '5 000.05', '0.50')
        """

        self.type_in(Keys.LEFT*3)  # встаем курсором перед точкой
        self.type_in(string, False)
        return self

    @before_after
    def human_type_in(self, string=''):
        """Ввод строчки в поле

        :param string: строка для ввода
        """
        self.type_in(string, human=True)
        return self

    @property
    def text(self):
        """Метод для получения текста."""

        result, _ = self._return_property(lambda: self.webelement().get_attribute("value"))
        if not result:
            result = ''
        return result

    @before_after
    def select_text(self, value, start=0):
        """Метод для выделения текста в поле.

        :param value: сколько символов выделяем
        :param start: позиция с которой начинаем выделять
        """

        keys = Keys.HOME + Keys.RIGHT*start + Keys.LEFT_SHIFT + Keys.RIGHT*value
        self._send_keys_wrapper(*keys, action_chain=False)
        log(f'Текст был выделен в {self.name_output()}', "[a]")
        return self

    @before_after
    def delete_text(self, value, start=0):
        """Метод для выделения части текста в поле и его удаления.

        :param value: сколько символов удаляем
        :param start: позиция с которой начинаем выделять
        """

        keys = Keys.HOME + Keys.RIGHT*start + Keys.LEFT_SHIFT + Keys.RIGHT*value + Keys.DELETE
        self._send_keys_wrapper(*keys, action_chain=False)
        log('Текст был удален из %s' % self.name_output(), "[a]")
        return self

    @before_after
    def copy_text(self, value, start=0):
        """Метод для выделения части текста в поле и его копирования в буфер ОС.

        :param value: - сколько символов копируем
        :param start: - позиция с которой начинаем выделять

        """
        keys = Keys.HOME + Keys.RIGHT*start + Keys.LEFT_SHIFT + Keys.RIGHT*value + Keys.CONTROL + Keys.INSERT
        self._send_keys_wrapper(*keys, action_chain=False)
        log(f'Текст был скопирован из {self.name_output()}', "[a]")
        return self

    def set_value(self, value, check=True):
        """Метод изменения value

        :param value: строка которую надо ввести
        :param check: нужно ли делать проверку
        """

        if check:
            self.should_be(Displayed, Enabled)
        self.driver.execute_script("arguments[0].value = arguments[1]", self.webelement(), value)
        return self
