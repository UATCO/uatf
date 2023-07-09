import pytest
from uatf.ui import *
from uatf import *


class TestBrowser(TestCaseUI):

    @classmethod
    def setUpClass(cls):
        cls.config.WAIT_ELEMENT_LOAD = 1

    def test_execute_script(self):
        self.browser.open('data:,')
        try:
            self.browser.execute_script('$("div")')
            pytest.fail('Должно вызваться исключение')
        except AssertionError:
            pytest.fail('Должно вызваться исключение')
        except Exception:
            pass

    def test_action(self):
        """Проверка action в браузер"""

        self.browser.open('https://sbis.ru')
        assert self.browser.actions
        self.browser.move_cursor_by_offset(1, 1)
