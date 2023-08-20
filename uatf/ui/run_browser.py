import os
import tempfile

from selenium import webdriver
from ..config import Config
from ..logfactory import log


class RunBrowser:
    """Класс для запуска браузеров"""

    max_headless_resolution = ('1920', '1000')

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

        if self.config.GENERAL.get('CHROME_MOBILE_EMULATION'):
            chrome_mobile_emulation = self.config.GENERAL.get('CHROME_MOBILE_EMULATION')
            devices = ('iPad Mini', 'iPhone SE', 'iPhone X', 'iPhone XR', 'Pixel 5', 'Galaxy Tab S4')
            if chrome_mobile_emulation not in devices:
                raise ValueError(f"Выбрано неверное устройство {chrome_mobile_emulation}, " 
                                 f"список поддерживаемых устройств:\n{chr(10).join(devices)}")
            mobile_emulation = {"deviceName": chrome_mobile_emulation}
            options.add_experimental_option('mobileEmulation', mobile_emulation)

        self._set_download_dir(options)

        prefs = options.experimental_options.get('prefs')

        custom_pref = {"plugins.plugins_disabled": ["Adobe Flash Player"],
                       "browser.enable_spellchecking": False,
                       "safebrowsing.enabled": True,  # xml
                       'download.prompt_for_download': False,
                       'download.directory_upgrade': True,
                       'safebrowsing.disable_download_protection': True}

        local_state = {
            # chrome flags (@1 - True, @2 False)
            "browser.enabled_labs_experiments": [
                # была бага что не в HEADLESS не мог захватить фокус, вроде бы починили уже
                "calculate-native-win-occlusion@2",
                # включение по умолчанию запрета на скачивание MixedContent
                'treat-unsafe-downloads-as-active-content@1'
            ],
        }

        if prefs:
            prefs.update(custom_pref)
        else:
            prefs = custom_pref

        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('localState', local_state)
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", '--enable-logging'])
        options.add_argument("--always-authorize-plugins=true")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--disable-notifications')
        options.add_argument("--disable-logging")
        options.add_argument("--start-maximized")
        options.add_argument("--safebrowsing-disable-download-protection")
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--disable-backgrounding-occluded-windows')

        headless_mode = self.config.get('HEADLESS_MODE', 'GENERAL')
        if headless_mode:
            resolution = self.config.get('BROWSER_RESOLUTION', 'GENERAL')
            options.add_argument(f"--headless={headless_mode}")
            options.add_argument("--lang=ru-RU")

            size = resolution.split('x') if resolution else self.max_headless_resolution
            options.add_argument("--window-size={},{}".format(*size))

        if self.config.get('DISABLE_GPU', 'GENERAL') or headless_mode:
            options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)
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
                    self.config.set_option('DOWNLOAD_DIR_BROWSER', '\\'.join((download_dir_browser, tmp_name)),
                                           'GENERAL')
                else:
                    self.config.set_option('DOWNLOAD_DIR_BROWSER', self.config.get('DOWNLOAD_DIR', 'GENERAL'),
                                           'GENERAL')
