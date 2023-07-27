import os
import string
import sqlite3
from .bd_model import ResultBD
from .. import Config
from ..ui.screen_capture import make_gif, make_video

bd = ResultBD()
config = Config()


def get_tpl_path(file_name: str):
    """Получаем путь до шаблонов"""

    lib_path = os.path.split(__file__)[0]
    file = os.path.join(lib_path, 'templates', file_name)
    return file


with open(get_tpl_path("template_ui.html")) as tpl:
    template = string.Template(tpl.read())

with open(get_tpl_path("style_ui.css")) as stpl:
    template_css = string.Template(stpl.read())

with open(get_tpl_path("ui_report.js")) as stpl:
    template_js = string.Template(stpl.read())


class ReportUI:
    """Класс для создания отчета"""

    def __init__(self, driver=None, file_name: str = None, suite_name: str = None, test_name: str = None,
                 status: str = None,
                 std_out: str = None, start_time: str = None,
                 stop_time: str = None):
        self.file_name = file_name
        self.suite_name = suite_name
        self.test_name = test_name
        self.status = status
        self.std_out = std_out
        self.start_time = start_time
        self.stop_time = stop_time
        self.driver = driver

    def save_test_result(self):
        """Сохраняем тестовые данные в бд"""

        gif_path = img_path = ''
        if config.get('SCREEN_CAPTURE', 'GENERAL') == 'gif':
            gif_path, img_path = self.generate_gif()
        elif config.get('SCREEN_CAPTURE', 'GENERAL') == 'video':
            gif_path, img_path = self.generate_video()
        bd.save_test_result(self.file_name, self.suite_name, self.test_name, self.status, self.start_time,
                            self.stop_time, self.std_out, img_path, gif_path)

    def create_report(self):
        """Создаем html-отчет"""

        content = ''
        rs = bd.get_test_results()
        for (file_name, suite_name, test_name, status, start_time, stop_time, std_out, img_path, gif_path) in rs:
            content = content + f"""
        <tr>
            <td>{file_name}</td>
            <td>{suite_name}</td>
            <td>{test_name}</td>
            <td class={'"status-failed"' if status == 'failed' else '"status-passed"'}>{status}</td>
            <td>{start_time}</td>
            <td>{stop_time}</td>
            <td class="std_out">
                {self.change_std_out(std_out) if bool(std_out) else ''}
            </td>
            {f'<td><a href={gif_path}><img src={img_path} alt="Видео падения"></a></td>' if status == 'failed' else '<td></td>'}
            
        </tr>\n"""

        final_output = template.safe_substitute(content=content)
        with open("artifact/report.html", "w") as output:
            output.write(final_output)

        with open('artifact/style.css', 'w') as style:
            style.write(template_css.template)

        with open('artifact/report.js', 'w') as style:
            style.write(template_js.template)

    def change_std_out(self, std_out: str):
        """формируем кусок html-отчета в кликабельными ссылками"""

        new_std_out = ''
        std_lst = std_out.split('\n')
        for row in std_lst:
            if std_lst.index(row) in [1, 3, 5]:
                _ = row.split()
                file_path = f"""{_[1].split(' ')[-1].replace('"', '')[:-1]}:{_[-3][:-1]}"""
                new_std_out = new_std_out + f'<pre>  {_[0][:7]} <a href="http://localhost:63342/api/file/{file_path}">{file_path}</a> {_[-2]} {_[-1]}</pre>\n'
            else:
                new_std_out = new_std_out + f'<pre>{row}</pre>\n'
        return new_std_out

    def generate_gif(self):
        """Генерируем GIF"""

        gif_name, last_img = '', None
        if config.get("SCREEN_CAPTURE", 'GENERAL').lower() == 'gif':
            gif_name, last_img = make_gif(self.driver)
        return gif_name, last_img

    def generate_video(self):
        """Генерируем видео падения"""

        vedeo_path, last_img = '', None
        if config.get("SCREEN_CAPTURE", 'GENERAL').lower() == 'video':
            vedeo_path, last_img = make_video()
        return vedeo_path, last_img

