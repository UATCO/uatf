import os
import string
import sqlite3
from .bd_model import ResultBD

bd = ResultBD()


def get_tpl_path(file_name: str):
    """Получаем путь до шаблонов"""

    lib_path = os.path.split(__file__)[0]
    file = os.path.join(lib_path, 'templates', file_name)
    return file


with open(get_tpl_path("template_ui.html")) as tpl:
    template = string.Template(tpl.read())

with open(get_tpl_path("style_ui.css")) as stpl:
    template_css = string.Template(stpl.read())


class ReportUI:
    """Класс для создания отчета"""

    def __init__(self, file_name: str = None, suite_name: str = None, test_name: str = None, status: str = None,
                 std_out: str = None, start_time: str = None,
                 stop_time: str = None):
        self.file_name = file_name
        self.suite_name = suite_name
        self.test_name = test_name
        self.status = status
        self.std_out = std_out
        self.start_time = start_time
        self.stop_time = stop_time

    def save_test_result(self):
        """Сохраняем тестовые данные в бд"""

        bd.save_test_result(self.file_name, self.suite_name, self.test_name, self.status, self.start_time,
                            self.stop_time, self.std_out)

    def create_report(self):
        """Создаем html-отчет"""
        content = ''
        rs = bd.get_test_results()
        for (file_name, suite_name, test_name, status, start_time, stop_time, std_out) in rs:
            content = content + f"""
        <tr>
            <td>{file_name}</td>
            <td>{suite_name}</td>
            <td>{test_name}</td>
            <td class={'"status-failed"' if status == 'failed' else '"status-passed"'}>{status}</td>
            <td>{start_time}</td>
            <td>{stop_time}</td>
            <td class="std_out"><pre>{std_out}</pre></td>
        </tr>\n"""

        final_output = template.safe_substitute(content=content)
        with open("artifact/report.html", "w") as output:
            output.write(final_output)

        with open('artifact/style.css', 'w') as style:
            style.write(template_css.template)
