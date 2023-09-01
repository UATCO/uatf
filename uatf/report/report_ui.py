import datetime
import hashlib
import os
import random
import string
from .db_model import ResultBDUI
from .. import Config, log
from ..helper import save_artifact, get_artifact_path
from ..ui.screen_capture import make_gif, make_video, add_screen_for_gif
from string import Template
from ..ui.browser import Browser

bd = ResultBDUI()
config = Config()


def get_tpl_path(file_name: str):
    """Получаем путь до шаблонов"""

    lib_path = os.path.split(__file__)[0]
    file = os.path.join(lib_path, 'templates', file_name)
    return file


with open(get_tpl_path("report_ui/template_ui.html")) as tpl:
    template = string.Template(tpl.read())

with open(get_tpl_path("report_ui/style_ui.css")) as stpl:
    template_css = string.Template(stpl.read())

with open(get_tpl_path("ui_report.js")) as stpl:
    template_js = string.Template(stpl.read())


class ReportUI:
    """Класс для создания отчета"""

    def __init__(self, driver=None, file_name: str = None, suite_name: str = None, test_name: str = None,
                 status: str = None,
                 std_out: str = None, start_time: str = None,
                 stop_time: str = None, description: str = None, fail_screen: str = None, test_logs: str = None):
        self.file_name = file_name
        self.suite_name = suite_name
        self.test_name = test_name
        self.status = status
        self.std_out = std_out
        self.start_time = start_time
        self.stop_time = stop_time
        self.driver = driver
        self.description = description
        self.template_report = self.load_template('report_ui/report.template')
        self.str_report = None
        self.fail_screen = fail_screen
        self.browser = Browser(self.driver)
        self.test_logs = test_logs

    def save_test_result(self):
        """Сохраняем тестовые данные в бд"""

        gif_path = img_path = logs_file_path = ''
        if config.get('SCREEN_CAPTURE', 'GENERAL') == 'gif':
            gif_path, img_path = self.generate_gif()
        elif config.get('SCREEN_CAPTURE', 'GENERAL') == 'video' or config.get('SCREEN_CAPTURE',
                                                                              'GENERAL') == 'video_present':
            gif_path, img_path = self.generate_video()
        if self.status == 'failed' or config.get('SCREEN_CAPTURE','GENERAL') == 'video_present':
            logs_file_path = self.save_test_logs()
        bd.save_test_result(self.file_name, self.suite_name, self.test_name, self.status, self.start_time,
                            self.stop_time, self.std_out, img_path, gif_path, self.description, logs_file_path)
        config.set_option('SCREENSHOT_LIST', [], 'GENERAL')

    def create_report(self):
        """Создаем html-отчет"""

        content = ''
        rs = bd.get_test_results()
        for (file_name, suite_name, test_name, status, start_time, stop_time, std_out, img_path, gif_path,
             description, logs_file_path) in rs:

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
            </td>
            {'<td></td>' if status == 'passed' and not Config().get('CREATE_REPORT_SHOW', 'GENERAL') else f'<td><a href={gif_path}><img src={img_path} alt="Видео падения"></a></td>'}
            
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
            if '^' in row:
                continue
            if std_lst.index(row) in [1, 3, 6]:
                _ = row.split()
                file_path = f"""{_[1].split(' ')[-1].replace('"', '')[:-1]}:{_[-3][:-1]}"""
                new_std_out = new_std_out + f'<pre>  {_[0][:7]} <a href="http://localhost:63342/api/file/{file_path}">{file_path}</a> {_[-2]} {_[-1]}</pre>\n'
            else:
                new_std_out = new_std_out + f'<pre>{row}</pre>\n'
        return new_std_out

    def generate_gif(self):
        """Генерируем GIF"""

        gif_name, last_img = make_gif(self.driver)
        return gif_name, last_img

    def generate_video(self):
        """Генерируем видео падения"""

        vedeo_path, last_img = make_video()
        return vedeo_path, last_img

    @staticmethod
    def load_template(template_name):
        """Загружаем шаблон"""

        lib_path = os.path.split(__file__)[0]
        file = os.path.join(lib_path, 'templates', template_name)
        if os.path.isfile(file):
            with open(file, encoding='utf-8') as file:
                data = file.read()
            return Template(data)
        else:
            raise FileNotFoundError('Не найден файл шаблона: %s' % os.path.abspath(file))

    def generate_console_error(self):
        """Выводим доп информацию о падении"""

        self.str_report = self.template_report.substitute(
            screenshots=self.fail_screen
        )

    def generate(self):

        self.get_screenshot_window()
        self.generate_console_error()
        log(self.str_report)

    def get_screenshot_window(self):
        """Делает скрин открытого окна"""

        self.fail_screen = self.get_screenshot(True)

    def get_screenshot(self, origin_name=False):
        """Делает скрин текущего окна"""

        screenshot = self.browser.get_screenshot()
        file_name = hashlib.md5(screenshot).hexdigest() + '.jpg'
        file_name, _http = save_artifact(file_name, screenshot, folder='screenshots', mode='wb')
        if not origin_name:
            return _http
        else:
            return file_name

    def save_test_logs(self):
        """Сохраняем тестовые логи"""

        file_name = f"{self.file_name}_{self.suite_name}_{self.test_name}_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')}.txt"
        path = os.path.join(get_artifact_path('tests_logs'), file_name)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(self.test_logs + '\n\n')
            file.write(self.std_out)
        return path
