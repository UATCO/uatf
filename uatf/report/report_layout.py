import os
import string

from uatf import Config
from uatf.report.db_model import ResultBDUI

bd = ResultBDUI()
config = Config()


def get_tpl_path(file_name: str):
    """Получаем путь до шаблонов"""

    lib_path = os.path.split(__file__)[0]
    file = os.path.join(lib_path, 'templates', file_name)
    return file


with open(get_tpl_path("report_layout/template_ui.html")) as tpl:
    template = string.Template(tpl.read())

# with open(get_tpl_path("style_ui.css")) as stpl:
#     template_css = string.Template(stpl.read())
#
with open(get_tpl_path("ui_report.js")) as stpl:
    template_js = string.Template(stpl.read())


class ReportLayout:
    """Класс для создания отчета тестов верстки"""

    def __init__(self, file_name: str = None, suite_name: str = None, test_name: str = None,
                 status: str = None,
                 std_out: str = None, start_time: str = None,
                 stop_time: str = None, description: str = None, test_logs: str = None):
        self.file_name = file_name
        self.suite_name = suite_name
        self.test_name = test_name
        self.status = status
        self.std_out = std_out
        self.start_time = start_time
        self.stop_time = stop_time
        self.description = description
        self.test_logs = test_logs
