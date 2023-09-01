from typing import Dict, Any, Callable

from .db_model import DB
from ..config import Config
from ..helper import get_artifact_path
from ..pytest_core.plugin import check_success_status, Status
from ..logfactory import log

CONFIG = Config()


def empty(*args: Any, **kwargs): ...


def save(f: Callable) -> Callable:
    def tmp(*args: Any, **kwargs: Any) -> None:
        if CONFIG.get('CACHE_ENABLE', 'GENERAL'):
            return f(*args, **kwargs)
        else:
            return empty(*args, **kwargs)
    return tmp


class CacheResults:

    def __init__(self, path=None):
        self.db = DB(path)
        self.config = CONFIG
        self.is_last_run = not self.config.get('RESTART_AFTER_BUILD_MODE', 'GENERAL')

    def init(self, restart_failed=False):
        self.db.setup(restart_failed)

    @save
    def save_test_result(self, reports):
        for report in reports:
            is_success = check_success_status(report.status)
            if (self.is_last_run and not is_success) or is_success:
                self.db.save_test_result(report.file_name, report.suite_name, report.test_name, report.status)
            if not is_success:
                self.db.save_failed_tests(report.file_name, report.suite_name, report.test_name)
        self.db.conn.commit()

    @save
    def delete_failed_tests(self):
        self.db.delete_failed_tests()

    def get_failed_tests(self):
        return self.db.get_failed_tests()

    def get_tests_counters(self) -> Dict[str, int]:
        """Считаем общее число успешных или выключенных тестов"""

        if not self.config.device_name and self.config.get('JENKINS_CONTROL_ADDRESS', 'GENERAL'):
            return self.db.get_counters()
        else:
            return dict()

    @save
    def save_build_result(self, exec_time):
        """Save build result"""

        exec_time_cache = self.get_sum_exec_time()
        if not exec_time_cache:
            exec_time_cache = exec_time
        exec_time_cache = round(exec_time_cache, 0)
        counters = self.get_counters()

    def exists_failed_tests(self) -> int:
        """Наличие упавших тестов"""

        return self.db.exists_failed_tests()

    @save
    def save_exec_time(self):
        if not self.config.restart_failed_tests:
            for file, exec_time in self.db.get_exec_time_from_test_results():
                self.db.save_exec_time(file_name=file, exec_time=exec_time)
            self.db.conn.commit()

    def get_exec_time_files(self):
        return self.db.get_exec_time_files()

    def get_sum_exec_time(self):
        return self.db.get_sum_exec_time()

    def get_counters(self):
        cursor = self.db.get_counters()
        counters = dict(skip=0, success=0, failed=0)
        for status, count in cursor:
            if status == Status.SKIPPED:
                counters['skip'] += count
            elif check_success_status(status):
                counters['success'] += count
            else:
                counters['failed'] += count
        return counters

    @save
    def save_build(self, test_files: list, folder: str, exec_time: float):
        self.save_exec_time()
        self.save_build_result(exec_time)

    @save
    def save_bl_method_call(self, method_name, host):
        """Сохранить название вызванного метода и стенд в БД"""

        return self.db.save_bl_method(method_name, host)

    def generate_regression_report(self) -> None:
        if self.config.get('GENERATE_HTML_REPORT', 'REGRESSION'):
            log('Генерируем отчет тестов вестки')
            from ..ui.layout.reporter import make_report
            from ..ui.layout.main import convert_regression_suite_name
            report_dir = get_artifact_path('regression')
            flaky_results_db = self.db.get_failed_tests()
            flaky_nodeid = [f"{convert_regression_suite_name(i[1])}::{i[2]}" for i in flaky_results_db]
            make_report(report_dir, flaky_nodeid)
