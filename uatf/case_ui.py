from .case import Case
from .logfactory import log


class TestCaseUI(Case):

    @classmethod
    def _setup_class_framework(cls):
        """Общие действия перед запуском всех тестов"""

        log('_setup_class_framework', '[d]')

    def _setup_framework(self, request):
        """Общие действия перед запуском каждого теста"""

        super()._setup_framework(request)
        log('_setup_framework', '[d]')

    def _teardown_framework(self, request, subtests):
        """Общие действия после прохода каждого теста"""

        super()._teardown_framework(request, subtests)
        log('_teardown_framework', '[d]')

    @classmethod
    def _teardown_class_framework(cls):
        """Общие действия после прохода всех тестов"""

        log('_teardown_class_framework', '[d]')
