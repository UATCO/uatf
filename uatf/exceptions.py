"""Модуль для базовых исключений framework"""


class UATFBaseException(AssertionError):
    """Базовое исключение в atf"""

    def __init__(self, msg, report=None, **kwargs):
        super().__init__(msg)
        self.msg = msg
        self.report = report
        self.jc_params = kwargs

    def get_report(self):
        return self.report


class ElementException(UATFBaseException):
    """используется в should_be в ui"""

    def __init__(self, msg, report=None, element=None):
        super().__init__(msg, report=report)
        self.element = element
        self.error_reason = element.get_po_path()


class BrowserException(UATFBaseException):
    """используется в should_be в api"""
