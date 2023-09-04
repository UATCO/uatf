import string

from .report_base import ReporBase, get_tpl_path, config
from .. import Config
from ..report.db.db_model_layout import ResultBDLayout

bd = ResultBDLayout()

with open(get_tpl_path("report_layout/template_layout.html")) as tpl:
    template = string.Template(tpl.read())

with open(get_tpl_path("report_layout/style_layout.css")) as stpl:
    template_css = string.Template(stpl.read())

with open(get_tpl_path("ui_report.js")) as stpl:
    template_js = string.Template(stpl.read())


class ReportLayout(ReporBase):
    """Класс для создания отчета тестов верстки"""

    def __init__(self, file_name: str = None, suite_name: str = None, test_name: str = None,
                 status: str = None,
                 std_out: str = None, start_time: str = None,
                 stop_time: str = None, description: str = None, test_logs: str = None, dif_path: str = None,
                 cur_path: str = None, ref_path: str = None):
        super().__init__()
        self.file_name = file_name
        self.suite_name = suite_name
        self.test_name = test_name
        self.status = status
        self.std_out = std_out
        self.start_time = start_time
        self.stop_time = stop_time
        self.description = description
        self.test_logs = test_logs
        self.dif_path = dif_path
        self.cur_path = cur_path
        self.ref_path = ref_path

    def save_test_result(self):
        """Сохраняем тестовые данные в бд"""

        logs_file_path = ''

        if self.status == 'failed' or config.get('SCREEN_CAPTURE', 'GENERAL') == 'video_present':
            logs_file_path = self.save_test_logs()
        bd.save_test_result(self.file_name, self.suite_name, self.test_name, self.status, self.start_time,
                            self.stop_time, self.std_out, self.description, logs_file_path, self.dif_path,
                            self.cur_path, self.ref_path)

    def change_std_out(self, std_out: str):
        """формируем кусок html-отчета в кликабельными ссылками"""

        new_std_out = ''
        std_lst = std_out.split('\n')
        rs = bd.get_test_results()
        for row in std_lst:
            if rs[0][0] in row:
                _ = row.split()
                file_path = f"""{_[1].split(' ')[-1].replace('"', '')[:-1]}:{_[-3][:-1]}"""
                new_std_out = new_std_out + f'<pre>  {_[0][:7]} <a href="http://localhost:63342/api/file/{file_path}">{file_path}</a> {_[-2]} {_[-1]}</pre>\n'
        return new_std_out

    def create_report(self):
        """Создаем html-отчет"""

        content = ''
        rs = bd.get_test_results()
        for (file_name, suite_name, test_name, status, start_time, stop_time, std_out,
             description, logs_file_path, dif_path, cur_path, ref_path) in rs:

            if status == 'passed':
                status_class = '"status-passed"'
            elif Config().get('CREATE_REPORT_SHOW', 'GENERAL') and status != 'failed':
                status_class = '"status-passed"'
            else:
                status_class = '"status-failed"'

            content = content + f"""
        <tr>
            <td>{file_name}</td>
            <td>{suite_name}</td>
            <td>{test_name}</td>
            <td>{description}</td>
            <td class={status_class}>{status}</td>
            <td>{start_time}</td>
            <td>{stop_time}</td>
            <td class="std_out">
                {self.change_std_out(std_out) if bool(std_out) else ''}
                <p><a href={logs_file_path}>Логи теста.</a></p>
                <p><a href={cur_path}>Эталонная верстка.</a></p>
                <p><a href={ref_path}>Текущая верстка.</a></p>
            </td>
            <td><img src={dif_path}></td>
        """

        final_output = template.safe_substitute(content=content)
        with open("artifact/report.html", "w") as output:
            output.write(final_output)

        with open('artifact/style.css', 'w') as style:
            style.write(template_css.template)

        with open('artifact/report.js', 'w') as style:
            style.write(template_js.template)
