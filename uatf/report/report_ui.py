import os
import string
import sqlite3
from .bd_model import ResultBD

bd = ResultBD()
with open("/Users/artur_gaazov/Documents/uatf/uatf/report/template_ui.html") as tpl:
    template = string.Template(tpl.read())


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
        content = ''
        rs = bd.get_test_results()
        for (file_name, suite_name, test_name, status, start_time, stop_time, std_out) in rs:
            content = content + f"""        <tr>
            <td>{file_name}</td>
            <td>{suite_name}</td>
            <td>{test_name}</td>
            <td>{status}</td>
            <td>{start_time}</td>
            <td>{stop_time}</td>
        <td><pre>{std_out}</pre></td>
        </tr>\n"""

        final_output = template.safe_substitute(content=content)
        with open("report.html", "w") as output:
            output.write(final_output)
