import collections
from datetime import datetime
from typing import List, Union

from _pytest.config.argparsing import Parser
import pytest
from _pytest.main import Session
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from ..report.report_ui import ReportUI
from ..logfactory import log
from ..config import Config

Report = collections.namedtuple('Report', ('file_name', 'suite_name', 'test_name', 'status'))
REPORT_LIST: List[Report] = []


class Status:
    FAILED = 2  # AssertionError
    BROKEN = 3
    PASSED = 1
    FLAKY = 0
    SKIPPED = 4
    SKIPPED_JC = 5

def strip_doc(description):
    doc = description or ''
    if doc:
        doc = doc.replace(':return:', '').strip()
    return doc

def pytest_runtest_protocol(item, nextitem):
    """
    Run the test protocol.
    Note: when teardown fails, two reports are generated for the case, one for
    the test case and the other for the teardown error.
    """
    from _pytest.runner import runtestprotocol
    from ..config import Config

    config = Config()

    if config.is_last_run:
        item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
        reports = runtestprotocol(item, nextitem=nextitem, log=False)
        is_save = True
    else:  # чтобы в junit вообще ничего не попадало если тесты перезапускаем в сборке
        reports = runtestprotocol(item, nextitem=nextitem, log=False)
        is_save = all(not r.failed for r in reports)
        if is_save:
            item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)

    if is_save:
        for report in reports:  # 3 reports: setup, call, teardown
            item.ihook.pytest_runtest_logreport(report=report)
        item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)
    return True


def check_success_status(status):
    return status in (Status.SKIPPED, Status.PASSED, Status.FLAKY)


def pytest_addoption(parser: Parser):
    parser.addini('junit_logging', help='', type='string', default='system-out')
    parser.addini('junit_duration_report', help='', type='string', default='total')
    parser.addini('disable_test_id_escaping_and_forfeit_all_rights_to_community_support',
                  help='', type='bool', default=True)
    parser.addini('log_cli', help='', type='bool', default=True)
    parser.addini('log_cli_format', help='', type='string', default="%(asctime)s.%(msecs).03d %(message)s")
    parser.addini('log_cli_date_format', help='', type='string', default="%d.%m.%y %H:%M:%S")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: CallInfo[None]):
    outcome = yield
    report: TestReport = outcome.get_result()

    if report.when == 'call':
        log('Создаем отчет прохождения теста')
        cls = item.getparent(pytest.Class)
        suite = cls.obj
        driver = getattr(suite, "driver", None)

        start_time = datetime.fromtimestamp(call.start).strftime('%d.%m.%y %H:%M:%S')
        stop_time = datetime.fromtimestamp(call.stop).strftime('%d.%m.%y %H:%M:%S')
        report_ui = ReportUI(driver=driver, file_name=item.parent.parent.name, suite_name=item.parent.name,
                               test_name=item.name,
                               status=report.outcome, std_out=report.longreprtext, start_time=start_time,
                               stop_time=stop_time, description=strip_doc(item.obj.__doc__))
        if Config().get('CREATE_REPORT', 'GENERAL'):
            report_ui.save_test_result()
        report_ui.generate()
        mini_report = Report(item.parent.parent.name, item.parent.name, item.name, report.outcome)

        REPORT_LIST.append(mini_report)

def pytest_sessionfinish(session: Session, exitstatus: Union[int, pytest.ExitCode]):
    from ..cache import CacheResults
    cache = CacheResults()
    if REPORT_LIST:
        cache.save_test_result(REPORT_LIST)