import os

from selenium.common import UnexpectedAlertPresentException

from .base_case_ui import BaseCaseUI
from ...logfactory import log
from ...ui.run_browser import RunBrowser
from ...ui.browser import Browser


class TestCaseUI(BaseCaseUI):

    @classmethod
    def start_browser(cls):
        """Запускаем браузер"""

        cls.driver = RunBrowser().driver
        cls.browser = Browser(cls.driver)

    @classmethod
    def _setup_class_framework(cls):
        """Общие действия перед запуском всех тестов"""

        log('_setup_class_framework', '[d]')
        super()._setup_class_framework()
        url = cls.config.get('SITE', 'GENERAL')
        assert cls.check_service(url) is True, 'Сервис недоступен'
        cls.browser.open(url)

    def _setup_framework(self, request):
        """Общие действия перед запуском каждого теста"""

        log('_setup.start', '[d]')
        super()._setup_framework(request)

        try:
            _ = self.driver.current_url
        except UnexpectedAlertPresentException:
            self.browser.close_alert()

        try:
            full_test_name = self.config.get('ATF_TEST_NAME', 'GENERAL')
            self.browser.add_cookie('autotest', full_test_name)
        except Exception as err:
            log(f'Не смогли выставить тестовую куку\n{err}', '[d]')

        if self.browser:
            self.browser.flush_js_error()

        log('_setup.end', '[d]')

    def _teardown_framework(self, request, subtests):
        """Общие действия после прохода каждого теста"""

        super()._teardown_framework(request, subtests)

        if self.config.get('COVERAGE', 'REGRESSION') or self.config.get('BROWSER_CHROME_COVERAGE', 'GENERAL'):
            report = getattr(request.node, 'report', None)
            if report is not None:
                from ..plugin import check_success_status
                if self.config.is_last_run or check_success_status(report.status):
                    file_name = os.path.basename(request.module.__file__)
                    self.browser.collect_js_coverage(file_name, self.name_class, self.test_method_name)

        if self.config.get('CHECK_JS_ERROR', "GENERAL"):
            if self.config.get('BROWSER', 'GENERAL'):
                errors = self.browser.get_js_error()
                if errors:
                    with subtests._test('teardown_js_errors', teardown=True):
                        str_errors = "\n".join(errors)
                        assert len(errors) == 0, f'Найдены js ошибки в консоли:\n{str_errors}'
            else:
                log("Проверка консоли возможно только в Google Chrome")

        if not self.config.get('DO_NOT_RESTART', 'GENERAL'):
            self.browser.delete_download_dir()
            if self.browser:  # если не инициализировался браузер то он будет None
                self.browser.quit()
        elif self.config.get('DO_NOT_RESTART', 'GENERAL') and self.config.get('SOFT_RESTART', 'GENERAL'):
            self.browser.soft_restart()

        if self.config.get('DO_NOT_RESTART', 'GENERAL') and self.config.get('CLEAR_DOWNLOAD_DIR', 'GENERAL'):
            self.browser.delete_download_dir(True)

    @classmethod
    def _teardown_class_framework(cls):
        """Общие действия после прохода всех тестов"""

        log('_teardown_class_framework', '[d]')
        super()._teardown_class_framework()
        if cls.config:
            Browser().delete_download_dir()
            if cls.driver and cls.config.get('DO_NOT_RESTART', 'GENERAL'):
                cls.browser.quit()

        from ...report.report_ui import ReportUI
        ReportUI().create_report()
