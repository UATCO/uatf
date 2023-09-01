from typing import Optional, List

import pytest

from ...helper import delay
try:
    from ...ui import Element
    from ...ui.layout.main import LayoutCompare
except ModuleNotFoundError:
    Element = LayoutCompare = None

from ...config import Config


__all__ = ['layout']


class Layout:

    def __init__(self, subtests, request):
        self._subtests = subtests
        self._instance = request.instance
        if not self._instance:
            raise ValueError('fixture work only with class')
        self._driver = getattr(self._instance, 'driver', None)
        if not self._driver:
            raise ValueError('driver is None')
        self._layout_testing = LayoutCompare(self._driver)
        try:
            _, self._class_name, self._test_name = request.node.nodeid.split('::')
        except ValueError:
            raise ValueError('Пока не поддерживаем тесты без классов')
        self._config = Config()
        self._capture_index = 0

    def _check_uniq_name(self, name):
        """Проверка на уникальность имени сабтеста внутри теста"""

        if not name:
            return

        subtests_list = getattr(self._subtests.item, '_subtests_list', [])
        if name in subtests_list:
            with self._subtests._test('uniq_layout_test_name'):
                raise ValueError('Имя теста верстки должно быть уникально внутри одного теста, '
                                 'передайте уникальный name')
        else:
            subtests_list.append(name)
            setattr(self._subtests.item, '_subtests_list', subtests_list)

    def capture_element_cut_areas(
            self, name: str,
            element: Element,
            fill_rect: Optional[List[List[int]]] = None,
            fill_element: Optional[List[Element]] = None,
            tolerance: Optional[float] = None
    ):
        """Метод сохранения изображения с вырезанными (залитыми) элементами

        :param name: check name
        :param element: фотографируемый элемент
        :param fill_rect: вырезаемые прямоугольники, формат: [ [x0,y0,width,height], ...], x0 и y0 берутся относительно
                          координат родительского элемента
        :param fill_element: вырезаемые элементы, формат: [ element1, element2, ...]
        :param tolerance: максимально допустимая разница между цветами
        """
        if fill_rect is None:
            fill_rect = []

        if fill_element:
            coordinates = element.coordinates
            fill_rect2 = self._layout_testing.get_fill_area_by_elements(coordinates, fill_element)
            fill_rect.extend(fill_rect2)
        self.capture(name=name, element=element, fill_rect=fill_rect, tolerance=tolerance)

    def capture(
            self, name: Optional[str] = None, element: Optional[Element] = None,
            width: Optional[int] = None, height: Optional[int] = None,
            left: int = 0, top: int = 0, bottom: int = 0, right: int = 0,
            fill: bool = False,
            fill_rect: Optional[List[List[int]]] = None,
            wait_react_load: bool = False,
            tolerance: Optional[float] = None):
        """Сохраняет изображение для утилиты сравнения

        :param name - Имя скриншота
        :param element - элемент, который скриним
        :param width - Ширина скриншота (Игнорируется есле передан element)
        :param height - Высота скриншота (Игнорируется есле передан element)
        :param left - Смещение скриншота по оси X влево
        :param top - Смещение скриншота по оси Y вверх
        :param bottom - Смещение скриншота по оси Y вниз
        :param right - Смещение скриншота по оси X вправо
        :param fill - Закрашивать области или обрезать
        :param fill_rect - закрашиваемые области, формат [ [x0,y0,width,height], ...]
        :param wait_react_load - Проверка асинхронной загрузки всех подмодулей для react
        :param tolerance: максимально допустимая разница между цветами
        """

        if not name:
            name = str(self._capture_index)
            self._capture_index += 1

        if not self._subtests._is_need_run(name, True):
            return

        self._check_uniq_name(name)

        with self._subtests._test(name, layout=True):

            # в react компонент с ассинхронной загрузкой добавляется в дом дерево не дожидаясь загрузки всех модулей
            if element and wait_react_load:
                element.check_react_async_load()

            capture_delay = int(self._config.get('CAPTURE_DELAY', 'REGRESSION'))
            if capture_delay:
                delay(capture_delay, 'Задержка перед снятием скриншота')

            self._layout_testing.compare(suite=self._class_name, test=self._test_name, check_name=name,
                                         width=width, height=height, left=left, top=top, element=element,
                                         bottom=bottom, right=right, fill=fill, fill_rect=fill_rect,
                                         tolerance=tolerance)

    def capture_with_offset(
            self, name: Optional[str] = None, element: Optional[Element] = None,
            all: int = 0, x: Optional[int] = None, y: Optional[int] = None,
            top: Optional[int] = None, bottom: Optional[int] = None,
            left: Optional[int] = None, right: Optional[int] = None,
            wait_react_load: bool = False,
            tolerance: Optional[float] = None):
        """Сохраняет изображение c отступами для утилиты сравнения

        :param name - Имя скриншота
        :param element - элемент, который скриним
        :param all - Отступ от всех границ
        :param x - Отступ слева и справа (Приоритет над value)
        :param y - Отступ сверху и снизу (Приоритет над value)
        :param top - Отступ сверху (Приоритет над value_y)
        :param bottom - Отступ снизу (Приоритет над value_y)
        :param left - Отступ слева (Приоритет над value_x)
        :param right - Отступ справа (Приоритет над value_x)
        :param wait_react_load - Проверка асинхронной загрузки всех подмодулей для react
        :param tolerance: максимально допустимая разница между цветами
        """
        _left = _top = _bottom = _right = all
        if x is not None:
            _left = _right = x
        if y is not None:
            _top = _bottom = y
        if left is not None:
            _left = left
        if right is not None:
            _right = right
        if top is not None:
            _top = top
        if bottom is not None:
            _bottom = bottom
        self.capture(name=name, element=element, left=_left, top=_top, bottom=_bottom, right=_right,
                     wait_react_load=wait_react_load, tolerance=tolerance)


@pytest.fixture
def layout(subtests, request):
    """fixture for layout regression testing"""

    yield Layout(subtests, request)
