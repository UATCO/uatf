import contextlib
import sqlite3
import os

from ..config import Config
from ..helper import get_artifact_path


config = Config()


class DB:
    """Класс для работы с sqlite3"""

    FAILED_TESTS_DB = 'failed_tests'

    def __init__(self, path=None) -> None:
        if path is None:
            self._path = os.path.join(get_artifact_path(), 'result.db')
        else:
            self._path = path
        self._connect()

    def _connect(self):
        self.conn = sqlite3.connect(self._path, timeout=10)
        self.cursor = self.conn.cursor()

    def setup(self, restart_failed=False):
        if not restart_failed:
            self._delete_db()

        cursor = self.conn.cursor()

        if not restart_failed:
            self.delete_failed_tests()
            # отдельная коллекция, чтобы можно было не трогать время прогона
            cursor.execute('drop table if exists exec_time')
            cursor.execute('CREATE TABLE exec_time (file text, time real)')

        cursor.execute('drop table if exists test_results')
        cursor.execute('CREATE TABLE test_results (file text, suite text, test text, status integer, '
                       'exec_time real, id_check text, '
                       'UNIQUE (file, suite, test) ON CONFLICT REPLACE)')

        cursor.execute('drop table if exists called_methods')
        cursor.execute('CREATE TABLE called_methods (method_name text, host text)')
        self.conn.commit()

    def _delete_db(self):
        self.conn.close()
        with contextlib.suppress(FileNotFoundError, PermissionError):
            os.remove(self._path)
        self._connect()

    def delete_failed_tests(self):
        self.cursor.execute(f'drop table if exists {self.FAILED_TESTS_DB}')
        self.cursor.execute(f'CREATE TABLE {self.FAILED_TESTS_DB} (file text, suite text, test text)')
        self.conn.commit()

    def save_test_result(self, file_name, suite, test, status):
        # не делает commit!
        self.cursor.execute("INSERT INTO test_results VALUES (?, ?, ?, ?)",
                            (file_name, suite, test, status))

    def get_test_results(self) -> list:
        self.cursor.execute('SELECT * FROM test_results')
        return self.cursor.fetchall()

    def get_counters(self):
        self.cursor.execute("SELECT status, count(*) FROM test_results GROUP BY status")
        return self.cursor.fetchall()

    def save_failed_tests(self, file_name, suite, test):
        # не делает commit!
        self.cursor.execute(f"INSERT INTO {self.FAILED_TESTS_DB} VALUES (?, ?, ?)", (file_name, suite, test))

    def get_exec_time_from_test_results(self):
        self.cursor.execute("SELECT file, sum(exec_time) FROM test_results GROUP BY file")
        return self.cursor.fetchall()

    def save_exec_time(self, file_name, exec_time):
        # не делает commit!
        # сохраняем в отдельной таблице тк результаты тестов стираются после перезапуска упавших
        self.cursor.execute("INSERT INTO exec_time VALUES (?, ?)", (file_name, exec_time))

    def get_exec_time_files(self) -> list:
        """Получение времени выполнения файлов с тестами"""

        self.cursor.execute('SELECT * from exec_time ORDER BY time DESC')
        return self.cursor.fetchall()

    def get_sum_exec_time(self):
        self.cursor.execute("SELECT SUM(time) FROM exec_time")
        return self.cursor.fetchone()[0]

    def get_failed_tests(self) -> list:
        self.cursor.execute(f'SELECT * from {self.FAILED_TESTS_DB}')
        return self.cursor.fetchall()

    def exists_failed_tests(self) -> int:
        """Наличие упавших тестов"""

        self.cursor.execute(f'SELECT COUNT(*) FROM {self.FAILED_TESTS_DB}')
        return bool(self.cursor.fetchone()[0])

    def save_bl_method(self, method_name, host):
        """Сохранить название вызванного метода и стенд в БД"""

        self.cursor.execute(f"""INSERT INTO called_methods
                             SELECT  "{method_name}", "{host}"
                             WHERE NOT EXISTS (SELECT 1 FROM  
                             called_methods WHERE method_name = "{method_name}" 
                             and host = "{host}")""")
        self.conn.commit()

    def get_bl_methods(self) -> list:
        self.cursor.execute('SELECT * from called_methods')
        return self.cursor.fetchall()

    def get_flaky_tests(self) -> list:
        self.cursor.execute('SELECT * FROM test_results WHERE status = 0')
        return self.cursor.fetchall()
