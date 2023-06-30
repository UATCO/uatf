import sys
import time
import inspect
from types import TracebackType
from contextlib import contextmanager

import attr
import pytest
import logging
from _pytest._code import ExceptionInfo, Traceback
from _pytest.capture import CaptureFixture
from _pytest.capture import FDCapture
from _pytest.capture import SysCapture
from _pytest.outcomes import OutcomeException
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from _pytest.runner import check_interactive_exception

from .config import Config
from .logfactory import LOG_FORMATTER


config = Config()

if sys.version_info[:2] < (3, 7):

    @contextmanager
    def nullcontext():
        yield

else:
    from contextlib import nullcontext


@attr.s
class SubTestContext:
    msg = attr.ib()
    kwargs = attr.ib()


def get_outer_traceback(tb, from_file):
    """Создает из фреймов недостающую структуру трейсбэка для отчета
    :param tb: текущий трейсбэк
    :param from_file: от какого файла нужно сформировать трейсбэк
    """
    frames_list = inspect.getouterframes(tb.tb_frame)
    index_start = 0
    index_end = len(frames_list) + 1
    for i, item in enumerate(frames_list):
        if item.frame == tb.tb_next.tb_frame:
            index_start = i + 1
        if item.filename == from_file:
            index_end = i + 1
    outer_traceback = frames_list[index_start:index_end]
    tb_next = tb
    for item in outer_traceback:
        tb_item = TracebackType(tb_next, item.frame, item.frame.f_lasti, item.lineno)
        tb_next = tb_item
    return tb_next


class LoggerInfoFilter(logging.Filter):

    def filter(self, record):
        return record.levelno == logging.INFO


def get_subtest_log(caplog):
    """Собираем логи для subtest
    """
    test_logs = caplog.get_records('call') or []
    test_logs = "".join([caplog.handler.format(item) for item in test_logs])
    return test_logs


@attr.s(init=False)
class SubTestReport(TestReport):
    context = attr.ib()

    @property
    def count_towards_summary(self):
        return not self.passed

    @property
    def head_line(self):
        _, _, domain = self.location
        return f"{domain} {self.sub_test_description()}"

    def sub_test_description(self):
        parts = []
        if isinstance(self.context.msg, str):
            parts.append(f"[{self.context.msg}]")
        if self.context.kwargs:
            params_desc = ", ".join(
                f"{k}={v!r}" for (k, v) in sorted(self.context.kwargs.items())
            )
            parts.append(f"({params_desc})")
        return " ".join(parts) or "(<subtest>)"

    def _to_json(self):
        data = super()._to_json()
        del data["context"]
        data["_report_type"] = "SubTestReport"
        data["_subtest.context"] = attr.asdict(self.context)
        return data

    @classmethod
    def _from_json(cls, reportdict):
        report = super()._from_json(reportdict)
        context_data = reportdict["_subtest.context"]
        report.context = SubTestContext(
            msg=context_data["msg"], kwargs=context_data["kwargs"]
        )
        return report

    @classmethod
    def _from_test_report(cls, test_report):
        return super()._from_json(test_report._to_json())


@pytest.fixture
def subtests(request, caplog):
    capmam = request.node.config.pluginmanager.get_plugin("capturemanager")
    if capmam is not None:
        suspend_capture_ctx = capmam.global_and_fixture_disabled
    else:
        suspend_capture_ctx = nullcontext
    caplog.handler.setFormatter(LOG_FORMATTER)
    caplog.handler.addFilter(LoggerInfoFilter())
    yield SubTests(request.node.ihook, suspend_capture_ctx, request, caplog)


@attr.s
class SubTests:
    ihook = attr.ib()
    suspend_capture_ctx = attr.ib()
    request = attr.ib()
    caplog = attr.ib()

    @property
    def item(self):
        return self.request.node

    @contextmanager
    def _capturing_output(self):
        option = self.request.config.getoption("capture", None)

        # capsys or capfd are active, subtest should not capture

        capman = self.request.config.pluginmanager.getplugin("capturemanager")
        capture_fixture_active = getattr(capman, "_capture_fixture", None)

        if option == "sys" and not capture_fixture_active:
            with ignore_pytest_private_warning():
                fixture = CaptureFixture(SysCapture, self.request)
        elif option == "fd" and not capture_fixture_active:
            with ignore_pytest_private_warning():
                fixture = CaptureFixture(FDCapture, self.request)
        else:
            fixture = None

        if fixture is not None:
            fixture._start()

        captured = Captured()
        try:
            yield captured
        finally:
            if fixture is not None:
                out, err = fixture.readouterr()
                fixture.close()
                captured.out = f'{get_subtest_log(self.caplog)}\n{out}'
                captured.err = err

    def _is_need_run(self, postfix, layout):
        restarted_tests = config.get('NODE_IDS', 'GENERAL')
        if restarted_tests:  # Если падает весь тест, то нужно запускать все subtests
            postfix = self._get_postfix(postfix, layout, add_counter=False)
            sub_test_name = self.item.nodeid + f'_{postfix}'
            if self.item.nodeid not in restarted_tests and sub_test_name not in restarted_tests:
                return False
        return True

    def _get_postfix(self, postfix=None, layout=False, add_counter=True):
        """Генерация имени подтеста"""

        if not postfix:
            subtests_count = getattr(self.request, '_subtest_count', 1)
            postfix = f'subtest_{str(subtests_count).zfill(3)}'
            if add_counter:
                setattr(self.request, '_subtest_count', subtests_count + 1)
        if layout:
            postfix = f'regression_{postfix}'
        return postfix

    def get_nodeid(self, postfix=None, layout=False, add_counter=True):
        """Генерация имени подтеста"""

        postfix = self._get_postfix(postfix, layout, add_counter)
        return f'{self.item.nodeid}_{postfix}'

    @contextmanager
    def _test(self, postfix=None, layout=False, teardown=False):
        start = time.time()
        precise_start = time.perf_counter()
        postfix = self._get_postfix(postfix, layout)

        exc_info = None

        with self._capturing_output() as captured:
            try:
                yield
            except (Exception, OutcomeException):
                exc_info = ExceptionInfo.from_current()
                if layout and len(exc_info.traceback) > 1:
                    outer_traceback = get_outer_traceback(exc_info.tb, from_file=str(self.item.fspath))
                    exc_info.traceback = Traceback(outer_traceback)

        if teardown:  # для teardown сохраняем только неуспешные в последний прогон

            if not exc_info:
                if not config.is_last_run \
                        or f'{self.item.nodeid}_{postfix}' not in config.get('NODE_IDS', 'GENERAL'):
                    return

        precise_stop = time.perf_counter()
        duration = precise_stop - precise_start
        stop = time.time()

        call_info = make_call_info(
            exc_info, start=start, stop=stop, duration=duration, when="call"
        )
        teardown_info = make_call_info(
            None, start=stop, stop=stop, duration=0, when="teardown"
        )

        origin_name = self.item.nodeid
        # TODO если писать [] то в pycharm видна иерархия, надо бы поправить
        try:  # тк выставляем на самом item, то надо потом его удалить
            self.item._nodeid += f'_{postfix}'
            setattr(self.item, 'subtest', True)
            report = self.ihook.pytest_runtest_makereport(item=self.item, call=call_info)
            teardown_report = self.ihook.pytest_runtest_makereport(item=self.item, call=teardown_info)
        finally:
            delattr(self.item, 'subtest')
            self.item._nodeid = origin_name

        sub_report = SubTestReport._from_test_report(report)
        sub_report.context = SubTestContext(postfix, dict())

        captured.update_report(sub_report)
        captured.update_report(teardown_report)

        # save to junit xml only last failed run
        if not exc_info or config.is_last_run or report.skipped:
            with self.suspend_capture_ctx():
                self.ihook.pytest_runtest_logreport(report=sub_report)
                self.ihook.pytest_runtest_logreport(report=teardown_report)

        if check_interactive_exception(call_info, sub_report):
            self.ihook.pytest_exception_interact(
                node=self.item, call=call_info, report=sub_report
            )

    def test(self):
        return self._test()


def make_call_info(exc_info, *, start, stop, duration, when):
    try:
        return CallInfo(
            None, exc_info, start=start, stop=stop, duration=duration, when=when
        )
    except TypeError:
        # support for pytest<6: didn't have a duration parameter then
        return CallInfo(None, exc_info, start=start, stop=stop, when=when, duration=stop - start)


@contextmanager
def ignore_pytest_private_warning():
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            "A private pytest class or function was used.",
            category=pytest.PytestDeprecationWarning,
        )
        yield


@attr.s
class Captured:
    out = attr.ib(default="", type=str)
    err = attr.ib(default="", type=str)

    def update_report(self, report):
        if self.out:
            report.sections.append(("Captured stdout call", self.out))
        if self.err:
            report.sections.append(("Captured stderr call", self.err))


def pytest_report_to_serializable(report):
    if isinstance(report, SubTestReport):
        return report._to_json()


def pytest_report_from_serializable(data):
    if data.get("_report_type") == "SubTestReport":
        return SubTestReport._from_json(data)


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report):
    if report.when != "call" or not isinstance(report, SubTestReport):
        return

    if hasattr(report, "wasxfail"):
        return None

    outcome = report.outcome
    if report.passed:
        return outcome, ",", "SUBPASS"
    elif report.skipped:
        return outcome, "-", "SUBSKIP"
    elif outcome == "failed":
        return outcome, "u", "SUBFAIL"
