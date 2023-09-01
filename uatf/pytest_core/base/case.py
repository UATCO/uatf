import os

import pytest
import requests

from ...logfactory import log
from ...config import Config
from ...helper import create_artifact_folder


class TestCase:
    """Класс для создания инстанса с набором тестов"""

    config = Config()
    name_class: str = ''

    create_artifact_folder()

    @classmethod
    def _setup_class_framework(cls):
        """Общие действия перед запуском всех тестов"""

        log('_general_setup_class.start', '[d]')
        log('{0}_setup_class framework{0}'.format('=' * 10), '[d]')
        url = cls.config.get('SITE', 'GENERAL')
        assert cls.check_service(url) is True, 'Сервис недоступен'

        if cls.config.get('CREATE_REPORT_DEBUG', 'GENERAL'):
            from ...report.db_model import ResultBD
            ResultBD().setup()

        log('_general_setup_class.end', '[d]')

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def _base_setup_class(cls, request):
        """Это нужно чтобы эмулировать поведение uatf, когда при падении setup вызывается teardown

        https://docs.pytest.org/en/6.2.x/xunit_setup.html
        teardown functions are not called if the corresponding setup function existed and failed/was skipped.
        """
        _cls = request.node.obj
        _cls.name_class = request.node.name
        request.addfinalizer(cls._teardown_class_framework)
        request.addfinalizer(cls.tearDownClass)
        cls._setup_class_framework()
        cls.setUpClass()

    def _setup_framework(self, request):
        """Общие действия перед запуском каждого теста"""

        log('_general_setup.start', '[d]')
        self._set_test_name_to_config()
        doc = request.node.obj.__doc__
        if doc:
            test_name = '%s - %s' % (self.test_method_name, doc)
        else:
            test_name = self.test_method_name
        log("TEST NAME: {}".format(test_name), "[f]")

        site = self.config.get('SITE', 'GENERAL')
        if site:
            log(f'SITE: {site}', '[f]')
        log('_general_setup.end', '[d]')

    @classmethod
    def setUpClass(cls):
        """action test"""

    def _set_test_name_to_config(self):
        full_test_name = f'{self.name_class}.{self.test_method_name}'
        self.config.set_option('ATF_TEST_NAME', full_test_name, 'GENERAL')

    @pytest.fixture(autouse=True)
    def _base_setup(self, request, subtests):
        """base method for call teardown after failed setup"""
        test = request.node
        self.test_method_name = test.name

        def teardown():
            with subtests._test(postfix='teardown', teardown=True):
                self.tearDown()
            self._teardown_framework(request, subtests)

        request.addfinalizer(teardown)

        self._setup_framework(request)
        self.setUp()

    def setUp(self):
        """action test"""

    def tearDown(self):
        """action test"""

    def _teardown_framework(self, request, subtests):
        """action framework"""

    @classmethod
    def tearDownClass(cls):
        """action suite"""

    @classmethod
    def _teardown_class_framework(cls):
        """Общие действия перед запуском каждого теста

        для классов TestCase и TestCaseUI
        """
        log('{0}_teardown_class framework{0}'.format('=' * 10), '[d]')

    @staticmethod
    def check_service(url):
        """Проверка доступности сайта

        :param url: адрес сайта
        """
        try:
            response = requests.get(url, verify=Config().get('API_SSL_VERIFY', 'GENERAL'))
            result = response.status_code < 500
            log("Сайт (сервис) '%s' доступен. Код ответа: %d %s" %
                (url, response.status_code, response.text), '[d]')
        except Exception as err:
            log(f'Ошибка проверки url: {url}\n' + str(err))
            result = False
        return result
