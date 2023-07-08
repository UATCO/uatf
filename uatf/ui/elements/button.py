# -*- coding: utf-8 -*-
"""
Модуль реализует работу с кнопками
"""
from .element import Element


class Button(Element):
    """Класс реализует работу с кнопками"""

    def __str__(self):
        return 'кнопка'
