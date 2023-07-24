import sqlite3


class ResultBD:
    """Модель бд для результатов тестов"""

    def __init__(self):
        self._connect()

    def _connect(self):
        self.conn = sqlite3.connect('result.db', timeout=10)
        self.cursor = self.conn.cursor()

    def setup(self):
        cursor = self.conn.cursor()

        cursor.execute('drop table if exists test_results')
        cursor.execute('CREATE TABLE test_results (file_name text, suite_name text, test_name text, status text, '
                       'start_time text, stop_time text,'
                       'std_out real, '
                       'UNIQUE (file_name, suite_name, test_name) ON CONFLICT REPLACE)')
        self.conn.commit()

    def save_test_result(self, file_name, suite_name, test_name, status, start_time, stop_time, std_out):
        self.cursor.execute("INSERT INTO test_results VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (file_name, suite_name, test_name, status, start_time,
                             stop_time, std_out))
        self.conn.commit()

    def get_test_results(self) -> list:
        self.cursor.execute('SELECT * FROM test_results')
        return self.cursor.fetchall()