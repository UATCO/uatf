"""
Модуль, реализующий работу со ссылками
"""
from .element import Element


class Link(Element):
    """Класс, реализующий работу со ссылками"""

    def __str__(self):
        return 'ссылка'

