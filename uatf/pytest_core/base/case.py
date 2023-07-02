import pytest


class Case:
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
        """Общие действия перед запуском всех тестов"""

    def _setup_framework(self, request):
        """Общие действия перед запуском каждого теста"""

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

    def _teardown_framework(self, request, subtests):
        """Общие действия после прохода каждого теста"""

    @classmethod
    def _teardown_class_framework(cls):
        """Общие действия после прохода всех тестов"""
