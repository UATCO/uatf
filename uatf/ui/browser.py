import os
import shutil
import time
from datetime import datetime

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchWindowException

from ..config import Config
from ..logfactory import log
from urllib import parse


class Browser:
    """Класс для работы с браузером"""

    def __init__(self, driver):
        self.config = Config()
        self.driver: WebDriver = driver

    def open(self, url: str):
        """Метод для откртытия веб-страницы
        :param url: ссылка по которой переходим"""

        self.driver.get(url)

    def quite(self):
        """Закрываем браузер"""

        self.driver.quit()

    @property
    def current_url(self):
        """Получает url текущего окна."""

        return self.driver.current_url

    @property
    def current_window_handle(self):
        """Получает handle текущего окна"""

        return self.driver.current_window_handle

    @property
    def current_title(self):
        """Получает заголовок текущего окна."""

        return self.driver.title

    @property
    def titles(self):
        """Получает заголовки всех окон."""

        handles = self.get_windows
        current_window = self.driver.current_window_handle
        titles = []
        for handle in handles:
            self.switch_to_window(strategy='handle', value=handle)
            titles.append(self.current_title)
        self.switch_to_window(strategy='handle', value=current_window)
        return titles

    @property
    def get_windows(self):
        """Возвращает список хэндлов всех окон."""

        return self.driver.window_handles

    def switch_to_window(self, value, strategy: str = 'number'):
        """Переключается между окнами по number, handle

        :param value: значения по которому переключаемся
        :param strategy: стратегия поиска окна. Возможные варианты 'number', 'handle'
        """

        if strategy == 'number':
            self.driver.switch_to.window(self.get_windows[value])
        else:
            self.driver.switch_to.window(value)

    @property
    def count_windows(self):
        """Возвращает количество открытых окон."""

        return len(self.driver.window_handles)

    def maximize_window(self):
        """Разворачивает окно на весь экран."""

        self.driver.maximize_window()

    def set_window_size(self, width, height, window_handle='current'):
        """Устанавливает размер окна. По умолчанию текущего."""

        self.driver.set_window_size(width, height, window_handle)

    def set_window_position(self, x, y, window_handle='current'):
        """Устанавливает координаты окна.

        Устанавливает координаты левого верхнего угла окна.
        Отчет координат ведется: x - слева направо; y - сверху вниз.
        """

        self.driver.set_window_position(x, y, window_handle)

    def get_window_size(self, window_handle='current'):
        """Возвращает размер окна. По умолчанию текущего."""

        return self.driver.get_window_size(window_handle)

    def get_window_position(self, window_handle='current'):
        """Возвращает координаты левого верхнего угла окна. По умолчанию текущего."""

        return self.driver.get_window_position(window_handle)

    def switch_to_opened_window(self):
        """Переключается на последнее открытое окно"""

        self.switch_to_window(len(self.get_windows) - 1)

    def switch_to_parent_window(self):
        """Переключаемся на родительское окно."""

        self.switch_to_window(0)

    def close(self):
        """Закрывает текущее окно"""

        self.driver.close()

    def back(self):
        """Делает один шаг назад по истории браузера."""

        self.driver.back()

    def forward(self):
        """Делает один шаг вперед по истории браузера."""

        self.driver.forward()

    def refresh(self):
        """Обновляет текущую страницу."""

        self.driver.refresh()

    def execute_script(self, script, *args):
        """Запуск java скрипта"""

        msg_err = "Не смогли выполнить JS код:\n %s" % script
        result = self.driver.execute_script(script, *args)
        if isinstance(result, Exception):
            raise Exception('%s\n%s' % (msg_err, result))
        log('Выполнили js код: \n%s' % script, "[a]")
        return result

    def delete_cookie(self, name):
        """удаление cookie"""

        self.driver.delete_cookie(name)

    def delete_all_cookies(self):
        """Удаление всех cookies браузера"""

        stands = ('online', 'reg', 'inside', 'my', 'n.sbis.ru')
        parsed_url = parse.urlparse(self.current_url)
        if list(filter(lambda x: x in parsed_url.netloc, stands)):  # на тестовых стендах переходим на auth
            self.driver.get('%s://%s/ver.html' % (parsed_url.scheme, parsed_url.netloc))
            time.sleep(0.2)
        self.driver.delete_all_cookies()

    def add_cookie(self, name, value, path="/", secure=False, domain=None):
        """Установка cookie"""

        cookie = {'name': name, 'value': value, 'path': path, 'secure': secure}
        if domain:
            cookie['domain'] = domain
        self.driver.add_cookie(cookie)

    def create_new_tab(self, url='about:'):
        """Создание новой вкладки
        :param url: адрес который открыть
        """

        self.driver.execute_script("window.open('%s', '_blank')" % url)

    def soft_restart(self):
        """Мягкий рестарт браузера

        Закрываем все окна
        Чистим все куки
        Переходим на пустую страницу
        """
        self.close_windows_and_alert()
        self.switch_to_window(0)
        self.delete_all_cookies()
        try:
            self.execute_script('localStorage.clear()')
        except Exception as e:
            log("Ошибка! %s" % e.args, '[e]')

    def close_windows_and_alert(self):
        """Закрывает все открытые окна, кроме 1.
        Закрывает окно с alert
        Переключается на 1 окно
        """

        self.close_alert()
        revers_windows = self.get_windows[::-1]
        for window in revers_windows:
            self.switch_to_window(strategy='handle', value=window)
            self.close_alert()
            self.refresh()
            self.close_alert()
            if window != revers_windows[-1]:  # если не последнее
                self.close_windows_by_handle(window)

    def close_alert(self):
        """Закрывает alert"""

        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            log('Текст alert: %s' % text, '[i]')
            alert.accept()
            return True
        except (NoAlertPresentException, NoSuchWindowException):
            log('alert не найден', '[d]')
            return False

    def close_windows_by_handle(self, handles):
        """Закрывает окна по хэндлам.

        Закрывает окна по хендлами. Они могут быть переданны в списке
        или один хэндл строкой
        Возвращается в текущее окно, если мы его не закрывали.
        Возвращает true, если отработал
        """
        assert type(handles) in (str, list), 'Неверно передан handle'

        try:
            current_handle = self.driver.current_window_handle
            current_handles = self.get_windows
            if type(handles) == str:
                handle = handles
                if handle in current_handles:
                    self.switch_to_window(strategy='handle', value=handle)
                    self.driver.close()
                    if current_handle != handle:
                        self.switch_to_window(strategy='handle', value=current_handle)
            else:
                for handle in handles:
                    if handle in current_handles:
                        self.switch_to_window(strategy='handle', value=handle)
                        self.driver.close()
                if current_handle not in handles:
                    self.switch_to_window(strategy='handle', value=current_handle)
            return True
        except NoSuchWindowException:
            return False

    def __has_method_log(self):
        """Проверка а есть ли у платформы/браузер метод для получения логов"""

        _browser = self.config.get('BROWSER', 'GENERAL')

        return _browser.lower()

    def flush_js_error(self):
        """Удаляем логи из памяти"""

        if self.__has_method_log():
            return self.driver.get_log('browser')

    def get_js_error(self):
        """Получение js ошибок"""

        logs = self.flush_js_error()
        errors = []
        if logs:
            # оставляем уникальные логи со временем и текстом ошибки
            result = list({error['message']: {'timestamp': error['timestamp'], 'message': error['message'], }
                           for error in logs if error.get('level', None) != 'WARNING'}.values())
            for error in result:
                error['timestamp'] = datetime.fromtimestamp(error['timestamp'] / 1e3).strftime('%d-%m-%Y %H:%M:%S.%f')
                errors.append('{};{}'.format(error['timestamp'], error['message'].replace('\\n', '\n')))
        return errors

    @property
    def site(self):
        """Возвращает текущий url без параметров, только сайт"""

        url = self.current_url
        res = parse.urlparse(url)
        return f'{res.scheme}://{res.netloc}'

    def delete_download_dir(self, make_dir=False):
        """Удаление папки для скачивания файлов"""

        config = Config()
        download_dir = config.get('DOWNLOAD_DIR', "GENERAL")
        if not download_dir:
            return

        # если её нет, значит мы не создали папку
        eth_download_dir = config.get('ETH_DOWNLOAD_DIR', "GENERAL")
        # вторая проверка на всякий пожарный, но такая ситуация невозможна
        # if (eth_download_dir and download_dir) and (eth_download_dir != download_dir):
        if eth_download_dir and download_dir:
            shutil.rmtree(download_dir, True)
            if make_dir:
                os.makedirs(download_dir, exist_ok=True)
