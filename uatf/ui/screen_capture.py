"""Модуль для записи прохождения теста в MP4 / GIF"""
import base64
import hashlib
import io
from dataclasses import dataclass
import os
import tempfile
from os import path
from typing import Optional

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException

from ..config import Config
from ..helper import save_artifact, get_artifact_path


CONFIG = Config()
config_general = CONFIG.GENERAL
HIGHLIGHT_ACTION = CONFIG.get('HIGHLIGHT_ACTION', 'GENERAL')
RECORD_VIDEO = CONFIG.get('SCREEN_CAPTURE', 'GENERAL')
font_path = path.abspath(path.join(path.dirname(__file__), 'consola.ttf'))


def get_font_size() -> int:
    browser = CONFIG.device_name
    # Выбор размера шрифта в зависимости от браузера
    if browser == 'android':
        size = 40
    elif browser == 'ios':
        size = 30
    else:
        size = 16
    return size


font_size = get_font_size()
font_element: Optional[FreeTypeFont] = None


def gen_file_name(screenshot_list):
    """Генерация имени видео
    Задумка следующая: если мы падаем в setup, то действия все одинаковые и скрины тоже
    Поэтому мы постараемся исключить генерацию одинаковых video / gif
    """

    name = ';'.join(screenshot_list)
    file_name = hashlib.md5(name.encode()).hexdigest()
    return file_name


def add_screen_for_gif(screenshot_path):
    """Добавление скрина для GIF"""

    screenshot_list = config_general.get('SCREENSHOT_LIST', [])
    screenshot_list.append(screenshot_path)
    config_general['SCREENSHOT_LIST'] = screenshot_list


def make_screen_for_gif(driver, element=None, type_of_action=None, data=None, log=None):
    """
    Делаем скриншот окна и сохраняет его в папке
    :param driver: драйвер
    :param element: элемент, если нужен
    :param type_of_action: тип действия - клик, написание, очистка, should_be
    :param data: дополнительные данные для действия - матчеры и их значения
    :param log: кастомное сообщение, которое можно написать на скрине
    :return:
    """

    if not (CONFIG.is_last_run or RECORD_VIDEO == 'all') or not (RECORD_VIDEO or HIGHLIGHT_ACTION):
        return
    screen_folder = CONFIG.get('TMP_DIR_SCREENS', 'GENERAL')
    if not screen_folder:
        # папка временная, после генерации удаляется, поэтому можно сохранить в текущую
        screen_folder = tempfile.mkdtemp(dir=os.getcwd())
        CONFIG.set_option('TMP_DIR_SCREENS', screen_folder, 'GENERAL')

    try:
        screenshot_data = base64.b64decode(driver.get_screenshot_as_base64())
    except (UnexpectedAlertPresentException, WebDriverException):
        return

    # Для добавления комментария на скриншоте
    if element is not None and config_general.get('SCREEN_CAPTURE') == 'all':
        screenshot_data = screen_log(screenshot_data, element, driver, type_of_action.text, data)

    screenshot_name = (hashlib.md5(screenshot_data).hexdigest()) + ".jpg"
    screenshot_path = path.join(screen_folder, screenshot_name)

    from PIL import Image
    import io
    if not path.isfile(screenshot_path):
        bg = Image.open(io.BytesIO(bytearray(screenshot_data)))
        img = Image.new("RGB", bg.size, (255, 255, 255))
        from .browser import Env
        if not Env.is_mobile():
            img.paste(bg, (0, 0), bg)
        else:
            img.paste(bg, (0, 0))
        img.save(screenshot_path, quality=95)
    add_screen_for_gif(screenshot_path)


@dataclass
class DrawableType:
    text: str = 'default'
    is_highlighted: bool = True


def mobile_draw(driver, screenshot_data, type_of_action, data, log):
    from PIL import Image, ImageDraw
    import io
    im = Image.open(io.BytesIO(screenshot_data))
    draw = ImageDraw.Draw(im)
    multiplier = im.size[0] / driver.get_window_size()['width']

    # Пишем свой текст в левом верхнем углу
    if log:
        draw_log(draw, log)
    if type_of_action == 'tap':
        draw_circle(draw, data[0] * multiplier, data[1] * multiplier)
    elif type_of_action == 'swipe':
        draw_arrow(draw, tuple(multiplier * x for x in data[0]), tuple(multiplier * x for x in data[1]))
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def write_log_on_image(draw, event_type, args, x0=0, y0=0):
    """
    Метод отрисовки логов
    :param draw: канвас
    :param event_type: тип события
    :param args: аргументы события
    :param x0: координата начала сообщения
    :param y0: координата начала сообщения
    :return:
    """
    text_log = ''
    red_color = '#991111'
    green_color = '#119911'
    main_color = red_color
    if 'should' in event_type:
        main_color = green_color
        condition = args[0]
        from .should_be import Condition
        if isinstance(condition, Condition):
            condition_name = type(condition).__name__
        else:
            condition_name = condition.__name__
        if event_type == 'should_not_be':
            text_log = 'Not'
        text_log += condition_name
        if hasattr(condition, 'text'):
            text_log += f'({condition.text})'
    else:
        text_log = event_type
    if len(args) > 1:
        additional_params = ""
        for data in args[1:]:
            if not isinstance(data, bool):
                try:
                    additional_params += str(data)
                except TypeError:
                    pass
        if additional_params:
            text_log += f'({additional_params})'
    draw_log(draw, text_log, x0, y0, main_color)


def screen_log(screenshot_data, element, driver, event_type=None, args=None):
    """
    Метод создания скрина с комментарием по событию
    :param screenshot_data: канвас
    :param element:  элемент
    :param driver: драйвер
    :param event_type: тип события
    :param args: аргументы события
    :return:
    """
    from PIL import Image, ImageDraw
    from ..exceptions import ElementException
    im = Image.open(io.BytesIO(screenshot_data))
    draw = ImageDraw.Draw(im)
    try:
        coord = element.coordinates
    except ElementException:
        coord = {'x': -1, 'y': -1}

    # в ios экран растягивается в два раза от оригинала
    multiplier = im.size[0] / driver.get_window_size()['width']
    if args is None or coord['x'] != -1:
        x0 = coord['x'] * multiplier
        y0 = coord['y'] * multiplier
        write_log_on_image(draw, event_type, args, x0, y0)
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def mobile_highlight(element, driver, element_on_screen=True):
    """
    Метод обводки мобильных элементов
    :param element: элемент
    :param driver: драйвер
    :return:
    """
    from PIL import Image, ImageDraw
    import io
    from uatf import assert_that, equal_to, and_wait, not_equal
    from ..ui.elements.custom_list import CustomList
    from ..exceptions import ElementException

    fail_flag = False
    if element_on_screen:
        try:
            assert_that(lambda: (element.is_enabled or element.is_displayed), equal_to(True),
                        desc=f'Элемент {element.rus_name} не отображается', wait_time=and_wait(wait_time=2, period=1))
            assert_that(element.coordinates, not_equal(None), desc='Координата получена')
        except ElementException:
            fail_flag = True
    else:
        fail_flag = True
    screenshot_data = base64.b64decode(driver.get_screenshot_as_base64())
    im = Image.open(io.BytesIO(screenshot_data))
    draw = ImageDraw.Draw(im)
    if not fail_flag:
        # в ios экран растягивается в два раза от оригинала
        try:
            multiplier = im.size[0] / driver.get_window_size()['width']
            if isinstance(element, CustomList):
                # Для элементов CustomList обводим элементы циклом
                element = element.item(1)
            crd = element.coordinates
            size = element.size
            x0 = crd['x'] * multiplier
            y0 = crd['y'] * multiplier
            x1 = crd['x'] * multiplier + size['width'] * multiplier
            y1 = crd['y'] * multiplier + size['height'] * multiplier
            draw_rect(draw, x0, y0, x1, y1)
        except TypeError:
            fail_flag = True
        except ElementException:
            fail_flag = True
    if fail_flag:
        draw_log(draw, 'No element: ' + element.locator)

    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def draw_circle(draw, x0, y0):
    """
    Отрисовка круга
    :param draw: канвас
    :param x0: центр круга
    :param y0: центр круга
    :return:
    """
    left_up_point = ((x0 - 10), (y0 - 10))
    right_down_point = ((x0 + 10), (y0 + 10))
    draw.ellipse([left_up_point, right_down_point], fill=(255, 0, 0))


def draw_arrow(draw, start, end):
    """
    Метод отрисовки стрелки (для свайпов в мобильных тестах)
    :param draw:
    :param start: Начало стрелки
    :param end: конец стрелки
    :return:
    """
    import math
    x0, y0 = start
    x1, y1 = end
    draw.line(((x0, y0), (x1, y1)), width=10, fill='red')
    xb = 0.90 * (x1 - x0) + x0
    yb = 0.90 * (y1 - y0) + y0
    if x0 == x1:
        vtx0 = (xb - 20, yb)
        vtx1 = (xb + 20, yb)
        if y0 > y1:
            vtx2 = (x1, y1-30)
        else:
            vtx2 = (x1, y1 + 30)
    elif y0 == y1:
        vtx0 = (xb, yb + 20)
        vtx1 = (xb, yb - 20)
        if x0 > x1:
            vtx2 = (x1-30, y1)
        else:
            vtx2 = (x1+30, y1)
    else:
        alpha = math.atan2(y1 - y0, x1 - x0) - 90 * math.pi / 180
        a = 20 * math.cos(alpha)
        b = 20 * math.sin(alpha)
        vtx0 = (xb + a, yb + b)
        vtx1 = (xb - a, yb - b)
        if y0 > y1:
            vtx2 = (x1, y1 - 30)
        else:
            vtx2 = (x1, y1 + 30)
    draw.polygon([vtx0, vtx1, vtx2], fill='red')


def draw_log(draw, text="", x0=0, y0=0, color='#991111'):
    """
    Отрисовка текста в указанной области
    :param draw: канвас
    :param text: текст
    :param x0: координата начала
    :param y0: координата начала
    :param color: цвет фона
    :return:
    """
    global font_element
    if font_element is None:
        font_element = ImageFont.truetype(font_path, font_size)

    size = draw.im.size
    # Вычисляем длину и ширину прямоугольника для фона
    width = (font_size/2+2)*len(text)+6
    height = font_size+6

    # Случай выхода комментария за пределы экрана
    if x0+width > size[0]:
        x0 = size[0] - width - 10
    if y0-height < 0:
        y0 = height+3
    shape = [(x0, y0-height), (x0+width, y0-3)]
    draw.rectangle(shape, fill=color)
    draw.text((x0+3, y0-height+3), text, (255, 255, 255), font=font_element)


def draw_rect(draw, x0, y0, x1, y1, color='red', width=5):

    """
    Отрисовка прямоугольника вокруг элемента, актуально для мобильного
    Отрисовываем как 4 линии, если будет очень медленно, то можно через закомментированную строку пустить,
    но ширина линии будет 1 px

    :param draw:  Канвас, на котором рисуем
    :return:
    """
    draw.rectangle([(x0, y0), (x1, y1)], outline=color, width=width)


def get_path_first_frame():
    """Загружаем шаблон"""

    lib_path = path.split(__file__)[0]
    file = path.join(lib_path, 'start_frame.jpg')
    if path.isfile(file):
        return file
    else:
        raise FileNotFoundError('Не найден файл: %s' % path.abspath(file))


def make_gif(driver):
    """Генерируем gif-картинку"""

    gif_name = _http = ''
    screenshot_list = config_general.get('SCREENSHOT_LIST')
    if len(screenshot_list) > 1:
        gif_name = gen_file_name(screenshot_list)
        from PIL import Image
        # стартовый frame
        start_frame = get_path_first_frame()
        # стартовый кадр
        gif = Image.open(start_frame)
        size = driver.get_window_size()
        if size['height'] > 127:  # размер окна больше размера скрина
            size['height'] -= 126
        gif.resize((size['width'], size['height']), Image.ANTIALIAS)

        # скрины
        images = [Image.open(screen) for screen in screenshot_list]
        # генерация gif
        gif_bytes = io.BytesIO()
        gif.save(gif_bytes, format='gif', duration=1000, loop=0, save_all=True, append_images=images)
        gif_name, _http = save_artifact(f'{gif_name}.gif', gif_bytes, folder='screenshots', mode='wb')
    return _http or gif_name


def make_video(with_metainfo=None):
    """Генерируем Видео из скриншотов"""
    import os
    video_file_name = ''
    screenshot_list = config_general.get('SCREENSHOT_LIST')

    if screenshot_list and len(screenshot_list) > 1:
        import cv2
        # Получаем эталонные размеры будущего видео
        img = cv2.imread(screenshot_list[0])
        height, width, _ = img.shape
        video_file_name = gen_file_name(screenshot_list)
        fourcc = cv2.VideoWriter_fourcc(*"VP80")
        # FIXME фигурирует папка screenshots, нужно обобщение
        screenshot_folder = get_artifact_path('screenshots')
        # FIXME перейти по возможности на метод save_artifact
        video_file_name = path.join(screenshot_folder, video_file_name + ".webm")
        if not os.path.isdir(screenshot_folder):
            os.mkdir(screenshot_folder)
        video_file_name = path.abspath(video_file_name)
        video = cv2.VideoWriter(video_file_name, fourcc, 1, (width, height))
        if with_metainfo:
            draw_metainfo(img, video, with_metainfo)
        # Генерация видео
        for file_name in screenshot_list:
            img1 = cv2.imread(file_name)
            img_height, img_width, _ = img1.shape
            if (img_height, img_width) != (height, width):
                img1 = cv2.resize(img1, (width, height))
            video.write(img1)

        video.release()
        cv2.destroyAllWindows()

    return video_file_name or None


def draw_metainfo(image, video, with_metainfo):
    """
    Запись метаинформации на первом кадре видео
    :param image:
    :param video:
    :param with_metainfo:
    :return:
    """
    import cv2
    lines = 0
    for key, value in with_metainfo.items():
        text_size, _ = cv2.getTextSize(key+': '+value, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
        text_w, text_h = text_size
        cv2.rectangle(image, (0, lines * (text_h+10)), (text_w, (lines+1) * (text_h+10)), (0, 0, 0), -1)
        cv2.putText(image, key+': '+value, (0, (lines+1) * (text_h+10)-5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        lines = lines + 1
    video.write(image)
    return video
