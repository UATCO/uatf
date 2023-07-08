# -*- coding: utf-8 -*-
"""
Матчеры для работы с элементами в assert_that
"""
from .elements import Element, TextField, Text
from ..assert_that import BaseMatcher


__all__ = ('is_displayed', 'is_empty', 'is_not_displayed', 'is_not_empty', 'is_not_present', 'is_present')


class IsEmpty(BaseMatcher):

    def _matches(self, item):
        if isinstance(item, (TextField, Text)):
            description = '\nПроверка отсутствия текста в поле'
            result = item.text == ''
        else:
            description = '\nМатчер предназначен проверки Table, TextField или Text! ' \
                          'Передан ' + item.__class__.__name__
            result = False
        return [result, description]


class IsNotEmpty(BaseMatcher):

    def _matches(self, item):
        result = False
        if isinstance(item, (TextField, Text)):
            description = '\nПроверка наличия текста в поле'
            result = item.text != ''
        else:
            description = '\nМатчер предназначен проверки таблиц! Передан ' + item.__class__.__name__
        return [result, description]


class IsPresent(BaseMatcher):

    def _matches(self, item):
        result = False
        description = '\nПроверка наличия ' + item.__class__.__name__
        if issubclass(item.__class__, Element):
            result = item.is_present
            description = '\nПроверка присутсвия на странице ' + item.name_output()
        return [result, description]


class IsNotPresent(BaseMatcher):

    def _matches(self, item):
        result = False
        description = '\nПроверка отсутствия ' + item.__class__.__name__
        if issubclass(item.__class__, Element):
            result = not item.is_present
            description = '\nПроверка отсутствия на странице ' + item.name_output()
        return [result, description]


class IsDisplayed(BaseMatcher):

    def _matches(self, item):
        result = False
        description = '\nПроверка отображения  ' + item.__class__.__name__
        if issubclass(item.__class__, Element):
            description = '\nПроверка отображения на странице ' + item.name_output()
            try:
                result = item.is_displayed
            except Exception as e:
                result = False
                description = '{0}\n{1}'.format(description, e)
        return [result, description]


class IsNotDisplayed(BaseMatcher):

    def _matches(self, item):
        result = False
        description = '\nПроверка НЕ отображения  ' + item.__class__.__name__
        if issubclass(item.__class__, Element):
            result = item.is_not_displayed
            description = '\nПроверка НЕ отображения на странице ' + item.name_output()
        return [result, description]


def is_present():
    """Проверка наличия элемента на странице

    Пример::

        assert_that(page_t.main_fix_1_table, is_present(), 'Здесь текстовое описание ошибки')
    """
    return IsPresent()


def is_not_present():
    """Проверка наличия элемента на странице

    Пример::

        assert_that(page_t.main_fix_1_table, is_not_present(), 'Здесь текстовое описание ошибки')
    """
    return IsNotPresent()


def is_displayed():
    """Проверка отображения элемента на странице

    Пример::
        assert_that(page_t.main_fix_1_table, is_displayed(), 'Здесь текстовое описание ошибки')
    """
    return IsDisplayed()


def is_not_displayed():
    """Проверка отсутствия отображения элемента на странице

    Пример::
        assert_that(page_t.main_fix_1_table, is_not_displayed(), 'Здесь текстовое описание ошибки')
    """
    return IsNotDisplayed()


def is_empty():
    """Проверка очистки таблицы (отсутствия строк в ней)

    Пример::
        assert_that(page_t.main_fix_1_table, is_empty(), 'Ошибка! Таблица не пуста', and_wait())
    """
    return IsEmpty()


def is_not_empty():
    """Проверка, что таблица не пустая

    Пример::
        assert_that(page_t.main_fix_1_table, is_not_empty(), 'Ошибка! Таблица пуста', and_wait())
    """
    return IsNotEmpty()
