import sqlite3


class DBBase:
    """Базис класс бд для результатов тестов"""

    def __init__(self):
        self._connect()

    def _connect(self):
        self.conn = sqlite3.connect('artifact/result.db', timeout=10)
        self.cursor = self.conn.cursor()

    def get_test_results(self) -> list:
        self.cursor.execute('SELECT * FROM test_results')
        return self.cursor.fetchall()
