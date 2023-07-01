import os
import shutil
import tempfile

from selenium import webdriver
from ..config import Config
from ..logfactory import log


class RunBrowser:
    """Класс для запуска браузеров"""

    def __init__(self):
        self.config = Config()
        self.driver = None
        if self.config.options['GENERAL']['BROWSER'] == 'chrome':
            self.run_chrome()

    def run_chrome(self):
        """Запускаем хром"""

        options = webdriver.ChromeOptions()
        logging_prefs = {'browser': self.config.get('BROWSER_LOG_LEVEL', 'GENERAL')}
        options.set_capability('goog:loggingPrefs', logging_prefs)
        self._set_download_dir(options)

        self.driver = webdriver.Chrome()
        log("BROWSER: Chrome", '[f]')

    def _set_download_dir(self, options):
        """Устанавливает дирректорию для скачивания файлов
        :param options: опции для запуска браузера
        """
        local_download_dir = self.config.get('DOWNLOAD_DIR', 'GENERAL')

        if local_download_dir:
            self._create_download_dir()
            dir_download = self.config.get('DOWNLOAD_DIR_BROWSER', 'GENERAL')
            download_path = {"download.default_directory": dir_download,
                             "profile.default_content_settings.multiple-automatic-downloads": 1}
            options.add_experimental_option("prefs", download_path)
        return options

    def _create_download_dir(self):
        """Создание папки для загрузки файлов"""

        download_dir_browser = self.config.get('DOWNLOAD_DIR_BROWSER', 'GENERAL')
        local_download_dir = self.config.get('DOWNLOAD_DIR', 'GENERAL')

        # создаем локальную директорию, если надо
        if local_download_dir:
            # если несколько классов в 1 файле с тестами,
            # чтобы не создавать temp папки в temp папке
            if not self.config.get('ETH_DOWNLOAD_DIR', 'GENERAL'):
                self.config.set_option('ETH_DOWNLOAD_DIR', local_download_dir, 'GENERAL')
            if not self.config.get('ETH_DOWNLOAD_DIR_BROWSER', 'GENERAL'):
                self.config.set_option('ETH_DOWNLOAD_DIR_BROWSER', download_dir_browser, 'GENERAL')
            download_path = self.config.get('ETH_DOWNLOAD_DIR', 'GENERAL')
            download_dir_browser = self.config.get('ETH_DOWNLOAD_DIR_BROWSER', 'GENERAL')
            if download_path:
                if not os.path.exists(download_path):
                    os.mkdir(download_path)
                    assert os.path.exists(download_path) is True, \
                        "Не смогли создать темповую директорию %s" % download_path
                tmp_path = tempfile.mkdtemp(dir=download_path)
                os.chmod(tmp_path, 0o775)
                self.config.set_option('DOWNLOAD_DIR', tmp_path, 'GENERAL')
                tmp_name = os.path.split(tmp_path)[-1]

                # задаем путь для скачивания в браузере
                if download_dir_browser:
                    self.config.set_option('DOWNLOAD_DIR_BROWSER', '\\'.join((download_dir_browser, tmp_name)), 'GENERAL')
                else:
                    self.config.set_option('DOWNLOAD_DIR_BROWSER', self.config.get('DOWNLOAD_DIR', 'GENERAL'), 'GENERAL')
