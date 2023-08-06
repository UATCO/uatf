"""
Модуль для запуска тестовых наборов
"""
import os
import subprocess
import sys
from fnmatch import fnmatch
from typing import Dict, Any, List
from .logfactory import log

from uatf import Config


def get_pytest_run_command():
    """Получить команду для запуска pytest"""
    default_command = [
        sys.executable,
        '-m',
        'pytest',
        '--tb=native',
        '-p', 'no:cacheprovider',
        '-p', 'no:warnings',
        '--disable-warnings'
    ]
    return default_command


class RunTests:
    """Класс запускает тесты из текущей дирректории и мониторит их."""

    def __init__(self) -> None:
        """Получаем опции из конфига. Если их нет, то выставляем по умолчанию"""

        self.options = sys.argv[1:]
        self.test_files: Dict[str, Any] = {}
        self.config = Config()
        self.recursive_search = self.config.get('RECURSIVE_SEARCH', 'GENERAL')
        self.test_pattern = self.config.get('TEST_PATTERN', 'GENERAL')
        self.cwd = os.getcwd()
        self.tests = self._find_files()
        self._patch_env()
        self.streams_number = self.config.get('STREAMS_NUMBER', 'GENERAL')
        plugins = 'uatf.pytest_core.plugin,uatf.pytest_core.fixtures.subtests'
        os.environ["PYTEST_PLUGINS"] = f"{plugins}"

    def _find_files(self) -> List[str]:
        """Список тестов по паттерну"""

        files = []
        for root, _, dir_files in os.walk(self.cwd):
            for file in dir_files:
                if fnmatch(file, self.test_pattern):
                    files.append(os.path.relpath(os.path.join(root, file), self.cwd))
            if not self.recursive_search:
                break
        return files

    def _patch_env(self) -> None:
        """Задаем ENVIRONMENT для тестов"""

        if self.recursive_search:
            env = os.environ
            try:
                path = env['PYTHONPATH']
                new_path = os.path.pathsep.join((self.cwd, path))
            except KeyError:
                new_path = self.cwd
            env['PYTHONPATH'] = new_path

    def _is_not_running_files(self) -> bool:
        return any(not v['run'] for v in self.test_files.values())

    def _run_test(self, test: str, **kwargs: str) -> 'subprocess.Popen':
        """Запускает тестовый набор"""

        action = 'RUN'
        log(f"{action} FILE: %s" % test)
        commands = get_pytest_run_command()
        commands.append(test)

        for k, v in kwargs.items():
            commands.extend([f'--{k}', v])

        if self.options:
            commands.extend(self.options)

        log(commands)
        return subprocess.Popen(commands)

    def _basic_run(self) -> None:
        """Метод для запуска и мониторинга тестов"""

        log("Запускаем тесты")
        for file in self._find_files():
            self._run_test(file)

    def run_tests(self):
        """Запускает тесты"""

        self._basic_run()


def main(*args, **kwargs):
    print(args, kwargs)
    return RunTests().run_tests()
