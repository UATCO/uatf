from uatf import *
import pytest


class TestFirst(TestCase):
    @classmethod
    def setUpClass(cls):
        print('setUpClass')

    def setUp(self):
        print('setUp')

    def test_01(self):
        log('Привет')
        assert 1 == 1

    def tearDown(self):
        print('tearDown')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')


