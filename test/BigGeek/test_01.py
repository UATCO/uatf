from uatf import *
from uatf.ui import *

class Test(TestCaseUI):

    def setUp(self):
        log('setUp')

    def test(self):
        log('test')

    def tearDown(self):
        log('tearDown')