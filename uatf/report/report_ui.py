import hashlib
import os
import string
from ..report.db.db_model_ui import ResultBDUI
from .. import Config, log
from ..helper import save_artifact
from ..ui.screen_capture import make_gif, make_video
from ..ui.browser import Browser
from ..report.report_base import ReporBase

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


class ReportUI(ReporBase):
    """Класс для создания отчета"""

    def __init__(self, driver=None, file_name: str = None, suite_name: str = None, test_name: str = None,
                 status: str = None,
                 std_out: str = None, start_time: str = None,
                 stop_time: str = None, description: str = None, fail_screen: str = None, test_logs: str = None):
        super().__init__()
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
        if self.status == 'failed' or config.get('SCREEN_CAPTURE', 'GENERAL') == 'video_present':
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

    def generate_gif(self):
        """Генерируем GIF"""

        gif_name, last_img = make_gif(self.driver)
        return gif_name, last_img

    def generate_video(self):
        """Генерируем видео падения"""

        vedeo_path, last_img = make_video()
        return vedeo_path, last_img

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
