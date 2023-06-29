import pytest


class TestCase:
    """Класс для создания инстанса с набором тестов"""

    @classmethod
    def setUpClass(cls):
        """action test"""

    def setUp(self):
        """action test"""

    def tearDown(self):
        """action test"""

    @classmethod
    def tearDownClass(cls):
        """action suite"""

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def _base_setup_class(cls, request):
        """Это нужно чтобы эмулировать поведение atf, когда при падении setup вызывается teardown

        https://docs.pytest.org/en/6.2.x/xunit_setup.html
        teardown functions are not called if the corresponding setup function existed and failed/was skipped.
        """
        _cls = request.node.obj
        _cls.name_class = request.node.name
        request.addfinalizer(cls._teardown_class_framework)
        request.addfinalizer(cls.tearDownClass)
        cls._setup_class_framework()
        cls.setUpClass()

    @classmethod
    def _setup_class_framework(cls):
        """Общие действия перед запуском тестов"""

    @classmethod
    def _teardown_class_framework(cls):
        """Общие действия перед запуском каждого теста"""
