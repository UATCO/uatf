import datetime
import os

from ..helper import get_artifact_path
from ..report.db.db_model_ui import ResultBDUI
from .. import Config
from string import Template

config = Config()


def get_tpl_path(file_name: str):
    """Получаем путь до шаблонов"""

    lib_path = os.path.split(__file__)[0]
    file = os.path.join(lib_path, 'templates', file_name)
    return file


class ReporBase:
    """Класс для создания отчета"""

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
        self.product_name = None

    def change_std_out(self, std_out: str):
        """формируем кусок html-отчета в кликабельными ссылками"""

        new_std_out = ''
        std_lst = std_out.split('\n')
        for row in std_lst:
            if '^' in row:
                continue
            if std_lst.index(row) in [1, 3, 5]:
                _ = row.split()
                file_path = f"""{_[1].split(' ')[-1].replace('"', '')[:-1]}:{_[-3][:-1]}"""
                new_std_out = new_std_out + f'<pre>  {_[0][:7]} <a href="http://localhost:63342/api/file/{file_path}">{file_path}</a> {_[-2]} {_[-1]}</pre>\n'
            else:
                new_std_out = new_std_out + f'<pre>{row}</pre>\n'
        return new_std_out

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

    def save_test_logs(self):
        """Сохраняем тестовые логи"""

        file_name = f"{self.file_name}_{self.suite_name}_{self.test_name}_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')}.txt"
        path = os.path.join(get_artifact_path('tests_logs'), file_name)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(self.test_logs + '\n\n')
            file.write(self.std_out)
        return path.split('artifact')[1][1:]

    def get_product_name(self):
        """Получаем имя продукта"""

        self.product_name = config.get('WORKSPACE', 'GENERAL').split('workspace')[-1].split('\\')[0]
