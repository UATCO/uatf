import functools
from typing import Any

from ...logfactory import LogFactory
from ...ui.elements.base_element import BaseElement


def control_action(func) -> Any:
    """Декоратор выполнения действий до/после Control action

    Нужен для того, чтобы скрыть все логирование действий над элементами контрола и
    вывести только красивый лог конечного действия

    пример
    @control_action
    def action(self)
        self.element1.mouse_over()
        self.element2.click()
        log('Совершили действие над контролом', '[c]')

    В логе будет только:
    Совершили действие над контролом (обязательно указать уровень - [c])

    Если напишем так
    def action(self)
        self.element1.mouse_over()
        self.element2.click()
        log('Совершили действие над контролом', '[c]')

    В логе будет:
    навели курсор на element1
    кликнули по element2
    Совершили действие над контролом
    """

    @functools.wraps(func)
    def tmp(*args, **kwargs):
        log_instance = LogFactory()
        log_instance.controls_log = True
        try:
            return func(*args, **kwargs)
        finally:
            log_instance.controls_log = False

    return tmp


class BaseControl(BaseElement):
    """Базовый класс для контролов"""

    def __str__(self):
        return 'контрол'

    def init(self, driver, parent=None, region=None, name=''):
        """Инициализация контрола не в PO
        ТОЛЬКО ДЛЯ ДИНАМИЧЕСКИХ КОНТРОЛОВ
        :param driver: драйвер
        :param parent: список функций/методов для нахождения родителей
        :param region: region
        """

        from ...ui.region import BaseRegion
        super().init(driver, parent, region)

        for key, value in self.get_elements():
            if issubclass(value.__class__, BaseElement):
                value.init(self.driver, parent=self, region=region)
            elif issubclass(value.__class__, BaseRegion):
                value.__init__(self.driver)

    def get_elements(self):
        for key, value in self.__dict__.items():
            if key not in self.IGNORE_ATTRS:  # иначе будет рекурсия
                yield key, value
