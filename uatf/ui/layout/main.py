import io
import os
import shutil
from typing import Optional, List

from PIL import Image, ImageDraw

from ...helper import get_artifact_path
from ..elements import Element
from .antialiasing import is_aa
from ...config import Config
from ...logfactory import log

config = Config()


class RegressionError(AssertionError):

    def __init__(self, msg, standard, current, diff, src: Optional[str], element: Optional[Element] = None):
        super().__init__(msg)
        self.standard = standard
        self.current = current
        self.diff = diff
        self.src = src
        self.error_reason = element.get_po_path() if element else None


color_space = config.get('COLOR_SPACE', 'REGRESSION')
if color_space == 'yiq':
    from .color_yiq import equal_yiq as equal_img
elif color_space == 'lab':
    from .color_lab import equal_ciede2000 as equal_img


def convert_coordinates_to_ios(rect):
    """Конвертор координат для ios"""

    return list(map(lambda x: x * 2, rect))


def create_image_from_bytes(_bytes, device_pixel_ratio=None) -> Image:
    png = Image.open(io.BytesIO(_bytes))
    if device_pixel_ratio:
        png = png.resize((round(png.width / device_pixel_ratio), round(png.height / device_pixel_ratio)))
    return png


def convert_coordinates(fill_rect):
    if fill_rect is None:
        return []
    elif fill_rect and config.device_name == 'ios':
        # координаты в iOS измеряются в точках, а не в пикселях
        return [convert_coordinates_to_ios(rect) for rect in fill_rect]
    else:
        return fill_rect


def convert_regression_suite_name(suite):
    """Конвертирует название suite теста верстки"""

    return suite.replace('TestRegression', 'Regression')


class LayoutCompare:
    """Layout Regression Testing"""

    def __init__(self, driver):
        self._driver = driver
        self._standard_dir = os.path.abspath(config.get('IMAGE_DIR', 'REGRESSION'))
        self._tolerance = config.get('TOLERANCE', 'REGRESSION')
        self._antialiasing_tolerance = config.get('ANTIALIASING_TOLERANCE', 'REGRESSION')
        self._report_dir = get_artifact_path('regression')
        self._device_pixel_ratio = None
        # координаты для скрина при эмуляции устройств делятся на devicePixelRatio
        # https://developer.mozilla.org/en-US/docs/Web/API/Window/devicePixelRatio
        if config.get("CHROME_MOBILE_EMULATION", "GENERAL"):
            self._device_pixel_ratio = self._driver.execute_script("return window.devicePixelRatio")

    def _process_image(
            self, name: Optional[str] = None,
            element: Optional[Element] = None,
            width: Optional[int] = None, height: Optional[int] = None,
            left: int = 0, top: int = 0, bottom: int = 0, right: int = 0,
            fill: bool = False,
            fill_rect: Optional[List[List[int]]] = None
    ) -> Image:
        """Обработка изображение для сравнения

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
        """

        if not any((element, width, height, left, top, bottom, right)):
            image = self._capture_window()
            msg = 'Сделали снимок экрана c именем %s' % name
        elif element and not any((width, height, left, top, bottom, right, fill_rect)):
            image = self._capture_element(element)
            msg = 'Сделали снимок %s c именем %s' % (element.name_output(), name)
        elif element and fill_rect:
            image = self._capture_element(element, fill_rect)
            msg = 'Сделали снимок %s c именем %s' % (element.name_output(), name)
        else:
            try:
                if element:
                    left, top, width, height = element.get_bound_with_indent(left, top, bottom, right)
                description = (width, height, name, left, top)
                if fill:
                    image = self._fill_rect_on_window(left, top, width, height)
                    msg = 'Закрасили область %sx%s с именем %s и смещением x:%s, y:%s' % description
                else:
                    image = self._crop_window(left, top, width, height)
                    msg = 'Сделали снимок области %sx%s с именем %s и смещением x:%s, y:%s' % description
            except Exception as err:
                image = self._create_empty_image()
                msg = f'Не смогли сохранить изображение {name}\n Генерируем заглушку размером 200x200\n{err}'
        log(msg)
        return image

    @staticmethod
    def _create_empty_image() -> Image:
        """Создаем заглушку"""

        return Image.new('RGB', (200, 200))

    def _crop_window(self, left: int, top: int, width=0, height=0) -> Image:
        """Сохраняем изображение по координатам
        :arg left - смещение по оси X
        :arg top - смещение по оси Y
        :arg width - длина
        :arg height - высота
        """

        png = self._capture_window()
        width_ = width or png.width
        height_ = height or png.height
        cropped = png.crop((left, top, left + width_, top + height_))
        png.close()
        return cropped

    def _fill_rect_on_window(self, left, top, width=0, height=0) -> Image:
        """Создаем изображение и закрашиваем области

        :arg left - смещение по оси X
        :arg top - смещение по оси Y
        :arg width - длина
        :arg height - высота
        """

        black = (0, 0, 0)

        png = self._capture_window()
        image_width, image_height = png.size
        _width = width or png.width
        _height = height or png.height
        draw = ImageDraw.Draw(png)
        draw.rectangle((0, 0, image_width, top), fill=black)
        draw.rectangle((0, top + _height, image_width, image_height), fill=black)
        draw.rectangle((0, top, left, top + _height), fill=black)
        draw.rectangle((left + _width, top, image_width, top + _height), fill=black)
        del draw
        return png

    def get_fill_area_by_elements(self, coordinates, fill_elements) -> list:
        """Получает размер элемента относительно родительского

        :param coordinates: координаты родительского элемента
        :param fill_elements: элементы, координаты которого получаем относительно родительского элемента
        :return: координаты элемента, формат: [x0, y0, width, height]
        """
        fill_rect = []
        for elem in fill_elements:
            fill_rect.append(self._get_fill_area_by_element(coordinates, elem))
        return fill_rect

    @staticmethod
    def _get_fill_area_by_element(coordinates, element) -> list:
        """Получает размер элемента относительно родительского

        :param coordinates: координаты родительского элемента
        :param element: элемент, координаты которого получаем относительно родительского элемента
        :return: координаты элемента, формат: [x0, y0, width, height]
        """

        elm_coords = element.coordinates
        elm_size = element.size
        elm_rect = [(elm_coords['x'] - coordinates['x']),
                    (elm_coords['y'] - coordinates['y']),
                    elm_size['width'],
                    elm_size['height']]
        return elm_rect

    def compare(
            self, check_name: str, suite: str = '', test: str = '',
            element: Optional[Element] = None,
            width: Optional[int] = None, height: Optional[int] = None,
            left: int = 0, top: int = 0, bottom: int = 0, right: int = 0,
            fill: bool = False, msg: str = "",
            fill_rect: Optional[List[List[int]]] = None,
            tolerance: float = None) -> bool:
        """Сохраняет изображение для утилиты сравнения

        :param suite имя сюита
        :param test имя теста
        :param check_name - Имя скриншота
        :param element - элемент, который скриним
        :param width - Ширина скриншота (Игнорируется есле передан element)
        :param height - Высота скриншота (Игнорируется есле передан element)
        :param left - Смещение скриншота по оси X влево
        :param top - Смещение скриншота по оси Y вверх
        :param bottom - Смещение скриншота по оси Y вниз
        :param right - Смещение скриншота по оси X вправо
        :param fill - Закрашивать области или обрезать
        :param fill_rect - закрашиваемые области, формат [ [x0,y0,width,height], ...]
        :param msg - сообщение об ошибке
        :param tolerance: максимально допустимая разница между цветами
        """
        file_name = self._get_file_path(check_name, suite, test)
        self._makedirs(file_name)

        current_image = self._process_image(name=check_name, element=element,
                                            width=width, height=height, left=left, top=top,
                                            bottom=bottom, right=right, fill=fill, fill_rect=fill_rect)

        if config.get('GENERATE_IMAGE', 'REGRESSION'):
            current_image.save(file_name)
            return True

        src = self._copy_standard_image(file_name)

        standard_name = file_name.replace('~cur', '~ref')
        diff_name = file_name.replace('~cur', '~diff')
        standard_image = Image.open(standard_name)
        tolerance = tolerance if tolerance else self._tolerance
        is_equal = self._compare_image(diff_name, standard_image=standard_image, current_image=current_image,
                                       tolerance=tolerance)
        if not is_equal:
            current_image.save(file_name)
            if not msg:
                msg = f"Текущее изображение '{check_name}' не соответствует ожидаемому"
            exc = RegressionError(msg, standard=standard_name, current=file_name, diff=diff_name,
                                  src=src, element=element)
            raise exc
        else:
            log(f'Изображения {check_name} идентичны')
            return True

    def _compare_image(self, diff_name: str, standard_image: Image, current_image: Image,
                       tolerance: float) -> bool:
        """Сравниваем эталонное изображение и текущее"""

        try:
            current_bytes = io.BytesIO()
            current_image.save(current_bytes, format="PNG")
            standard_bytes = io.BytesIO()
            standard_image.save(standard_bytes, format='PNG')

            # equal bytes
            if current_bytes.getvalue() == standard_bytes.getvalue():
                return True

            return self._compare_by_pixel(current_image, standard_image, diff_name, tolerance)
        except Exception as error:
            log('Error compare image:\n%s' % error, '[e]')
            return False

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _diff_not_equal_image_by_size(
            standard, current, width, height, pixel1, pixel2, highlight_color, tolerance
    ) -> Image:
        """Сравниваем эталонное изображение и текущее когда не совпадают размеры"""

        min_width = min(standard.width, current.width)
        min_height = min(standard.height, current.height)

        diff_image = Image.new('RGBA', (width, height))
        diff_pixels = diff_image.load()

        for y in range(0, height):
            for x in range(0, width):
                if x >= min_width or y >= min_height:
                    diff_pixels[x, y] = highlight_color
                    continue
                c1 = pixel1[x, y]
                c2 = pixel2[x, y]
                if c1 == c2 or equal_img(c1, c2) < tolerance:
                    diff_pixels[x, y] = c1
                else:
                    diff_pixels[x, y] = highlight_color

        return diff_image

    # noinspection PyUnresolvedReferences
    def _compare_by_pixel(self, current_image: Image, standard_image: Image, diff_name: str,
                          tolerance: float) -> bool:
        """Сравнение 2 PIL.Image"""

        diff_area = []
        stable_diff_area = []

        highlight_color = (255, 10, 193, 255)
        pixel1 = current_image.load()
        pixel2 = standard_image.load()
        width = max(standard_image.width, current_image.width)
        height = max(standard_image.height, current_image.height)
        border = max(max(width, height) // 100, 10)

        # сравнение 2 не равных по размеру
        if standard_image.width != current_image.width or standard_image.height != current_image.height:
            diff_image = self._diff_not_equal_image_by_size(
                standard_image, current_image, width, height, pixel1, pixel2, highlight_color, tolerance
            )
            diff_image.save(diff_name)
            return False

        antialiasing = config.get('ANTIALIASING', 'REGRESSION')
        diff_mask = config.get('HIGHLIGHT_DIFF', 'REGRESSION')
        is_equal = True

        diff_image = standard_image.copy()
        diff_pixels = diff_image.load()
        for y in range(0, height):
            for x in range(0, width):
                c1 = pixel1[x, y]
                c2 = pixel2[x, y]
                if c1 == c2:
                    continue
                delta = equal_img(c1, c2)
                if delta < tolerance:
                    continue
                if antialiasing and delta < self._antialiasing_tolerance \
                        and (is_aa(pixel1, x, y, width, height, pixel2) or
                             is_aa(pixel2, x, y, width, height, pixel1)):
                    continue
                else:
                    is_equal = False
                    diff_pixels[x, y] = highlight_color
                    if diff_mask:
                        diff_area = self.compute_diff_area(diff_area, x, y, border)

            if diff_mask:
                rectangle_collector = []
                for rectangle in diff_area:
                    if y - border > rectangle[3]:
                        rectangle_collector.append(rectangle)
                for rectangle in rectangle_collector:
                    stable_diff_area.append(rectangle)
                    diff_area.remove(rectangle)
        if not is_equal:
            if diff_mask:
                from PIL import Image
                diff_area = stable_diff_area + diff_area
                mask = self.draw_diff_mask(width, height, diff_area)
                diff_image = Image.alpha_composite(diff_image, mask)
            diff_image.save(diff_name)
        else:
            diff_image.close()
        return is_equal

    @staticmethod
    def compute_diff_area(diff_area: [], x, y, border_width=10):
        """
        Вычисляем, попадает ли пиксель в известтную ранее область с изменениями
        :param diff_area: Области изменения
        :param x:
        :param y:
        :param border_width: Ширина допустимого попадания в область
        :return:
        """
        inside_area = False
        for index, areas in enumerate(diff_area):
            if areas[0] < x + border_width and x - border_width < areas[2] \
                    and areas[1] < y + border_width and y - border_width < areas[3]:
                x0 = min(areas[0], x - border_width)
                x1 = max(areas[2], x + border_width)
                y0 = min(areas[1], y - border_width)
                y1 = max(areas[3], y + border_width)
                diff_area[index] = [x0, y0, x1, y1]
                inside_area = True
                break
        if not inside_area:
            diff_area.append([x - border_width, y - border_width, x + border_width, y + border_width])
        return diff_area

    @staticmethod
    def draw_diff_mask(width, height, diff_area):
        """
        Отрисовка маски изображения
        :param width:
        :param height:
        :param diff_area:
        :return:
        """
        rect_size = (width, height)
        im = Image.new("RGBA", rect_size, (0, 0, 0, 160)).convert("RGBA")
        for i in diff_area:
            draw = ImageDraw.Draw(im)
            draw.rectangle([(i[0] - 5, i[1] - 5), (i[2] + 5, i[3] + 5)], outline='red', width=5)
        for i in diff_area:
            rect_size = (i[2] - i[0], i[3] - i[1])
            x0 = max(i[0], 0)
            y0 = max(i[1], 0)
            rect_pos = (x0, y0)
            rect = Image.new("RGBA", rect_size, (255, 255, 255, 0))
            im.paste(rect, rect_pos)
        return im

    def _capture_element(self, element, fill_rect=None, fill_element=None) -> Image:
        """Сохраняем изображение элемента

        :arg element - элемент
        :param fill_rect: вырезаемые прямоугольники, формат: [ [x0, y0, width, height], …],
                         (x0 и y0 берутся относительно координат родительского элемента)
        :param fill_element: вырезаемые элементы, формат: [ element1, element2, …]
        """
        png = create_image_from_bytes(element.screenshot_as_png())
        fill_rect = convert_coordinates(fill_rect)
        if fill_element:
            coordinates = element.coordinates
            for elm in fill_element:
                fill_rect.append(self._get_fill_area_by_element(coordinates, elm))
        if fill_rect:
            for i in range(len(fill_rect)):
                rect = Image.new('RGBA', (int(fill_rect[i][2]), int(fill_rect[i][3])), (255, 255, 255, 0))
                png.paste(rect, (fill_rect[i][0], fill_rect[i][1]))
        return png

    def _capture_window(self) -> Image:
        """Сохраняем скрин Окна"""
        return create_image_from_bytes(self._driver.get_screenshot_as_png(),
                                       device_pixel_ratio=self._device_pixel_ratio)

    def _get_file_path(self, check_name, suite_name='', test_name='') -> str:
        """Получаем имя паки и файла для скринов"""

        # TODO для платформы из-за классов Regression
        if suite_name:
            suite_name = convert_regression_suite_name(suite_name)

        resolution = config.get('BROWSER_RESOLUTION', 'GENERAL')
        theme = config.get('REGRESSION_THEME', 'REGRESSION')
        prefix = "" if not theme else f'_{theme}'
        if resolution:
            resolution = resolution.replace('x', '_')
            prefix = f'{prefix}_{resolution}'

        if config.get('GENERATE_IMAGE', 'REGRESSION'):
            if suite_name:
                folder_name = os.path.join(self._standard_dir, suite_name, test_name, check_name)
            else:
                folder_name = os.path.join(self._standard_dir, check_name)
            file_name = os.path.join(folder_name, config.device_name + prefix + '.png')
        else:
            if suite_name:
                folder_name = os.path.join(self._report_dir, suite_name, test_name, check_name)
            else:
                folder_name = os.path.join(self._report_dir, check_name)
            file_name = os.path.join(folder_name, config.device_name + prefix + '~cur' + '.png')
        return file_name

    @staticmethod
    def _makedirs(filename):
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

    def _copy_standard_image(self, name):
        """Копируем скрин из папки с эталонами в папку с отчетом"""

        src = name.replace(self._report_dir, self._standard_dir).replace('~cur', '')

        if not os.path.exists(src):
            raise FileNotFoundError(f'Не найден эталон для сравнения: {src}')
            # раньше было так
            # empty = Image.new('RGB', (400, 400))
            # empty.save(src)
        dst = name.replace('~cur', '~ref')
        shutil.copyfile(src, dst)
        return src
