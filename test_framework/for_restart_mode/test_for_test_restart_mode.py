import time

import pytest
from uatf import *


class TestFailAndSuccess(TestCase):

    def test_fail(self):
        log('ТестЛоговУпавший')
        time.sleep(1)
        pytest.fail('Упал')

    def test_success(self):
        time.sleep(1)
        log('ТестЛоговУспешный')

    def test_for_sub(self, subtests):
        with subtests.test():
            pytest.fail('fail subtest')

    def test_for_skip_sub(self, subtests):
        with subtests.test():
            pytest.skip('skip subtest')