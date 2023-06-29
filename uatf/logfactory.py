# -*- coding: utf-8 -*-
import logging
import time
import sys
import platform

from .config import Config


__all__ = ['log', 'info', 'LogFactory']

CONFIG = Config()
# if platform.system() == 'Windows' and not CONFIG.pycharm_run and sys.version_info[:2] > (3, 6):
#     sys.stdout.reconfigure(encoding='utf-8')

LOG_FORMATTER = logging.Formatter("%(asctime)s.%(msecs).03d  %(message)s\n", datefmt="%d.%m.%y %H:%M:%S")


class LogFactory:
    """Класс регилизует работу с логами"""

    instance = None

    def __new__(cls, *args):  # singleton
        if cls.instance is None:
            cls.instance = super(LogFactory, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """Опции в config.ini:

        LOG_FILE_SILENCE, если равен True, то не выводить лог в файл
        LOG_CONSOLE_SILENCE, если равен True, то не выводить в консоль
        LOG_FILE_PATH - строковое значение, путь, где создавать файл с логом

        """
        if not hasattr(self, 'root_logger'):
            self._init_levels()
            self.root_logger = logging.getLogger('root_log')
            self.start_time = None
            self.controls_log = False
            self._config = CONFIG
            self._show_check_log = self._config.options['GENERAL'].get('SHOW_CHECK_LOG')
            self._debug = self._config.options['GENERAL'].get('DEBUG')
            self._init()

    def _init_levels(self):
        """Уровни логирования
        [f]         framework
        [e]         error
          [s]       step
            [i]     info
            [a]     action
            [c]     control action
            [ch]    check
              [d]   debug
        :return:
        """
        self.steps_level = '[s]'
        self.framework_level = '[f]'
        self.info_level = ('[i]', '[a]', '[c]', '[ch]')
        self.debug_level = '[d]'
        self.error_level = '[e]'
        self.all_level = self.info_level + (self.debug_level, self.steps_level, self.framework_level, self.error_level)

    def _init(self):

        if not hasattr(self, 'console_handler'):
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setFormatter(LOG_FORMATTER)
            if not self._config.pycharm_run:
                self.root_logger.addHandler(self.console_handler)

        if self._debug:  # выводить debug или нет
            self.root_logger.setLevel(logging.DEBUG)
        else:
            self.root_logger.setLevel(logging.INFO)

    @staticmethod
    def _format_new_line(text, indent):
        return text.replace('\n', '\n' + ' ' * (37 + indent))

    def write_event(self, text, level):
        """Запись лога"""

        try:
            text = str(text)
        except Exception as error:
            print("Не смогли преобразовать переданный в log объект к строке\n{0}".format(error))
            return

        if level not in self.all_level:
            level = "[i]"

        # нужно для того чтобы базовые действия внутри контролов не логировались
        if self.controls_log and level != '[c]' and not self._debug:
            return

        message = ''
        current_level = logging.NOTSET
        if level in self.info_level:
            # не логируем проверки, если выключена опция SHOW_CHECK_LOG
            if level != '[ch]' or self._show_check_log:
                indent = 8
                text = self._format_new_line(text, indent)
                message = "{0}{1} {2}".format(" "*indent, level, text)
                current_level = logging.INFO
        elif level == self.steps_level:
            indent = 4
            text = self._format_new_line(text, indent)
            message = "{0}{1} {2}".format(" " * indent, level, text)
            current_level = logging.INFO
        elif level == self.framework_level:
            text = self._format_new_line(text, 0)
            message = "{0} {1}".format(level, text)
            current_level = logging.INFO
        elif level == self.error_level:
            text = self._format_new_line(text, 0)
            message = "{0} {1}".format(level, text)
            current_level = logging.ERROR
        elif level == self.debug_level:
            indent = 12
            text = self._format_new_line(text, indent)
            message = "{0}{1} {2}".format(" " * indent, level, text)
            current_level = logging.DEBUG

        if self.root_logger.isEnabledFor(current_level):
            if self.start_time:
                delta = str(round(time.time() - self.start_time, 3))
                str_delta = '{:>8}с '.format('+' + delta)
            else:
                str_delta = ' ' * 12

            self.start_time = time.time()
            self.root_logger.log(current_level, f'{str_delta}{message}')


def log(text, level="[s]"):
    """Логирует сообщения, сохраняет
    :param text: текс сообщения
    :param level: уровень логирования
    """
    LogFactory().write_event(text, level)


def info(text):
    """Метод необходимо использовать для логирования небольших действий или вывода доп информации
    Имеет отступ такой же как любое действие с элементами
    """
    log(text, level="[i]")
