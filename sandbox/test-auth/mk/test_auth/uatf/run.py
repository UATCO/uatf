"""
Модуль для запуска тестовых наборов
"""
import os
import subprocess
import sys
from fnmatch import fnmatch
from typing import Dict, Any, List, Union

import pytest

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

    def _default_test_value(self) -> dict:

        return dict(tests=[], run=False, exec_time=0, process=None)

    def _collect_file_only(self, node_id: List[str]) -> Union[int, pytest.ExitCode]:
        """Проверка на то что в файле работают импорты"""

        cmd = node_id
        cmd.append('--collect-only')
        if self.options:
            cmd.extend(self.options)
        return pytest.main(cmd)

    def _check_file_list(self):
        """Удаляем файлы в которых нет тестов (не подходят под выборку),
        проверяем есть ли тесты для перезапуска"""

        bad_files = []
        empty_files = []

        for file, tests in self.test_files.items():
            exit_code = self._collect_file_only([file])
            # исключаем файлы из списка в которых нечего запускать
            if exit_code == pytest.ExitCode.NO_TESTS_COLLECTED:
                empty_files.append(file)
                continue

            # если при обработке файла возникли ошибки
            if exit_code != pytest.ExitCode.OK:
                bad_files.append(file)

        if bad_files:
            bad_files = '\n'.join(bad_files)
            raise ValueError(f'Не смогли запустить файлы: {bad_files}')

        if empty_files:  # удаляем пустые файлы их списка (во время итерации нельзя менять словарь)
            for key in empty_files:
                self.test_files.pop(key)

    def _generate_list_of_file_for_run(self) -> bool:
        """Создаем список файлов для запуска"""

        is_run = True

        tmp_cmd = self.config.get('FILES_TO_START', 'GENERAL')
        tmp_config = getattr(Config(), 'files_to_start', None)
        files_to_start = tmp_cmd or tmp_config
        if not files_to_start:
            log("Получаем список файлов в текущей директории")
            log("Запускаются только скрипты %s" % self.test_pattern)
            for file in self.tests:
                self.test_files[file] = self._default_test_value()
        else:
            log("Список файлов для запуска получен из командной строки / config.ini")
            for file in files_to_start:
                if not os.path.isfile(file):
                    raise FileNotFoundError('Не найден файл %s' % file)
                self.test_files[file] = self._default_test_value()
        if is_run:
            self._check_file_list()
        return is_run

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
        py_process: List['subprocess.Popen'] = []  # В списке хранятся запущенные процессы

        log("Запускаем тесты")
        while self._is_not_running_files() or len(py_process) > 0:
            if (int(self.streams_number) > len(py_process)) and self._is_not_running_files():
                test, value = next(filter(lambda v: not v[1]['run'], self.test_files.items()))
                process = self._run_test(test)
                self.test_files[test]['run'] = True
                py_process.append(process)
            else:
                # Ждем пока освободятся слоты, удаляем завершенные
                py_process = [proc for proc in py_process if proc.poll() is None]

    def run_tests(self):
        """Запускает тесты"""

        self._generate_list_of_file_for_run()
        self._basic_run()


def main(*args, **kwargs):
    print(args, kwargs)
    return RunTests().run_tests()
