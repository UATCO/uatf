from uatf import *
import pytest


class TestFirst(TestCase):
    @classmethod
    def setUpClass(cls):
        log('setUpClass')

    def setUp(self):
        log('setUp')

    def test_01(self):
        log('test_01')
        assert 1 == 1

    def tearDown(self):
        log('tearDown')

    @classmethod
    def tearDownClass(cls):
        log('tearDownClass')


