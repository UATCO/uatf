from _pytest.config.argparsing import Parser


class Status:
    FAILED = 2  # AssertionError
    BROKEN = 3
    PASSED = 1
    FLAKY = 0
    SKIPPED = 4
    SKIPPED_JC = 5


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
