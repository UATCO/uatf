from uatf import *
import pytest


class TestFirst(TestCaseUI):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_01(self):
        log('test_01')
        assert 1 == 1

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
