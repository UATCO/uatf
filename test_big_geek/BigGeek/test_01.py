from uatf import *
from uatf.ui import *

class Test(TestCaseUI):

    def setUp(self):
        log('setUp')

    def test_01(self):
        log('test_01')

    def test_02(self):
        log('test_02')

    def tearDown(self):
        log('tearDown')